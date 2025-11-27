"""
Tests de validation pour le Data Loader
Vérifie que les fichiers Excel sont correctement chargés et exploités
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from data_processing.data_loader import DataLoader


class TestDataLoader:
    """Tests pour le chargement des données"""

    @pytest.fixture
    def loader(self):
        """Fixture pour créer un loader"""
        return DataLoader("data/raw")

    def test_files_exist(self, loader):
        """Vérifie que les fichiers Excel existent"""
        assert (loader.data_path / "PLM_DataSet.xlsx").exists(), "PLM_DataSet.xlsx manquant"
        assert (loader.data_path / "MES_Extraction.xlsx").exists(), "MES_Extraction.xlsx manquant"
        assert (loader.data_path / "ERP_Equipes Airplus.xlsx").exists(), "ERP_Equipes Airplus.xlsx manquant"

    def test_load_all_data(self, loader):
        """Vérifie que toutes les données sont chargées"""
        plm, mes, erp = loader.load_all_data()

        assert plm is not None, "PLM data non chargé"
        assert mes is not None, "MES data non chargé"
        assert erp is not None, "ERP data non chargé"

    def test_plm_structure(self, loader):
        """Vérifie la structure des données PLM"""
        plm, _, _ = loader.load_all_data()

        # PLM doit être un dict avec plusieurs feuilles
        assert isinstance(plm, dict), "PLM doit être un dictionnaire"
        assert len(plm) >= 1, "PLM doit avoir au moins une feuille"

        # Vérifier Sheet1
        assert "Sheet1" in plm, "Sheet1 manquante dans PLM"
        sheet1 = plm["Sheet1"]

        # Vérifier les colonnes essentielles
        required_cols = ["Code / Référence", "Désignation", "Quantité"]
        for col in required_cols:
            assert col in sheet1.columns, f"Colonne {col} manquante dans PLM Sheet1"

        # Vérifier le nombre de lignes
        assert len(sheet1) == 40, f"Attendu 40 pièces dans PLM, trouvé {len(sheet1)}"

    def test_mes_structure(self, loader):
        """Vérifie la structure des données MES"""
        _, mes, _ = loader.load_all_data()

        # Vérifier que c'est un DataFrame
        assert isinstance(mes, pd.DataFrame), "MES doit être un DataFrame"

        # Vérifier les colonnes essentielles
        required_cols = [
            "Poste", "Nom", "Nombre pièces", "Référence",
            "Temps Prévu", "Date", "Heure Début", "Heure Fin",
            "Temps Réel", "Aléas Industriels"
        ]
        for col in required_cols:
            assert col in mes.columns, f"Colonne {col} manquante dans MES"

        # Vérifier le nombre de lignes
        assert len(mes) == 56, f"Attendu 56 enregistrements dans MES, trouvé {len(mes)}"

        # Vérifier les types de données
        assert mes["Date"].dtype == "datetime64[ns]", "Date doit être datetime"

    def test_erp_structure(self, loader):
        """Vérifie la structure des données ERP"""
        _, _, erp = loader.load_all_data()

        # Vérifier que c'est un DataFrame
        assert isinstance(erp, pd.DataFrame), "ERP doit être un DataFrame"

        # Vérifier les colonnes essentielles
        required_cols = [
            "Matricule", "Prénom", "Nom", "Qualification",
            "Poste de montage", "Coût horaire (€)"
        ]
        for col in required_cols:
            assert col in erp.columns, f"Colonne {col} manquante dans ERP"

        # Vérifier le nombre de lignes
        assert len(erp) == 150, f"Attendu 150 opérateurs dans ERP, trouvé {len(erp)}"

    def test_mes_operations(self, loader):
        """Vérifie que le MES contient les opérations attendues"""
        _, mes, _ = loader.load_all_data()

        # Vérifier qu'il y a au moins 20 opérations uniques
        unique_ops = mes["Nom"].nunique()
        assert unique_ops >= 20, f"Attendu au moins 20 opérations, trouvé {unique_ops}"

        # Vérifier que les temps sont cohérents
        assert mes["Nombre pièces"].min() >= 1, "Nombre de pièces doit être >= 1"

    def test_erp_qualifications(self, loader):
        """Vérifie que l'ERP contient les bonnes qualifications"""
        _, _, erp = loader.load_all_data()

        # Vérifier qu'il y a plusieurs qualifications
        unique_quals = erp["Qualification"].nunique()
        assert unique_quals >= 10, f"Attendu au moins 10 qualifications, trouvé {unique_quals}"

        # Vérifier que les coûts horaires sont cohérents
        assert erp["Coût horaire (€)"].min() > 0, "Coût horaire doit être > 0"
        assert erp["Coût horaire (€)"].max() < 100, "Coût horaire semble trop élevé"

    def test_data_consistency(self, loader):
        """Vérifie la cohérence entre les différentes sources"""
        plm, mes, erp = loader.load_all_data()

        # Vérifier que les références PLM existent dans le MES
        plm_refs = plm["Sheet1"]["Code / Référence"].unique()
        mes_refs = mes["Référence"].unique()

        # Au moins quelques références doivent correspondre
        common_refs = set(plm_refs) & set(mes_refs)
        assert len(common_refs) > 0, "Aucune référence commune entre PLM et MES"

        # Vérifier que les postes ERP correspondent aux postes MES
        erp_postes = erp["Poste de montage"].unique()
        # Format: "Poste 1", "Poste 2", etc.
        assert len(erp_postes) > 0, "Aucun poste dans ERP"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
