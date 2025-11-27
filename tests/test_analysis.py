"""
Tests de validation pour les modules d'analyse
Vérifie que les analyses produisent des résultats cohérents
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from analysis.process_mining import ProcessMiner
from analysis.bottleneck_detector import BottleneckDetector
from analysis.wip_analyzer import WIPAnalyzer
from analysis.rework_tracker import ReworkTracker


class TestProcessMining:
    """Tests pour le Process Mining"""

    @pytest.fixture
    def event_log(self):
        """Fixture pour charger l'event log"""
        return pd.read_csv("data/event_logs/manufacturing_event_log.csv")

    @pytest.fixture
    def pm(self, event_log):
        """Fixture pour créer un ProcessMiner"""
        return ProcessMiner(event_log)

    def test_process_overview(self, pm):
        """Vérifie la vue d'ensemble du processus"""
        overview = pm.get_process_overview()

        # Vérifier la structure
        required_keys = [
            "nombre_pieces", "nombre_operations", "nombre_evenements",
            "lead_time_moyen", "lead_time_std", "taux_rework", "throughput"
        ]
        for key in required_keys:
            assert key in overview, f"Clé {key} manquante dans overview"

        # Vérifier les valeurs
        assert overview["nombre_pieces"] > 0, "Nombre de pièces doit être > 0"
        assert overview["nombre_operations"] >= 4, "Doit avoir au moins 4 opérations"
        assert overview["lead_time_moyen"] > 0, "Lead time moyen doit être > 0"
        assert 0 <= overview["taux_rework"] <= 100, "Taux rework doit être entre 0 et 100%"

    def test_lead_times(self, pm):
        """Vérifie les calculs de lead time"""
        lead_times = pm.calculate_lead_times()

        # Vérifier la structure
        assert "lead_time" in lead_times.columns, "Colonne lead_time manquante"

        # Vérifier les valeurs
        assert (lead_times["lead_time"] > 0).all(), "Tous les lead times doivent être > 0"
        assert lead_times["lead_time"].notna().all(), "Pas de NaN dans lead times"

    def test_cycle_times(self, pm):
        """Vérifie les calculs de temps de cycle"""
        cycle_times = pm.calculate_cycle_times()

        # Vérifier la structure
        assert len(cycle_times) > 0, "Doit avoir au moins une opération"

        # Vérifier que toutes les opérations ont des stats
        for idx, row in cycle_times.iterrows():
            assert row["Nombre Événements"] > 0, f"Pas d'événements pour {idx}"


class TestBottleneckDetector:
    """Tests pour la détection des goulots"""

    @pytest.fixture
    def event_log(self):
        """Fixture pour charger l'event log"""
        return pd.read_csv("data/event_logs/manufacturing_event_log.csv")

    @pytest.fixture
    def bd(self, event_log):
        """Fixture pour créer un BottleneckDetector"""
        return BottleneckDetector(event_log)

    def test_detect_bottlenecks_by_wait_time(self, bd):
        """Vérifie la détection des goulots par temps d'attente"""
        bottlenecks = bd.detect_bottlenecks_by_wait_time()

        # Vérifier la structure
        required_cols = [
            "activity", "cycle_time_mean", "wait_time_mean",
            "wait_to_cycle_ratio", "is_bottleneck"
        ]
        for col in required_cols:
            assert col in bottlenecks.columns, f"Colonne {col} manquante"

        # Vérifier qu'au moins un goulot est identifié
        assert bottlenecks["is_bottleneck"].sum() > 0, \
            "Au moins un goulot devrait être identifié"

        # Vérifier les valeurs
        assert (bottlenecks["wait_time_mean"] >= 0).all(), \
            "Temps d'attente doit être >= 0"

    def test_detect_bottlenecks_by_wip(self, bd):
        """Vérifie la détection des goulots par WIP"""
        bottlenecks_wip = bd.detect_bottlenecks_by_wip()

        # Vérifier la structure
        required_cols = ["activity", "wip_mean", "wip_max", "is_bottleneck"]
        for col in required_cols:
            assert col in bottlenecks_wip.columns, f"Colonne {col} manquante"

        # Vérifier les valeurs
        assert (bottlenecks_wip["wip_mean"] >= 0).all(), "WIP moyen doit être >= 0"
        assert (bottlenecks_wip["wip_max"] >= bottlenecks_wip["wip_mean"]).all(), \
            "WIP max doit être >= WIP moyen"

    def test_bottleneck_impact(self, bd):
        """Vérifie le calcul de l'impact des goulots"""
        impact = bd.calculate_bottleneck_impact()

        # Vérifier la structure
        required_cols = ["activity", "total_time", "leadtime_contribution_pct"]
        for col in required_cols:
            assert col in impact.columns, f"Colonne {col} manquante"

        # Vérifier que la somme des contributions est cohérente
        total_contribution = impact["leadtime_contribution_pct"].sum()
        # Peut être > 100% car certaines opérations se chevauchent
        assert total_contribution > 0, "Contribution totale doit être > 0"


class TestWIPAnalyzer:
    """Tests pour l'analyse du WIP"""

    @pytest.fixture
    def event_log(self):
        """Fixture pour charger l'event log"""
        return pd.read_csv("data/event_logs/manufacturing_event_log.csv")

    @pytest.fixture
    def wip(self, event_log):
        """Fixture pour créer un WIPAnalyzer"""
        return WIPAnalyzer(event_log)

    def test_wip_by_activity(self, wip):
        """Vérifie le calcul du WIP par activité"""
        wip_by_activity = wip.calculate_wip_by_activity()

        # Vérifier la structure
        required_cols = ["activity", "wip_mean", "wip_max", "wip_std"]
        for col in required_cols:
            assert col in wip_by_activity.columns, f"Colonne {col} manquante"

        # Vérifier les valeurs
        assert (wip_by_activity["wip_mean"] >= 0).all(), "WIP moyen doit être >= 0"
        assert (wip_by_activity["wip_max"] >= wip_by_activity["wip_mean"]).all(), \
            "WIP max doit être >= WIP moyen"

    def test_inventory_profile(self, wip):
        """Vérifie le profil d'inventaire (Little's Law)"""
        inventory = wip.calculate_inventory_profile()

        # Vérifier la structure
        required_keys = [
            "avg_lead_time_hours", "throughput_pieces_per_hour",
            "theoretical_wip", "actual_wip"
        ]
        for key in required_keys:
            assert key in inventory, f"Clé {key} manquante dans inventory"

        # Vérifier les valeurs
        assert inventory["avg_lead_time_hours"] > 0, "Lead time doit être > 0"
        assert inventory["throughput_pieces_per_hour"] > 0, "Throughput doit être > 0"
        assert inventory["theoretical_wip"] > 0, "WIP théorique doit être > 0"

    def test_flow_efficiency(self, wip):
        """Vérifie le calcul de l'efficacité du flux"""
        flow_eff = wip.calculate_flow_efficiency()

        # Vérifier la structure
        required_keys = [
            "avg_flow_efficiency", "avg_value_adding_time",
            "avg_lead_time", "avg_waste_time"
        ]
        for key in required_keys:
            assert key in flow_eff, f"Clé {key} manquante dans flow_efficiency"

        # Vérifier les valeurs
        assert 0 <= flow_eff["avg_flow_efficiency"] <= 100, \
            "Flow efficiency doit être entre 0 et 100%"


class TestReworkTracker:
    """Tests pour le tracking des reworks"""

    @pytest.fixture
    def event_log(self):
        """Fixture pour charger l'event log"""
        return pd.read_csv("data/event_logs/manufacturing_event_log.csv")

    @pytest.fixture
    def rt(self, event_log):
        """Fixture pour créer un ReworkTracker"""
        return ReworkTracker(event_log)

    def test_rework_rate_by_activity(self, rt):
        """Vérifie le calcul du taux de rework par activité"""
        rework_rate = rt.calculate_rework_rate_by_activity()

        # Vérifier la structure
        required_cols = ["activity", "total_events", "rework_events", "rework_rate_pct"]
        for col in required_cols:
            assert col in rework_rate.columns, f"Colonne {col} manquante"

        # Vérifier les valeurs
        assert (rework_rate["rework_rate_pct"] >= 0).all(), \
            "Taux de rework doit être >= 0"
        assert (rework_rate["rework_rate_pct"] <= 100).all(), \
            "Taux de rework doit être <= 100"

    def test_rework_impact_on_leadtime(self, rt):
        """Vérifie l'impact des reworks sur le lead time"""
        impact = rt.calculate_rework_impact_on_leadtime()

        # Vérifier la structure
        required_keys = [
            "avg_leadtime_with_rework", "avg_leadtime_without_rework",
            "pieces_with_rework", "pieces_without_rework", "leadtime_increase_pct"
        ]
        for key in required_keys:
            assert key in impact, f"Clé {key} manquante dans impact"

        # Vérifier les valeurs
        # Le lead time avec rework devrait être supérieur
        if impact["pieces_with_rework"] > 0 and impact["pieces_without_rework"] > 0:
            assert impact["avg_leadtime_with_rework"] >= impact["avg_leadtime_without_rework"], \
                "Lead time avec rework devrait être >= sans rework"

    def test_first_pass_yield(self, rt):
        """Vérifie le calcul du First Pass Yield"""
        fpy = rt.calculate_first_pass_yield()

        # Vérifier la structure
        required_cols = ["activity", "ok_count", "total_count", "fpy_pct"]
        for col in required_cols:
            assert col in fpy.columns, f"Colonne {col} manquante"

        # Vérifier les valeurs
        assert (fpy["fpy_pct"] >= 0).all(), "FPY doit être >= 0"
        assert (fpy["fpy_pct"] <= 100).all(), "FPY doit être <= 100"

    def test_rework_summary(self, rt):
        """Vérifie le résumé complet des reworks"""
        summary = rt.get_rework_summary()

        # Vérifier la structure
        required_keys = [
            "global_rework_rate_pct", "total_rework_events",
            "top_rework_activities", "leadtime_impact"
        ]
        for key in required_keys:
            assert key in summary, f"Clé {key} manquante dans summary"

        # Vérifier les valeurs
        assert 0 <= summary["global_rework_rate_pct"] <= 100, \
            "Taux global de rework doit être entre 0 et 100%"
        assert summary["total_rework_events"] >= 0, \
            "Nombre de reworks doit être >= 0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
