"""
Script principal pour l'optimisation
"""

import pandas as pd
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from optimization.optimizer import ManufacturingOptimizer


def run_optimization_analysis(event_log_path: str):
    """Exécute l'analyse d'optimisation complète"""

    print("=" * 80)
    print("🚀 MANUFACTURING OPTIMIZATION ENGINE")
    print("=" * 80)

    # Charger l'event log
    print("\n📂 Chargement des données...")
    event_log = pd.read_csv(event_log_path)
    print(f"✅ Event log chargé: {len(event_log)} événements")

    # Créer l'optimiseur
    optimizer = ManufacturingOptimizer(event_log)

    # Identifier les opportunités
    opportunities = optimizer.identify_optimization_opportunities()

    # Générer les recommandations
    recommendations = optimizer.generate_recommendations(opportunities)

    # Calculer l'impact
    impact = optimizer.calculate_optimization_impact(recommendations)

    # Sauvegarder les résultats
    output_dir = Path("outputs/recommendations")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Sauvegarder les recommandations
    with open(output_dir / "recommendations.json", "w") as f:
        json.dump(recommendations, f, indent=2, default=str)

    # Sauvegarder l'impact
    with open(output_dir / "optimization_impact.json", "w") as f:
        json.dump(impact, f, indent=2, default=str)

    # Créer un fichier markdown avec les recommandations
    with open(output_dir / "recommendations.md", "w") as f:
        f.write("# 📋 RECOMMANDATIONS D'OPTIMISATION\n\n")
        f.write(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        f.write("## 🎯 Top 3 Actions Prioritaires\n\n")

        for i, rec in enumerate(recommendations[:3], 1):
            f.write(f"### Action #{i}: {rec['action']}\n\n")
            f.write(f"**Priorité**: {rec['priority']}\n\n")
            f.write(f"**Problème identifié**: {rec['problem']}\n\n")
            f.write(f"**Détails**: {rec['details']}\n\n")
            f.write(f"**Impact estimé**:\n")
            f.write(f"- ΔWIP: -{rec['estimated_wip_reduction_pct']:.1f}%\n")
            f.write(f"- ΔLead Time: -{rec['estimated_leadtime_reduction_pct']:.1f}%\n")
            f.write(f"- Coût: {rec['estimated_cost_euros']:,.0f}€\n")
            f.write(f"- ROI: {rec['roi']:.1f}x\n")
            f.write(f"- Payback: {rec['payback_months']:.0f} mois\n")
            f.write(f"- Durée d'implémentation: {rec['implementation_time']}\n\n")
            f.write("---\n\n")

        f.write("## 📊 Impact Global (Top 3)\n\n")
        f.write(f"- **ΔWIP total**: -{impact['delta']['wip_reduction_pct']:.1f}%\n")
        f.write(f"- **ΔLead Time total**: -{impact['delta']['leadtime_reduction_pct']:.1f}%\n")
        f.write(f"- **Augmentation débit**: +{impact['delta']['throughput_increase_pct']:.1f}%\n")
        f.write(f"- **Investissement total**: {impact['delta']['total_investment_euros']:,.0f}€\n")
        f.write(f"- **ROI global**: {impact['roi_global']:.1f}x\n\n")

    print(f"\n💾 Résultats sauvegardés dans: {output_dir}")

    print("\n" + "=" * 80)
    print("✅ OPTIMISATION TERMINÉE")
    print("=" * 80)

    return recommendations, impact


if __name__ == "__main__":
    event_log_path = "data/event_logs/manufacturing_event_log.csv"
    recommendations, impact = run_optimization_analysis(event_log_path)
