"""
Data Loader pour Manufacturing Operations Radar
Charge et explore les données PLM, MES et ERP
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple

class DataLoader:
    """Classe pour charger et explorer les données du hackathon"""

    def __init__(self, data_path: str = "data/raw"):
        self.data_path = Path(data_path)
        self.plm_data = None
        self.mes_data = None
        self.erp_data = None

    def load_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Charge toutes les données Excel"""
        print("📂 Chargement des données...")

        # Charger PLM
        plm_file = self.data_path / "PLM_DataSet.xlsx"
        print(f"  - Chargement PLM: {plm_file}")
        self.plm_data = pd.read_excel(plm_file, sheet_name=None)  # Charge toutes les feuilles

        # Charger MES
        mes_file = self.data_path / "MES_Extraction.xlsx"
        print(f"  - Chargement MES: {mes_file}")
        self.mes_data = pd.read_excel(mes_file)

        # Charger ERP
        erp_file = self.data_path / "ERP_Equipes Airplus.xlsx"
        print(f"  - Chargement ERP: {erp_file}")
        self.erp_data = pd.read_excel(erp_file)

        print("✅ Données chargées avec succès!\n")
        return self.plm_data, self.mes_data, self.erp_data

    def explore_plm_data(self) -> Dict:
        """Explore les données PLM"""
        print("🔍 EXPLORATION PLM DATA")
        print("=" * 60)

        # PLM peut avoir plusieurs feuilles
        if isinstance(self.plm_data, dict):
            print(f"Nombre de feuilles: {len(self.plm_data)}")
            for sheet_name, df in self.plm_data.items():
                print(f"\n📊 Feuille: {sheet_name}")
                print(f"  Shape: {df.shape}")
                print(f"  Colonnes: {list(df.columns)}")
                print(f"\n  Aperçu des premières lignes:")
                print(df.head(3))
        else:
            print(f"Shape: {self.plm_data.shape}")
            print(f"Colonnes: {list(self.plm_data.columns)}")
            print(f"\nAperçu:")
            print(self.plm_data.head())

        return {"plm": self.plm_data}

    def explore_mes_data(self) -> Dict:
        """Explore les données MES"""
        print("\n🔍 EXPLORATION MES DATA")
        print("=" * 60)
        print(f"Shape: {self.mes_data.shape}")
        print(f"Colonnes: {list(self.mes_data.columns)}")

        print(f"\n📊 Types de données:")
        print(self.mes_data.dtypes)

        print(f"\n📊 Statistiques descriptives:")
        print(self.mes_data.describe())

        print(f"\n📊 Aperçu des premières lignes:")
        print(self.mes_data.head(10))

        print(f"\n📊 Valeurs uniques par colonne:")
        for col in self.mes_data.columns:
            n_unique = self.mes_data[col].nunique()
            print(f"  - {col}: {n_unique} valeurs uniques")

        return {"mes": self.mes_data}

    def explore_erp_data(self) -> Dict:
        """Explore les données ERP"""
        print("\n🔍 EXPLORATION ERP DATA")
        print("=" * 60)
        print(f"Shape: {self.erp_data.shape}")
        print(f"Colonnes: {list(self.erp_data.columns)}")

        print(f"\n📊 Aperçu des premières lignes:")
        print(self.erp_data.head())

        print(f"\n📊 Répartition par qualification:")
        if 'Qualification' in self.erp_data.columns:
            print(self.erp_data['Qualification'].value_counts())

        print(f"\n📊 Répartition par poste:")
        if 'Poste de montage' in self.erp_data.columns:
            print(self.erp_data['Poste de montage'].value_counts())

        return {"erp": self.erp_data}

    def get_summary(self) -> Dict:
        """Retourne un résumé de toutes les données"""
        summary = {
            "plm": {
                "type": type(self.plm_data),
                "sheets": list(self.plm_data.keys()) if isinstance(self.plm_data, dict) else None
            },
            "mes": {
                "rows": len(self.mes_data),
                "columns": list(self.mes_data.columns)
            },
            "erp": {
                "rows": len(self.erp_data),
                "columns": list(self.erp_data.columns)
            }
        }
        return summary


if __name__ == "__main__":
    # Test du loader
    loader = DataLoader()
    plm, mes, erp = loader.load_all_data()

    loader.explore_plm_data()
    loader.explore_mes_data()
    loader.explore_erp_data()

    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ")
    print("=" * 60)
    summary = loader.get_summary()
    print(summary)
