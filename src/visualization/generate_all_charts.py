"""
Script pour générer toutes les visualisations
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from visualization.charts import ChartsGenerator
from analysis.bottleneck_detector import BottleneckDetector
import json


def generate_all_visualizations(event_log_path: str, kpis_path: str):
    """Génère toutes les visualisations et les sauvegarde"""

    print("=" * 80)
    print("📊 GÉNÉRATION DES VISUALISATIONS")
    print("=" * 80)

    # Charger les données
    print("\n📂 Chargement des données...")
    event_log = pd.read_csv(event_log_path)

    with open(kpis_path, 'r') as f:
        kpis = json.load(f)

    print(f"✅ Données chargées")

    # Créer le générateur
    charts_gen = ChartsGenerator(event_log)

    # Dossier de sortie
    output_dir = Path("outputs/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n🎨 Génération des graphiques...")

    # 1. Process Map
    print("  1/9 - Process Map...")
    fig_process = charts_gen.create_process_map()
    fig_process.write_html(output_dir / "process_map.html")
    fig_process.write_image(output_dir / "process_map.png") if has_kaleido() else None

    # 2. WIP Heatmap
    print("  2/9 - WIP Heatmap...")
    fig_wip = charts_gen.create_wip_heatmap(time_interval='2H')
    fig_wip.write_html(output_dir / "wip_heatmap.html")

    # 3. Pareto Chart
    print("  3/9 - Pareto Chart...")
    bd = BottleneckDetector(event_log)
    bottlenecks = bd.detect_bottlenecks_by_wait_time()
    fig_pareto = charts_gen.create_pareto_chart(bottlenecks)
    fig_pareto.write_html(output_dir / "pareto_bottlenecks.html")

    # 4. Gantt Chart
    print("  4/9 - Gantt Chart...")
    fig_gantt = charts_gen.create_gantt_chart(num_cases=20)
    fig_gantt.write_html(output_dir / "gantt_chart.html")

    # 5. Cycle Time Boxplot
    print("  5/9 - Cycle Time Boxplot...")
    fig_boxplot = charts_gen.create_cycle_time_boxplot()
    fig_boxplot.write_html(output_dir / "cycle_time_boxplot.html")

    # 6. Throughput Evolution
    print("  6/9 - Throughput Evolution...")
    fig_throughput = charts_gen.create_throughput_evolution(time_interval='2H')
    fig_throughput.write_html(output_dir / "throughput_evolution.html")

    # 7. Rework Sankey
    print("  7/9 - Rework Sankey...")
    fig_sankey = charts_gen.create_rework_sankey()
    fig_sankey.write_html(output_dir / "rework_sankey.html")

    # 8. KPI Dashboard
    print("  8/9 - KPI Dashboard...")
    fig_kpi = charts_gen.create_kpi_dashboard(kpis)
    fig_kpi.write_html(output_dir / "kpi_dashboard.html")

    print("\n✅ Toutes les visualisations ont été générées!")
    print(f"📁 Emplacement: {output_dir.absolute()}")

    # Lister les fichiers créés
    print("\n📋 Fichiers créés:")
    for file in sorted(output_dir.glob("*.html")):
        print(f"  • {file.name}")

    return output_dir


def has_kaleido():
    """Vérifie si kaleido est installé pour l'export PNG"""
    try:
        import kaleido
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    event_log_path = "data/event_logs/manufacturing_event_log.csv"
    kpis_path = "outputs/reports/kpis_summary.json"

    output_dir = generate_all_visualizations(event_log_path, kpis_path)

    print("\n" + "=" * 80)
    print("✅ GÉNÉRATION TERMINÉE")
    print("=" * 80)
    print(f"\n💡 Ouvrez les fichiers HTML dans votre navigateur pour voir les visualisations interactives!")
