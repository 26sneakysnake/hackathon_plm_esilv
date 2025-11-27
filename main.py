#!/usr/bin/env python3
"""
Manufacturing Operations Radar - Script Principal
Point d'entrée pour exécuter toutes les analyses
"""

import sys
from pathlib import Path
import argparse

# Ajouter src au path
sys.path.append(str(Path(__file__).parent / "src"))


def main():
    parser = argparse.ArgumentParser(
        description="Manufacturing Operations Radar - Analyse de la chaîne de production"
    )

    parser.add_argument(
        "--step",
        choices=["all", "data", "analysis", "viz", "optimize", "report", "dashboard"],
        default="all",
        help="Étape à exécuter (default: all)"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("🏭 MANUFACTURING OPERATIONS RADAR")
    print("=" * 80)
    print()

    if args.step in ["all", "data"]:
        print("📊 Étape 1/6: Génération de l'event log...")
        from data_processing.event_log_builder import EventLogBuilder
        from data_processing.data_loader import DataLoader

        loader = DataLoader()
        plm, mes, erp = loader.load_all_data()

        builder = EventLogBuilder(plm, mes, erp)
        event_log = builder.generate_event_log(num_cases=150)
        builder.save_event_log(event_log, "data/event_logs/manufacturing_event_log.csv")
        print("✅ Event log généré\n")

    if args.step in ["all", "analysis"]:
        print("📊 Étape 2/6: Analyses complètes...")
        from analysis.analyze_all import run_complete_analysis

        run_complete_analysis("data/event_logs/manufacturing_event_log.csv")
        print("✅ Analyses terminées\n")

    if args.step in ["all", "viz"]:
        print("📊 Étape 3/6: Génération des visualisations...")
        from visualization.generate_all_charts import generate_all_visualizations

        generate_all_visualizations(
            "data/event_logs/manufacturing_event_log.csv",
            "outputs/reports/kpis_summary.json"
        )
        print("✅ Visualisations générées\n")

    if args.step in ["all", "optimize"]:
        print("📊 Étape 4/6: Optimisation...")
        from optimization.run_optimization import run_optimization_analysis

        run_optimization_analysis("data/event_logs/manufacturing_event_log.csv")
        print("✅ Optimisation terminée\n")

    if args.step in ["all", "report"]:
        print("📊 Étape 5/6: Génération du rapport final...")
        from visualization.report_generator import generate_final_report

        generate_final_report()
        print("✅ Rapport généré\n")

    if args.step == "dashboard":
        print("📊 Lancement du dashboard Streamlit...")
        import os
        os.system("streamlit run src/visualization/dashboard.py")

    if args.step == "all":
        print("\n" + "=" * 80)
        print("✅ TOUTES LES ÉTAPES TERMINÉES")
        print("=" * 80)
        print("\n🎉 Le Manufacturing Operations Radar est prêt!")
        print("\n📊 Prochaines étapes:")
        print("  1. Consulter le rapport: outputs/reports/RAPPORT_FINAL.md")
        print("  2. Voir les visualisations: outputs/visualizations/")
        print("  3. Lancer le dashboard: python main.py --step dashboard")
        print()


if __name__ == "__main__":
    main()
