"""
Bottleneck Detector pour Manufacturing Operations Radar
Détecte et analyse les goulots d'étranglement
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class BottleneckDetector:
    """Détecte les goulots d'étranglement dans le flux de production"""

    def __init__(self, event_log: pd.DataFrame):
        self.event_log = event_log.copy()
        self._prepare_data()

    def _prepare_data(self):
        """Prépare les données pour l'analyse"""
        if not pd.api.types.is_datetime64_any_dtype(self.event_log['timestamp_start']):
            self.event_log['timestamp_start'] = pd.to_datetime(self.event_log['timestamp_start'])
        if not pd.api.types.is_datetime64_any_dtype(self.event_log['timestamp_end']):
            self.event_log['timestamp_end'] = pd.to_datetime(self.event_log['timestamp_end'])

    def detect_bottlenecks_by_wait_time(self, threshold_multiplier: float = 2.0) -> pd.DataFrame:
        """
        Détecte les goulots basés sur les temps d'attente
        Un goulot = temps d'attente > threshold_multiplier * temps de cycle moyen
        """
        # Calculer temps de cycle moyen et temps d'attente moyen par activité
        stats = self.event_log.groupby('activity').agg({
            'temps_reel': 'mean',
            'wait_time': 'mean',
            'case_id': 'count'
        }).reset_index()

        stats.columns = ['activity', 'cycle_time_mean', 'wait_time_mean', 'event_count']

        # Ratio attente / cycle
        stats['wait_to_cycle_ratio'] = stats['wait_time_mean'] / stats['cycle_time_mean']

        # Identifier les goulots
        global_mean_cycle = stats['cycle_time_mean'].mean()
        stats['is_bottleneck'] = stats['wait_time_mean'] > (threshold_multiplier * global_mean_cycle)

        # Trier par ratio décroissant
        stats = stats.sort_values('wait_to_cycle_ratio', ascending=False)

        # Calculer l'impact (% du temps d'attente total)
        total_wait = stats['wait_time_mean'].sum()
        stats['wait_time_impact_pct'] = (stats['wait_time_mean'] / total_wait * 100).round(1)

        return stats

    def detect_bottlenecks_by_wip(self) -> pd.DataFrame:
        """
        Détecte les goulots basés sur le WIP (Work In Progress)
        Plus de WIP = plus de congestion = goulot potentiel
        """
        # Calculer le WIP moyen par activité dans le temps
        # Pour chaque timestamp, compter combien de pièces sont en cours pour chaque activité

        wip_data = []

        # Obtenir tous les timestamps uniques
        all_timestamps = pd.concat([
            self.event_log['timestamp_start'],
            self.event_log['timestamp_end']
        ]).sort_values().unique()

        # Pour chaque activité
        for activity in self.event_log['activity'].unique():
            activity_events = self.event_log[self.event_log['activity'] == activity]

            wip_values = []
            for ts in all_timestamps:
                # Compter combien d'événements sont en cours à ce timestamp
                in_progress = (
                    (activity_events['timestamp_start'] <= ts) &
                    (activity_events['timestamp_end'] >= ts)
                ).sum()
                wip_values.append(in_progress)

            wip_data.append({
                'activity': activity,
                'wip_mean': np.mean(wip_values),
                'wip_max': np.max(wip_values),
                'wip_std': np.std(wip_values)
            })

        wip_df = pd.DataFrame(wip_data)
        wip_df = wip_df.sort_values('wip_mean', ascending=False)

        # Identifier les goulots (WIP moyen > 1.5x la moyenne globale)
        global_mean_wip = wip_df['wip_mean'].mean()
        wip_df['is_bottleneck'] = wip_df['wip_mean'] > (1.5 * global_mean_wip)

        return wip_df

    def detect_bottlenecks_by_utilization(self) -> pd.DataFrame:
        """
        Détecte les goulots basés sur le taux d'utilisation
        Utilisation élevée = ressource contrainte = goulot
        """
        # Calculer le taux d'utilisation par station
        station_stats = self.event_log.groupby('station_id').agg({
            'temps_reel': 'sum',
            'case_id': 'count'
        }).reset_index()

        # Calculer la période d'observation
        periode_start = self.event_log['timestamp_start'].min()
        periode_end = self.event_log['timestamp_end'].max()
        periode_hours = (periode_end - periode_start).total_seconds() / 3600

        # Taux d'utilisation = temps total travaillé / temps total disponible
        station_stats['utilization_pct'] = (
            station_stats['temps_reel'] / periode_hours * 100
        ).round(1)

        station_stats.columns = ['station_id', 'total_work_hours', 'event_count', 'utilization_pct']

        # Identifier les goulots (utilisation > 80%)
        station_stats['is_bottleneck'] = station_stats['utilization_pct'] > 80

        station_stats = station_stats.sort_values('utilization_pct', ascending=False)

        return station_stats

    def analyze_queue_times(self) -> pd.DataFrame:
        """
        Analyse les temps de file d'attente par activité
        """
        # Trier par case et timestamp
        df = self.event_log.sort_values(['case_id', 'timestamp_start'])

        # Calculer le temps entre la fin de l'activité précédente et le début de la suivante
        df['prev_end'] = df.groupby('case_id')['timestamp_end'].shift(1)
        df['queue_time'] = (df['timestamp_start'] - df['prev_end']).dt.total_seconds() / 3600

        # Nettoyer (ignorer valeurs négatives ou NaN)
        df['queue_time'] = df['queue_time'].clip(lower=0)

        # Statistiques par activité
        queue_stats = df.groupby('activity')['queue_time'].agg([
            'mean', 'std', 'min', 'max', 'count'
        ]).reset_index()

        queue_stats.columns = [
            'activity', 'queue_time_mean', 'queue_time_std',
            'queue_time_min', 'queue_time_max', 'event_count'
        ]

        queue_stats = queue_stats.sort_values('queue_time_mean', ascending=False)

        return queue_stats

    def get_bottleneck_summary(self) -> Dict:
        """
        Résumé complet des goulots d'étranglement
        """
        wait_bottlenecks = self.detect_bottlenecks_by_wait_time()
        wip_bottlenecks = self.detect_bottlenecks_by_wip()
        util_bottlenecks = self.detect_bottlenecks_by_utilization()

        # Top 3 goulots par chaque méthode
        top_wait = wait_bottlenecks.head(3)
        top_wip = wip_bottlenecks.head(3)
        top_util = util_bottlenecks.head(3)

        summary = {
            'by_wait_time': {
                'top_bottlenecks': top_wait.to_dict('records'),
                'total_bottlenecks': wait_bottlenecks['is_bottleneck'].sum()
            },
            'by_wip': {
                'top_bottlenecks': top_wip.to_dict('records'),
                'total_bottlenecks': wip_bottlenecks['is_bottleneck'].sum()
            },
            'by_utilization': {
                'top_bottlenecks': top_util.to_dict('records'),
                'total_bottlenecks': util_bottlenecks['is_bottleneck'].sum()
            }
        }

        return summary

    def calculate_bottleneck_impact(self) -> pd.DataFrame:
        """
        Calcule l'impact de chaque goulot sur le lead time global
        """
        # Calculer le lead time par pièce
        lead_times = self.event_log.groupby('case_id').agg({
            'timestamp_start': 'min',
            'timestamp_end': 'max'
        })
        lead_times['lead_time'] = (
            lead_times['timestamp_end'] - lead_times['timestamp_start']
        ).dt.total_seconds() / 3600

        avg_lead_time = lead_times['lead_time'].mean()

        # Pour chaque activité, calculer sa contribution au lead time
        activity_contributions = self.event_log.groupby('activity').agg({
            'temps_reel': 'mean',
            'wait_time': 'mean',
            'case_id': 'count'
        }).reset_index()

        activity_contributions.columns = [
            'activity', 'avg_cycle_time', 'avg_wait_time', 'event_count'
        ]

        # Temps total (cycle + attente) par activité
        activity_contributions['total_time'] = (
            activity_contributions['avg_cycle_time'] + activity_contributions['avg_wait_time']
        )

        # % du lead time
        activity_contributions['leadtime_contribution_pct'] = (
            activity_contributions['total_time'] / avg_lead_time * 100
        ).round(1)

        activity_contributions = activity_contributions.sort_values(
            'leadtime_contribution_pct', ascending=False
        )

        return activity_contributions


print("✅ BottleneckDetector class loaded")
