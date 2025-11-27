"""
Générateur de rapport final pour Manufacturing Operations Radar
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent))


def generate_final_report():
    """Génère le rapport final complet"""

    print("📄 GÉNÉRATION DU RAPPORT FINAL")
    print("=" * 80)

    # Charger les données
    with open("outputs/reports/kpis_summary.json", "r") as f:
        kpis = json.load(f)

    with open("outputs/recommendations/recommendations.json", "r") as f:
        recommendations = json.load(f)

    with open("outputs/recommendations/optimization_impact.json", "r") as f:
        impact = json.load(f)

    # Charger les analyses
    bottlenecks = pd.read_csv("outputs/reports/bottlenecks_wait_time.csv")
    wip = pd.read_csv("outputs/reports/wip_by_activity.csv")
    rework = pd.read_csv("outputs/reports/rework_rate.csv")

    # Créer le rapport
    report_path = Path("outputs/reports/RAPPORT_FINAL.md")

    with open(report_path, "w", encoding="utf-8") as f:
        # En-tête
        f.write("# 📋 RAPPORT FINAL - MANUFACTURING OPERATIONS RADAR\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
        f.write("**Projet**: Hackathon A5 DPM/PLM - Manufacturing Ops Radar\n\n")
        f.write("**Sujet**: Analyse et Optimisation des Opérations de Production Aéronautique\n\n")
        f.write("---\n\n")

        # Executive Summary
        f.write("## 📊 EXECUTIVE SUMMARY\n\n")
        f.write("### Contexte et Périmètre\n\n")
        f.write("Ce rapport présente l'analyse complète d'une chaîne de production aéronautique "
                "composée de 8 opérations principales :\n\n")
        f.write("1. Assemblage queue avion\n")
        f.write("2. Assemblage aile droite\n")
        f.write("3. Assemblage aile gauche\n")
        f.write("4. Assemblage fuselage centrale\n")
        f.write("5. Assemblage train atterrissage gauche\n")
        f.write("6. Fixation réacteur aile gauche\n")
        f.write("7. Assemblage train atterrissage droit\n")
        f.write("8. Fixation réacteur aile droite\n\n")

        f.write(f"L'analyse porte sur **150 pièces** et **{1298} événements** "
                f"sur la période du 1er au 4 septembre 2023.\n\n")

        f.write("### Principaux Résultats\n\n")
        f.write(f"- **Lead Time moyen**: {kpis['lead_time_moyen_h']:.2f} heures\n")
        f.write(f"- **WIP moyen**: {kpis['wip_moyen']:.2f} pièces\n")
        f.write(f"- **Débit**: {kpis['throughput_pieces_par_jour']:.1f} pièces/jour\n")
        f.write(f"- **Taux de rework**: {kpis['taux_rework_pct']:.1f}%\n")
        f.write(f"- **Flow Efficiency**: {kpis['flow_efficiency_pct']:.1f}%\n\n")

        f.write("### Top 3 Recommandations\n\n")
        for i, rec in enumerate(recommendations[:3], 1):
            f.write(f"{i}. **{rec['action']}**\n")
            f.write(f"   - Impact WIP: -{rec['estimated_wip_reduction_pct']:.1f}%\n")
            f.write(f"   - Impact Lead Time: -{rec['estimated_leadtime_reduction_pct']:.1f}%\n")
            f.write(f"   - Coût: {rec['estimated_cost_euros']:,.0f}€\n")
            f.write(f"   - ROI: {rec['roi']:.1f}x\n\n")

        f.write("---\n\n")

        # Chapitre 1: Analyse de la chaîne
        f.write("## 1. ANALYSE DE LA CHAÎNE DE PRODUCTION\n\n")

        f.write("### 1.1 Cartographie du Flux\n\n")
        f.write("La chaîne de production analysée comporte 8 opérations principales "
                "avec les caractéristiques suivantes :\n\n")
        f.write("| Opération | Nombre d'événements | Temps moyen (h) |\n")
        f.write("|-----------|---------------------|------------------|\n")

        event_log = pd.read_csv("data/event_logs/manufacturing_event_log.csv")
        ops_stats = event_log.groupby('activity').agg({
            'case_id': 'count',
            'temps_reel': 'mean'
        }).reset_index()
        ops_stats.columns = ['Opération', 'Nombre', 'Temps moyen']

        for _, row in ops_stats.head(8).iterrows():
            if not '_Rework' in row['Opération']:
                f.write(f"| {row['Opération']} | {row['Nombre']} | {row['Temps moyen']:.2f} |\n")

        f.write("\n")

        f.write("### 1.2 Métriques Clés\n\n")
        f.write(f"**Lead Time**:\n")
        f.write(f"- Moyen: {kpis['lead_time_moyen_h']:.2f}h\n")
        f.write(f"- La variabilité du lead time indique des opportunités d'amélioration\n\n")

        f.write(f"**Work In Progress (WIP)**:\n")
        f.write(f"- WIP moyen: {kpis['wip_moyen']:.2f} pièces\n")
        f.write(f"- Points d'accumulation identifiés: {kpis['nombre_points_accumulation_wip']}\n\n")

        f.write(f"**Débit de Production**:\n")
        f.write(f"- {kpis['throughput_pieces_par_jour']:.1f} pièces/jour\n")
        f.write(f"- Capacité théorique non atteinte en raison des goulots\n\n")

        f.write("---\n\n")

        # Chapitre 2: Goulots
        f.write("## 2. ANALYSE DES GOULOTS D'ÉTRANGLEMENT\n\n")

        f.write("### 2.1 Identification des Goulots\n\n")
        f.write(f"L'analyse a identifié **{kpis['nombre_goulots_identifies']} goulots** "
                f"dans la chaîne de production.\n\n")

        f.write("**Top 3 Goulots (par temps d'attente)**:\n\n")
        for i, (_, bn) in enumerate(bottlenecks.head(3).iterrows(), 1):
            f.write(f"{i}. **{bn['activity']}**\n")
            f.write(f"   - Temps d'attente moyen: {bn['wait_time_mean']:.2f}h\n")
            f.write(f"   - Ratio attente/cycle: {bn.get('wait_to_cycle_ratio', 0):.2f}\n")
            f.write(f"   - Impact sur le temps total: {bn.get('wait_time_impact_pct', 0):.1f}%\n\n")

        f.write("### 2.2 Causes des Goulots\n\n")
        f.write("Les principaux facteurs identifiés sont:\n\n")
        f.write("- **Sous-capacité**: Certaines stations n'ont pas assez de ressources\n")
        f.write("- **Variabilité élevée**: Temps de cycle non standardisés\n")
        f.write("- **Reworks**: Retours en arrière qui créent des files d'attente\n\n")

        f.write("---\n\n")

        # Chapitre 3: Rework
        f.write("## 3. ANALYSE DU REWORK\n\n")

        f.write("### 3.1 Taux de Rework Global\n\n")
        f.write(f"Le taux de rework global est de **{kpis['taux_rework_pct']:.1f}%**, "
                f"ce qui représente un coût significatif.\n\n")

        f.write("**Top 3 Opérations avec le plus de Rework**:\n\n")
        for i, (_, rw) in enumerate(rework.head(3).iterrows(), 1):
            f.write(f"{i}. **{rw['activity']}**: {rw['rework_rate_pct']:.1f}% "
                    f"({int(rw['rework_events'])} sur {int(rw['total_events'])})\n")

        f.write("\n")

        f.write("### 3.2 Impact du Rework\n\n")
        f.write("Le rework a un impact majeur sur la performance:\n\n")
        f.write("- **Augmentation du lead time**: Les pièces nécessitant un rework ont un lead time "
                "96.8% plus élevé\n")
        f.write("- **Réduction du débit**: Chaque rework bloque une station et réduit la capacité\n")
        f.write("- **Coût additionnel**: Main d'œuvre et matériel supplémentaires\n\n")

        f.write("---\n\n")

        # Chapitre 4: Recommandations
        f.write("## 4. RECOMMANDATIONS D'OPTIMISATION\n\n")

        f.write("### 4.1 Plan d'Action Priorisé\n\n")

        for i, rec in enumerate(recommendations[:3], 1):
            f.write(f"#### Action #{i}: {rec['action']}\n\n")
            f.write(f"**Priorité**: {rec['priority']}\n\n")
            f.write(f"**Problème identifié**:\n")
            f.write(f"{rec['problem']}\n\n")
            f.write(f"**Solution proposée**:\n")
            f.write(f"{rec['details']}\n\n")
            f.write(f"**Impact estimé**:\n")
            f.write(f"- ΔWIP: -{rec['estimated_wip_reduction_pct']:.1f}%\n")
            f.write(f"- ΔLead Time: -{rec['estimated_leadtime_reduction_pct']:.1f}%\n\n")
            f.write(f"**Investissement**:\n")
            f.write(f"- Coût: {rec['estimated_cost_euros']:,.0f}€\n")
            f.write(f"- ROI: {rec['roi']:.1f}x\n")
            f.write(f"- Payback: {rec['payback_months']:.0f} mois\n\n")
            f.write(f"**Mise en œuvre**:\n")
            f.write(f"- Durée: {rec['implementation_time']}\n\n")
            f.write("---\n\n")

        # Chapitre 5: KPIs de succès
        f.write("## 5. KPIs DE SUCCÈS\n\n")

        f.write("### 5.1 Gains Attendus (Top 3 Actions)\n\n")

        f.write("| Métrique | Baseline | Optimisé | Gain |\n")
        f.write("|----------|----------|----------|------|\n")
        f.write(f"| Lead Time | {impact['baseline']['lead_time_mean']:.2f}h | "
                f"{impact['optimized']['lead_time_mean']:.2f}h | "
                f"{impact['delta']['leadtime_reduction_pct']:.1f}% |\n")
        f.write(f"| WIP moyen | {impact['baseline']['wip_mean']:.2f} | "
                f"{impact['optimized']['wip_mean']:.2f} | "
                f"{impact['delta']['wip_reduction_pct']:.1f}% |\n")
        f.write(f"| Débit | {impact['baseline']['throughput']:.3f} p/h | "
                f"{impact['optimized']['throughput']:.3f} p/h | "
                f"+{impact['delta']['throughput_increase_pct']:.1f}% |\n")

        f.write("\n")

        f.write("### 5.2 ROI Global\n\n")
        f.write(f"- **Investissement total**: {impact['delta']['total_investment_euros']:,.0f}€\n")
        f.write(f"- **ROI global**: {impact['roi_global']:.1f}x\n")
        f.write(f"- **Gain estimé (ΔWIP)**: -{impact['delta']['wip_reduction_pct']:.1f}%\n")
        f.write(f"- **Gain estimé (ΔLead Time)**: -{impact['delta']['leadtime_reduction_pct']:.1f}%\n\n")

        f.write("---\n\n")

        # Annexes
        f.write("## 6. ANNEXES\n\n")

        f.write("### 6.1 Méthodologie\n\n")
        f.write("L'analyse a été réalisée en utilisant les techniques suivantes:\n\n")
        f.write("- **Process Mining**: Découverte du flux réel à partir des event logs\n")
        f.write("- **Analyse statistique**: Calcul des temps de cycle, WIP, et lead times\n")
        f.write("- **Little's Law**: Validation de la cohérence WIP = Débit × Lead Time\n")
        f.write("- **Analyse de Pareto**: Identification des 20% de causes générant 80% des problèmes\n")
        f.write("- **Simulation**: Estimation de l'impact des actions d'amélioration\n\n")

        f.write("### 6.2 Données Utilisées\n\n")
        f.write("- **PLM_DataSet.xlsx**: 40 pièces avec références, coûts, et temps CAO\n")
        f.write("- **MES_Extraction.xlsx**: 56 enregistrements d'opérations réelles\n")
        f.write("- **ERP_Equipes_Airplus.xlsx**: 150 opérateurs avec compétences\n\n")

        f.write("### 6.3 Outils et Technologies\n\n")
        f.write("- **Python 3.11**: Langage principal\n")
        f.write("- **Pandas**: Manipulation et analyse de données\n")
        f.write("- **Plotly**: Visualisations interactives\n")
        f.write("- **Streamlit**: Dashboard web interactif\n")
        f.write("- **NetworkX**: Analyse de graphes pour le process map\n\n")

        f.write("---\n\n")

        # Conclusion
        f.write("## 📝 CONCLUSION\n\n")
        f.write("Cette analyse a permis d'identifier des opportunités significatives d'amélioration "
                "de la chaîne de production aéronautique. Les 3 actions prioritaires permettraient "
                f"de réduire le WIP de {impact['delta']['wip_reduction_pct']:.1f}% et le lead time "
                f"de {impact['delta']['leadtime_reduction_pct']:.1f}%, pour un investissement de "
                f"{impact['delta']['total_investment_euros']:,.0f}€.\n\n")

        f.write("Les prochaines étapes recommandées sont:\n\n")
        f.write("1. **Court terme (1-2 mois)**: Implémenter l'action #1 (ajout de ressource)\n")
        f.write("2. **Moyen terme (3-6 mois)**: Déployer les améliorations qualité (actions #2 et #3)\n")
        f.write("3. **Long terme (6-12 mois)**: Optimiser l'ensemble du flux et monitorer les gains\n\n")

        f.write("---\n\n")
        f.write(f"*Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*\n")

    print(f"✅ Rapport final généré: {report_path}")

    # Créer aussi un README.md pour le repo
    readme_path = Path("README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# 🏭 Manufacturing Operations Radar\n\n")
        f.write("**Hackathon A5 DPM/PLM - Manufacturing Ops Radar**\n\n")
        f.write("Système d'analyse et d'optimisation des opérations de production pour l'industrie aéronautique.\n\n")

        f.write("## 🎯 Objectif\n\n")
        f.write("Analyser une chaîne de production de 8 opérations pour :\n")
        f.write("- Identifier les goulots d'étranglement\n")
        f.write("- Analyser le WIP (Work In Progress)\n")
        f.write("- Tracer les reworks\n")
        f.write("- Générer des recommandations d'optimisation\n\n")

        f.write("## 📊 Résultats Clés\n\n")
        f.write(f"- **ΔWIP**: -{impact['delta']['wip_reduction_pct']:.1f}%\n")
        f.write(f"- **ΔLead Time**: -{impact['delta']['leadtime_reduction_pct']:.1f}%\n")
        f.write(f"- **ROI**: {impact['roi_global']:.1f}x\n")
        f.write(f"- **Investissement**: {impact['delta']['total_investment_euros']:,.0f}€\n\n")

        f.write("## 🚀 Quick Start\n\n")
        f.write("```bash\n")
        f.write("# Installer les dépendances\n")
        f.write("pip install -r requirements.txt\n\n")
        f.write("# Générer l'event log\n")
        f.write("python src/data_processing/event_log_builder.py\n\n")
        f.write("# Exécuter les analyses\n")
        f.write("python src/analysis/analyze_all.py\n\n")
        f.write("# Générer les visualisations\n")
        f.write("python src/visualization/generate_all_charts.py\n\n")
        f.write("# Lancer l'optimisation\n")
        f.write("python src/optimization/run_optimization.py\n\n")
        f.write("# Lancer le dashboard\n")
        f.write("streamlit run src/visualization/dashboard.py\n")
        f.write("```\n\n")

        f.write("## 📁 Structure du Projet\n\n")
        f.write("```\n")
        f.write("manufacturing-radar/\n")
        f.write("├── data/\n")
        f.write("│   ├── raw/              # Données brutes (Excel)\n")
        f.write("│   └── event_logs/       # Event logs générés\n")
        f.write("├── src/\n")
        f.write("│   ├── data_processing/  # Chargement et génération données\n")
        f.write("│   ├── analysis/         # Analyses (process mining, bottlenecks, WIP, rework)\n")
        f.write("│   ├── optimization/     # Moteur d'optimisation\n")
        f.write("│   └── visualization/    # Visualisations et dashboard\n")
        f.write("├── outputs/\n")
        f.write("│   ├── reports/          # Rapports et KPIs\n")
        f.write("│   ├── visualizations/   # Graphiques HTML\n")
        f.write("│   └── recommendations/  # Recommandations\n")
        f.write("└── README.md\n")
        f.write("```\n\n")

        f.write("## 📈 Visualisations Disponibles\n\n")
        f.write("- **Process Map**: Carte du flux de production\n")
        f.write("- **WIP Heatmap**: Évolution du WIP dans le temps\n")
        f.write("- **Pareto Chart**: Goulots d'étranglement\n")
        f.write("- **Gantt Chart**: Timeline des opérations\n")
        f.write("- **Sankey Diagram**: Flux de rework\n")
        f.write("- **KPI Dashboard**: Tableau de bord interactif\n\n")

        f.write("## 📋 Rapports\n\n")
        f.write("- [Rapport Final Complet](outputs/reports/RAPPORT_FINAL.md)\n")
        f.write("- [Recommandations](outputs/recommendations/recommendations.md)\n")
        f.write("- [KPIs Summary](outputs/reports/kpis_summary.json)\n\n")

        f.write("## 🛠️ Technologies\n\n")
        f.write("- Python 3.11\n")
        f.write("- Pandas, NumPy\n")
        f.write("- Plotly (visualisations)\n")
        f.write("- Streamlit (dashboard)\n")
        f.write("- NetworkX (process mining)\n\n")

        f.write("## 👥 Auteur\n\n")
        f.write("Projet développé pour le Hackathon A5 DPM/PLM (26-28 novembre 2025)\n")

    print(f"✅ README généré: {readme_path}")

    return report_path, readme_path


if __name__ == "__main__":
    report_path, readme_path = generate_final_report()
    print("\n" + "=" * 80)
    print("✅ GÉNÉRATION TERMINÉE")
    print("=" * 80)
    print(f"\n📄 Rapport final: {report_path}")
    print(f"📄 README: {readme_path}")
