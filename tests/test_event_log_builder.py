"""
Tests de validation pour l'Event Log Builder
Vérifie que l'event log est correctement généré à partir des données
"""

import pytest
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent / "src"))

from data_processing.data_loader import DataLoader
from data_processing.event_log_builder import EventLogBuilder


class TestEventLogBuilder:
    """Tests pour la génération de l'event log"""

    @pytest.fixture
    def builder(self):
        """Fixture pour créer un builder"""
        loader = DataLoader("data/raw")
        plm, mes, erp = loader.load_all_data()
        return EventLogBuilder(plm, mes, erp)

    def test_operation_sequence(self, builder):
        """Vérifie que la séquence d'opérations est cohérente"""
        operations = builder.get_operation_sequence()

        # Doit avoir entre 4 et 8 opérations
        assert 4 <= len(operations) <= 8, f"Attendu 4-8 opérations, trouvé {len(operations)}"

        # Toutes les opérations doivent être uniques
        assert len(operations) == len(set(operations)), "Opérations dupliquées"

        # Les opérations doivent venir du MES
        mes_operations = builder.mes_data["Nom"].unique()
        for op in operations:
            assert op in mes_operations, f"Opération {op} non trouvée dans MES"

    def test_operation_stats(self, builder):
        """Vérifie les statistiques d'opérations"""
        operations = builder.get_operation_sequence()

        for op in operations[:3]:  # Tester les 3 premières
            stats = builder.get_operation_stats(op)

            # Vérifier la structure
            assert "temps_prevu_moyen" in stats
            assert "temps_reel_moyen" in stats
            assert "variabilite" in stats
            assert "taux_alea" in stats

            # Vérifier les valeurs
            assert stats["temps_prevu_moyen"] > 0, f"Temps prévu invalide pour {op}"
            assert stats["temps_reel_moyen"] > 0, f"Temps réel invalide pour {op}"
            assert 0 <= stats["taux_alea"] <= 1, f"Taux aléa invalide pour {op}"

    def test_generate_event_log(self, builder):
        """Vérifie la génération de l'event log"""
        num_cases = 50
        event_log = builder.generate_event_log(num_cases=num_cases)

        # Vérifier que c'est un DataFrame
        assert isinstance(event_log, pd.DataFrame), "Event log doit être un DataFrame"

        # Vérifier le nombre de cases
        unique_cases = event_log["case_id"].nunique()
        assert unique_cases == num_cases, f"Attendu {num_cases} cases, trouvé {unique_cases}"

        # Vérifier les colonnes essentielles
        required_cols = [
            "case_id", "activity", "timestamp_start", "timestamp_end",
            "station_id", "resource_id", "result", "rework_flag",
            "reference", "temps_prevu", "temps_reel"
        ]
        for col in required_cols:
            assert col in event_log.columns, f"Colonne {col} manquante dans event log"

    def test_event_log_structure(self, builder):
        """Vérifie la structure détaillée de l'event log"""
        event_log = builder.generate_event_log(num_cases=20)

        # Vérifier les types de données
        assert pd.api.types.is_datetime64_any_dtype(event_log["timestamp_start"]), \
            "timestamp_start doit être datetime"
        assert pd.api.types.is_datetime64_any_dtype(event_log["timestamp_end"]), \
            "timestamp_end doit être datetime"

        # Vérifier que timestamp_end > timestamp_start
        assert (event_log["timestamp_end"] >= event_log["timestamp_start"]).all(), \
            "timestamp_end doit être >= timestamp_start"

        # Vérifier les valeurs de result
        valid_results = {"OK", "Rework", "NOK"}
        assert event_log["result"].isin(valid_results).all(), \
            f"Résultats invalides, attendu {valid_results}"

        # Vérifier que rework_flag est booléen
        assert event_log["rework_flag"].dtype == bool, "rework_flag doit être booléen"

    def test_event_log_completeness(self, builder):
        """Vérifie que chaque pièce passe par toutes les opérations"""
        event_log = builder.generate_event_log(num_cases=30)
        operations = builder.get_operation_sequence()

        # Pour chaque case, vérifier qu'elle a au moins passé par les opérations principales
        for case_id in event_log["case_id"].unique()[:5]:  # Tester 5 cases
            case_events = event_log[event_log["case_id"] == case_id]
            case_ops = case_events["activity"].unique()

            # Retirer les suffixes "_Rework"
            main_ops = [op.replace("_Rework", "") for op in case_ops]
            main_ops = list(set(main_ops))

            # Doit avoir au moins 4 opérations principales
            assert len(main_ops) >= 4, \
                f"Case {case_id} n'a que {len(main_ops)} opérations"

    def test_rework_logic(self, builder):
        """Vérifie la logique de rework"""
        event_log = builder.generate_event_log(num_cases=100)

        # Compter les reworks
        rework_events = event_log[event_log["rework_flag"]].copy()
        total_events = len(event_log)
        rework_rate = len(rework_events) / total_events * 100

        # Le taux de rework doit être entre 5% et 25%
        assert 5 <= rework_rate <= 25, \
            f"Taux de rework anormal: {rework_rate:.1f}% (attendu 5-25%)"

        # Vérifier que les événements de rework ont bien le flag
        assert rework_events["rework_flag"].all(), \
            "Tous les événements de rework doivent avoir rework_flag=True"

    def test_resource_assignment(self, builder):
        """Vérifie l'assignation des ressources"""
        event_log = builder.generate_event_log(num_cases=50)

        # Vérifier que toutes les ressources sont assignées
        assert event_log["resource_id"].notna().all(), \
            "Toutes les opérations doivent avoir une ressource"

        # Vérifier le format des resource_id (commence par AIR)
        assert event_log["resource_id"].str.startswith("AIR").all(), \
            "Les matricules doivent commencer par AIR"

        # Vérifier que les qualifications sont présentes
        assert event_log["qualification"].notna().all(), \
            "Toutes les ressources doivent avoir une qualification"

    def test_time_consistency(self, builder):
        """Vérifie la cohérence temporelle"""
        event_log = builder.generate_event_log(num_cases=50)

        # Pour chaque case, vérifier l'ordre chronologique
        for case_id in event_log["case_id"].unique()[:10]:  # Tester 10 cases
            case_events = event_log[event_log["case_id"] == case_id].sort_values("timestamp_start")

            # Vérifier que les événements sont bien ordonnés
            timestamps = case_events["timestamp_start"].values
            assert (timestamps[:-1] <= timestamps[1:]).all(), \
                f"Événements non ordonnés pour case {case_id}"

    def test_data_from_sources(self, builder):
        """Vérifie que les données proviennent bien des sources"""
        event_log = builder.generate_event_log(num_cases=30)

        # Vérifier que les références viennent du PLM
        plm_refs = builder.plm_data["Sheet1"]["Code / Référence"].unique()
        assert event_log["reference"].isin(plm_refs).all(), \
            "Toutes les références doivent venir du PLM"

        # Vérifier que les ressources viennent de l'ERP
        erp_matricules = builder.erp_data["Matricule"].unique()
        assert event_log["resource_id"].isin(erp_matricules).all(), \
            "Toutes les ressources doivent venir de l'ERP"

        # Vérifier que les activités viennent du MES
        mes_operations = builder.mes_data["Nom"].unique()
        main_activities = [act.replace("_Rework", "") for act in event_log["activity"].unique()]
        for act in set(main_activities):
            assert act in mes_operations, \
                f"Activité {act} non trouvée dans MES"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
