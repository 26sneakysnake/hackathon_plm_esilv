"""
Script principal pour exécuter toutes les analyses
"""

import pandas as pd
import json
from pathlib import Path
import sys

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from analysis.process_mining import ProcessMiner
from analysis.bottleneck_detector import BottleneckDetector
from analysis.wip_analyzer import WIPAnalyzer
from analysis.rework_tracker import ReworkTracker


def run_complete_analysis(event_log_path: str):
    """Exécute toutes les analyses et génère un rapport"""

    print("=" * 80)
    print("🚀 MANUFACTURING OPERATIONS RADAR - ANALYSE COMPLÈTE")
    print("=" * 80)

    # Charger l'event log
    print("\n📂 Chargement de l'event log...")
    event_log = pd.read_csv(event_log_path)
    print(f"✅ Event log chargé: {len(event_log)} événements, {event_log['case_id'].nunique()} pièces")

    # ====================
    # 1. PROCESS MINING
    # ====================
    print("\n" + "=" * 80)
    print("📊 1. PROCESS MINING")
    print("=" * 80)

    pm = ProcessMiner(event_log)

    overview = pm.get_process_overview()
    print(f"\n🔍 Vue d'ensemble:")
    print(f"  • Nombre de pièces: {overview['nombre_pieces']}")
    print(f"  • Nombre d'opérations: {overview['nombre_operations']}")
    print(f"  • Lead time moyen: {overview['lead_time_moyen']:.2f}h (±{overview['lead_time_std']:.2f}h)")
    print(f"  • Lead time min/max: {overview['lead_time_min']:.2f}h / {overview['lead_time_max']:.2f}h")
    print(f"  • Taux de rework: {overview['taux_rework']:.1f}%")
    print(f"  • Débit: {overview['throughput']:.3f} pièces/heure")
    print(f"  • Période: {overview['periode_debut']} → {overview['periode_fin']}")

    print(f"\n📊 Temps de cycle par opération:")
    cycle_times = pm.calculate_cycle_times()
    print(cycle_times[['Temps Réel Moyen (h)', 'Temps Attente Moyen (h)', 'Nombre Événements']].head(10))

    # ====================
    # 2. BOTTLENECK DETECTION
    # ====================
    print("\n" + "=" * 80)
    print("🚨 2. DÉTECTION DES GOULOTS D'ÉTRANGLEMENT")
    print("=" * 80)

    bd = BottleneckDetector(event_log)

    print("\n🔴 Goulots par temps d'attente:")
    wait_bottlenecks = bd.detect_bottlenecks_by_wait_time()
    print(wait_bottlenecks[['activity', 'wait_time_mean', 'cycle_time_mean', 'wait_to_cycle_ratio', 'is_bottleneck']].head(5))

    print("\n🔴 Goulots par WIP:")
    wip_bottlenecks = bd.detect_bottlenecks_by_wip()
    print(wip_bottlenecks[['activity', 'wip_mean', 'wip_max', 'is_bottleneck']].head(5))

    print("\n🔴 Impact sur le lead time:")
    impact = bd.calculate_bottleneck_impact()
    print(impact[['activity', 'total_time', 'leadtime_contribution_pct']].head(5))

    # ====================
    # 3. WIP ANALYSIS
    # ====================
    print("\n" + "=" * 80)
    print("📦 3. ANALYSE DU WIP (WORK IN PROGRESS)")
    print("=" * 80)

    wip = WIPAnalyzer(event_log)

    wip_by_activity = wip.calculate_wip_by_activity()
    print("\n📊 WIP par activité:")
    print(wip_by_activity[['activity', 'wip_mean', 'wip_max', 'wip_std']].head(8))

    inventory = wip.calculate_inventory_profile()
    print(f"\n📦 Profil d'inventaire (Little's Law):")
    print(f"  • WIP théorique: {inventory['theoretical_wip']:.2f} pièces")
    print(f"  • WIP réel moyen: {inventory['actual_wip']:.2f} pièces")
    print(f"  • Efficacité WIP: {inventory['wip_efficiency']:.1f}%")

    flow_eff = wip.calculate_flow_efficiency()
    print(f"\n⚡ Efficacité du flux:")
    print(f"  • Flow Efficiency moyenne: {flow_eff['avg_flow_efficiency']:.1f}%")
    print(f"  • Temps à valeur ajoutée: {flow_eff['avg_value_adding_time']:.2f}h")
    print(f"  • Temps de gaspillage: {flow_eff['avg_waste_time']:.2f}h")

    accumulation = wip.identify_wip_accumulation_points()
    print(f"\n🚨 Points d'accumulation de WIP ({len(accumulation)} trouvés):")
    if len(accumulation) > 0:
        print(accumulation[['activity', 'wip_mean', 'wip_excess', 'wip_excess_pct']].head(5))

    # ====================
    # 4. REWORK ANALYSIS
    # ====================
    print("\n" + "=" * 80)
    print("🔄 4. ANALYSE DES REWORKS")
    print("=" * 80)

    rt = ReworkTracker(event_log)

    rework_rate = rt.calculate_rework_rate_by_activity()
    print("\n📊 Taux de rework par activité:")
    print(rework_rate[['activity', 'total_events', 'rework_events', 'rework_rate_pct']].head(8))

    rework_cost = rt.calculate_rework_cost()
    print(f"\n💰 Coût des reworks:")
    if len(rework_cost) > 0:
        print(rework_cost[['activity', 'total_cost_euros', 'rework_count', 'total_time_hours']].head(5))
        print(f"\n  💸 Coût total des reworks: {rework_cost['total_cost_euros'].sum():.2f}€")

    leadtime_impact = rt.calculate_rework_impact_on_leadtime()
    print(f"\n⏱️ Impact sur le lead time:")
    print(f"  • Lead time avec rework: {leadtime_impact['avg_leadtime_with_rework']:.2f}h")
    print(f"  • Lead time sans rework: {leadtime_impact['avg_leadtime_without_rework']:.2f}h")
    print(f"  • Augmentation: +{leadtime_impact['leadtime_increase_pct']:.1f}%")

    fpy = rt.calculate_first_pass_yield()
    print(f"\n✅ First Pass Yield (FPY):")
    print(fpy[['activity', 'ok_count', 'total_count', 'fpy_pct']].head(8))

    # ====================
    # 5. RÉSUMÉ EXÉCUTIF
    # ====================
    print("\n" + "=" * 80)
    print("📋 5. RÉSUMÉ EXÉCUTIF - KPIs CLÉS")
    print("=" * 80)

    kpis = {
        'lead_time_moyen_h': round(overview['lead_time_moyen'], 2),
        'wip_moyen': round(inventory['actual_wip'], 2),
        'throughput_pieces_par_jour': round(overview['throughput'] * 24, 2),
        'taux_rework_pct': round(overview['taux_rework'], 1),
        'flow_efficiency_pct': round(flow_eff['avg_flow_efficiency'], 1),
        'cout_rework_total_euros': round(rework_cost['total_cost_euros'].sum(), 2) if len(rework_cost) > 0 else 0,
        'nombre_goulots_identifies': int(wait_bottlenecks['is_bottleneck'].sum()),
        'nombre_points_accumulation_wip': len(accumulation)
    }

    print("\n🎯 KPIs Globaux:")
    for key, value in kpis.items():
        print(f"  • {key}: {value}")

    # Sauvegarder les résultats
    output_dir = Path("outputs/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Sauvegarder les KPIs
    with open(output_dir / "kpis_summary.json", "w") as f:
        json.dump(kpis, f, indent=2)

    # Sauvegarder les analyses détaillées
    wait_bottlenecks.to_csv(output_dir / "bottlenecks_wait_time.csv", index=False)
    wip_by_activity.to_csv(output_dir / "wip_by_activity.csv", index=False)
    rework_rate.to_csv(output_dir / "rework_rate.csv", index=False)
    cycle_times.to_csv(output_dir / "cycle_times.csv")

    print(f"\n💾 Résultats sauvegardés dans: {output_dir}")

    print("\n" + "=" * 80)
    print("✅ ANALYSE COMPLÈTE TERMINÉE")
    print("=" * 80)

    return {
        'overview': overview,
        'wait_bottlenecks': wait_bottlenecks,
        'wip_by_activity': wip_by_activity,
        'rework_rate': rework_rate,
        'kpis': kpis
    }


if __name__ == "__main__":
    event_log_path = "data/event_logs/manufacturing_event_log.csv"
    results = run_complete_analysis(event_log_path)
