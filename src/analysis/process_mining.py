"""
Process Mining pour Manufacturing Operations Radar
Analyse du flux de production et métriques clés
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import timedelta


class ProcessMiner:
    """Analyse du flux de production"""

    def __init__(self, event_log: pd.DataFrame):
        self.event_log = event_log.copy()
        self._prepare_data()

    def _prepare_data(self):
        """Prépare les données pour l'analyse"""
        # Convertir en datetime si nécessaire
        if not pd.api.types.is_datetime64_any_dtype(self.event_log['timestamp_start']):
            self.event_log['timestamp_start'] = pd.to_datetime(self.event_log['timestamp_start'])
        if not pd.api.types.is_datetime64_any_dtype(self.event_log['timestamp_end']):
            self.event_log['timestamp_end'] = pd.to_datetime(self.event_log['timestamp_end'])

        # Calculer la durée totale de chaque événement
        self.event_log['duration'] = (
            self.event_log['timestamp_end'] - self.event_log['timestamp_start']
        ).dt.total_seconds() / 3600  # en heures

    def calculate_lead_times(self) -> pd.DataFrame:
        """Calcule le lead time par pièce"""
        lead_times = self.event_log.groupby('case_id').agg({
            'timestamp_start': 'min',
            'timestamp_end': 'max'
        })

        lead_times['lead_time'] = (
            lead_times['timestamp_end'] - lead_times['timestamp_start']
        ).dt.total_seconds() / 3600  # en heures

        return lead_times

    def calculate_cycle_times(self) -> pd.DataFrame:
        """Calcule les temps de cycle par opération"""
        cycle_times = self.event_log.groupby('activity').agg({
            'temps_reel': ['mean', 'std', 'min', 'max'],
            'wait_time': ['mean', 'std', 'min', 'max'],
            'case_id': 'count'
        }).round(2)

        cycle_times.columns = [
            'Temps Réel Moyen (h)', 'Temps Réel Std (h)', 'Temps Réel Min (h)', 'Temps Réel Max (h)',
            'Temps Attente Moyen (h)', 'Temps Attente Std (h)', 'Temps Attente Min (h)', 'Temps Attente Max (h)',
            'Nombre Événements'
        ]

        return cycle_times

    def calculate_throughput(self) -> Dict:
        """Calcule le débit de production"""
        # Période totale
        periode_start = self.event_log['timestamp_start'].min()
        periode_end = self.event_log['timestamp_end'].max()
        periode_hours = (periode_end - periode_start).total_seconds() / 3600

        # Nombre de pièces complètes
        pieces_completes = self.event_log['case_id'].nunique()

        throughput = pieces_completes / periode_hours if periode_hours > 0 else 0

        return {
            'throughput_pieces_per_hour': throughput,
            'throughput_pieces_per_day': throughput * 24,
            'periode_hours': periode_hours,
            'pieces_completes': pieces_completes
        }

    def get_process_overview(self) -> Dict:
        """Vue d'ensemble du processus"""
        lead_times = self.calculate_lead_times()
        throughput = self.calculate_throughput()

        overview = {
            'nombre_pieces': self.event_log['case_id'].nunique(),
            'nombre_operations': self.event_log['activity'].nunique(),
            'nombre_evenements': len(self.event_log),
            'lead_time_moyen': lead_times['lead_time'].mean(),
            'lead_time_std': lead_times['lead_time'].std(),
            'lead_time_min': lead_times['lead_time'].min(),
            'lead_time_max': lead_times['lead_time'].max(),
            'taux_rework': self.event_log['rework_flag'].mean() * 100,
            'throughput': throughput['throughput_pieces_per_hour'],
            'periode_debut': self.event_log['timestamp_start'].min(),
            'periode_fin': self.event_log['timestamp_end'].max()
        }

        return overview

    def analyze_variants(self) -> pd.DataFrame:
        """Analyse des variantes de processus"""
        # Créer la trace (séquence d'activités) pour chaque case
        traces = self.event_log.groupby('case_id')['activity'].apply(
            lambda x: ' → '.join(x)
        ).reset_index()
        traces.columns = ['case_id', 'trace']

        # Compter les variantes
        variant_counts = traces['trace'].value_counts().reset_index()
        variant_counts.columns = ['Variante', 'Nombre de Pièces']
        variant_counts['Fréquence (%)'] = (
            variant_counts['Nombre de Pièces'] / len(traces) * 100
        ).round(2)

        return variant_counts

    def calculate_activity_matrix(self) -> pd.DataFrame:
        """Matrice de transition entre activités"""
        # Trier par case_id et timestamp
        df = self.event_log.sort_values(['case_id', 'timestamp_start'])

        # Créer les paires d'activités successives
        df['next_activity'] = df.groupby('case_id')['activity'].shift(-1)

        # Compter les transitions
        transitions = df.groupby(['activity', 'next_activity']).size().reset_index(name='count')
        transitions = transitions[transitions['next_activity'].notna()]

        # Créer la matrice
        matrix = transitions.pivot(index='activity', columns='next_activity', values='count')
        matrix = matrix.fillna(0).astype(int)

        return matrix


print("✅ ProcessMiner class loaded")
