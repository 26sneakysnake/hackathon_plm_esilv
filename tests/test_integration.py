"""
Tests d'intégration complets
Vérifie que le workflow end-to-end fonctionne correctement
"""

import pytest
import pandas as pd
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from data_processing.data_loader import DataLoader
from data_processing.event_log_builder import EventLogBuilder
from analysis.process_mining import ProcessMiner
from analysis.bottleneck_detector import BottleneckDetector
from analysis.wip_analyzer import WIPAnalyzer
from analysis.rework_tracker import ReworkTracker
from optimization.optimizer import ManufacturingOptimizer


class TestIntegration:
    """Tests d'intégration end-to-end"""

    def test_complete_workflow(self):
        """Test du workflow complet de bout en bout"""

        # 1. Chargement des données
        print("\n1️⃣ Test du chargement des données...")
        loader = DataLoader("data/raw")
        plm, mes, erp = loader.load_all_data()

        assert plm is not None, "PLM non chargé"
        assert mes is not None, "MES non chargé"
        assert erp is not None, "ERP non chargé"
        print("   ✅ Données chargées")

        # 2. Génération de l'event log
        print("\n2️⃣ Test de la génération de l'event log...")
        builder = EventLogBuilder(plm, mes, erp)
        event_log = builder.generate_event_log(num_cases=50)

        assert len(event_log) > 0, "Event log vide"
        assert event_log["case_id"].nunique() == 50, "Nombre de cases incorrect"
        print(f"   ✅ Event log généré: {len(event_log)} événements")

        # 3. Process Mining
        print("\n3️⃣ Test du Process Mining...")
        pm = ProcessMiner(event_log)
        overview = pm.get_process_overview()

        assert overview["nombre_pieces"] == 50, "Nombre de pièces incorrect"
        assert overview["lead_time_moyen"] > 0, "Lead time invalide"
        print(f"   ✅ Process mining OK - Lead time: {overview['lead_time_moyen']:.2f}h")

        # 4. Détection des goulots
        print("\n4️⃣ Test de la détection des goulots...")
        bd = BottleneckDetector(event_log)
        bottlenecks = bd.detect_bottlenecks_by_wait_time()

        assert len(bottlenecks) > 0, "Aucun goulot détecté"
        num_bottlenecks = bottlenecks["is_bottleneck"].sum()
        print(f"   ✅ {num_bottlenecks} goulots identifiés")

        # 5. Analyse WIP
        print("\n5️⃣ Test de l'analyse WIP...")
        wip = WIPAnalyzer(event_log)
        wip_by_activity = wip.calculate_wip_by_activity()

        assert len(wip_by_activity) > 0, "Aucune analyse WIP"
        avg_wip = wip_by_activity["wip_mean"].mean()
        print(f"   ✅ WIP moyen: {avg_wip:.2f} pièces")

        # 6. Analyse Rework
        print("\n6️⃣ Test de l'analyse des reworks...")
        rt = ReworkTracker(event_log)
        rework_summary = rt.get_rework_summary()

        assert "global_rework_rate_pct" in rework_summary, "Taux de rework manquant"
        print(f"   ✅ Taux de rework: {rework_summary['global_rework_rate_pct']:.1f}%")

        # 7. Optimisation
        print("\n7️⃣ Test de l'optimisation...")
        optimizer = ManufacturingOptimizer(event_log)
        opportunities = optimizer.identify_optimization_opportunities()

        assert len(opportunities) > 0, "Aucune opportunité identifiée"
        print(f"   ✅ {sum(len(v) if isinstance(v, list) else 1 for v in opportunities.values())} opportunités trouvées")

        recommendations = optimizer.generate_recommendations(opportunities)
        assert len(recommendations) >= 3, "Pas assez de recommandations"
        print(f"   ✅ {len(recommendations)} recommandations générées")

        print("\n✅ WORKFLOW COMPLET VALIDÉ")

    def test_data_consistency_through_pipeline(self):
        """Vérifie la cohérence des données tout au long du pipeline"""

        # Charger les données
        loader = DataLoader("data/raw")
        plm, mes, erp = loader.load_all_data()

        # Générer event log
        builder = EventLogBuilder(plm, mes, erp)
        event_log = builder.generate_event_log(num_cases=30)

        # Vérifier que les références PLM sont préservées
        event_log_refs = event_log["reference"].unique()
        plm_refs = plm["Sheet1"]["Code / Référence"].unique()

        assert all(ref in plm_refs for ref in event_log_refs), \
            "Certaines références ne viennent pas du PLM"

        # Vérifier que les ressources ERP sont préservées
        event_log_resources = event_log["resource_id"].unique()
        erp_resources = erp["Matricule"].unique()

        assert all(res in erp_resources for res in event_log_resources), \
            "Certaines ressources ne viennent pas de l'ERP"

        print("✅ Cohérence des données vérifiée à travers le pipeline")

    def test_kpis_calculation(self):
        """Vérifie que tous les KPIs clés sont calculés"""

        # Charger event log existant
        event_log = pd.read_csv("data/event_logs/manufacturing_event_log.csv")

        # Calculer tous les KPIs
        pm = ProcessMiner(event_log)
        bd = BottleneckDetector(event_log)
        wip = WIPAnalyzer(event_log)
        rt = ReworkTracker(event_log)

        # Collecter tous les KPIs
        overview = pm.get_process_overview()
        inventory = wip.calculate_inventory_profile()
        flow_eff = wip.calculate_flow_efficiency()
        rework_summary = rt.get_rework_summary()

        kpis = {
            "lead_time_moyen_h": overview["lead_time_moyen"],
            "wip_moyen": inventory["actual_wip"],
            "throughput_pieces_par_jour": overview["throughput"] * 24,
            "taux_rework_pct": overview["taux_rework"],
            "flow_efficiency_pct": flow_eff["avg_flow_efficiency"],
            "nombre_goulots": bd.detect_bottlenecks_by_wait_time()["is_bottleneck"].sum()
        }

        # Vérifier que tous les KPIs sont valides
        for key, value in kpis.items():
            assert value is not None, f"KPI {key} est None"
            assert not pd.isna(value), f"KPI {key} est NaN"
            assert value >= 0, f"KPI {key} est négatif: {value}"

        print(f"✅ Tous les KPIs sont valides: {kpis}")

    def test_output_files_generation(self):
        """Vérifie que tous les fichiers de sortie sont générés"""

        # Vérifier les rapports
        reports_dir = Path("outputs/reports")
        assert reports_dir.exists(), "Dossier reports manquant"

        expected_files = [
            "kpis_summary.json",
            "bottlenecks_wait_time.csv",
            "wip_by_activity.csv",
            "rework_rate.csv"
        ]

        for file in expected_files:
            filepath = reports_dir / file
            assert filepath.exists(), f"Fichier {file} manquant"

        # Vérifier que les fichiers JSON sont valides
        with open(reports_dir / "kpis_summary.json", "r") as f:
            kpis = json.load(f)
            assert len(kpis) > 0, "KPIs JSON vide"

        print("✅ Tous les fichiers de sortie sont présents")

    def test_visualizations_generation(self):
        """Vérifie que les visualisations sont générées"""

        viz_dir = Path("outputs/visualizations")
        assert viz_dir.exists(), "Dossier visualizations manquant"

        expected_viz = [
            "process_map.html",
            "wip_heatmap.html",
            "pareto_bottlenecks.html",
            "gantt_chart.html"
        ]

        for viz in expected_viz:
            filepath = viz_dir / viz
            assert filepath.exists(), f"Visualisation {viz} manquante"

            # Vérifier que le fichier n'est pas vide
            assert filepath.stat().st_size > 0, f"Visualisation {viz} est vide"

        print("✅ Toutes les visualisations sont générées")

    def test_recommendations_quality(self):
        """Vérifie la qualité des recommandations"""

        # Charger les recommandations
        rec_file = Path("outputs/recommendations/recommendations.json")
        assert rec_file.exists(), "Fichier recommendations.json manquant"

        with open(rec_file, "r") as f:
            recommendations = json.load(f)

        assert len(recommendations) >= 3, "Pas assez de recommandations"

        # Vérifier la structure de chaque recommandation
        for rec in recommendations[:3]:
            required_keys = [
                "priority", "action", "problem", "details",
                "estimated_wip_reduction_pct", "estimated_leadtime_reduction_pct",
                "estimated_cost_euros", "roi"
            ]

            for key in required_keys:
                assert key in rec, f"Clé {key} manquante dans recommandation"

            # Vérifier les valeurs
            assert rec["priority"] in ["HIGH", "MEDIUM", "LOW"], \
                "Priorité invalide"
            assert rec["estimated_wip_reduction_pct"] > 0, \
                "Impact WIP doit être positif"
            assert rec["estimated_cost_euros"] > 0, \
                "Coût doit être positif"

        print(f"✅ {len(recommendations)} recommandations de qualité générées")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
