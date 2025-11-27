"""
WIP Analyzer pour Manufacturing Operations Radar
Analyse le Work In Progress par étape et dans le temps
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class WIPAnalyzer:
    """Analyse le WIP (Work In Progress) dans la chaîne de production"""

    def __init__(self, event_log: pd.DataFrame):
        self.event_log = event_log.copy()
        self._prepare_data()

    def _prepare_data(self):
        """Prépare les données pour l'analyse"""
        if not pd.api.types.is_datetime64_any_dtype(self.event_log['timestamp_start']):
            self.event_log['timestamp_start'] = pd.to_datetime(self.event_log['timestamp_start'])
        if not pd.api.types.is_datetime64_any_dtype(self.event_log['timestamp_end']):
            self.event_log['timestamp_end'] = pd.to_datetime(self.event_log['timestamp_end'])

    def calculate_wip_over_time(self, time_interval: str = '1H') -> pd.DataFrame:
        """
        Calcule le WIP dans le temps avec un intervalle de temps donné
        time_interval: '1H' (1 heure), '30min', '2H', etc.
        """
        # Période d'observation
        start_time = self.event_log['timestamp_start'].min()
        end_time = self.event_log['timestamp_end'].max()

        # Créer une grille de temps
        time_range = pd.date_range(start=start_time, end=end_time, freq=time_interval)

        wip_data = []

        for ts in time_range:
            # Pour chaque timestamp, compter le WIP total
            in_progress = (
                (self.event_log['timestamp_start'] <= ts) &
                (self.event_log['timestamp_end'] >= ts)
            )

            wip_total = in_progress.sum()

            # WIP par activité
            wip_by_activity = self.event_log[in_progress].groupby('activity').size().to_dict()

            wip_data.append({
                'timestamp': ts,
                'wip_total': wip_total,
                **{f'wip_{act}': count for act, count in wip_by_activity.items()}
            })

        wip_df = pd.DataFrame(wip_data)
        wip_df = wip_df.fillna(0)

        return wip_df

    def calculate_wip_by_activity(self) -> pd.DataFrame:
        """
        Calcule les statistiques de WIP par activité
        """
        # Obtenir tous les timestamps uniques
        all_timestamps = pd.concat([
            self.event_log['timestamp_start'],
            self.event_log['timestamp_end']
        ]).sort_values().unique()

        wip_stats = []

        for activity in self.event_log['activity'].unique():
            activity_events = self.event_log[self.event_log['activity'] == activity]

            wip_values = []
            for ts in all_timestamps:
                # Compter le WIP à ce timestamp
                in_progress = (
                    (activity_events['timestamp_start'] <= ts) &
                    (activity_events['timestamp_end'] >= ts)
                ).sum()
                wip_values.append(in_progress)

            wip_stats.append({
                'activity': activity,
                'wip_mean': np.mean(wip_values),
                'wip_median': np.median(wip_values),
                'wip_max': np.max(wip_values),
                'wip_min': np.min(wip_values),
                'wip_std': np.std(wip_values),
                'event_count': len(activity_events)
            })

        wip_df = pd.DataFrame(wip_stats)
        wip_df = wip_df.sort_values('wip_mean', ascending=False)

        return wip_df

    def calculate_wip_by_station(self) -> pd.DataFrame:
        """
        Calcule les statistiques de WIP par station
        """
        # Obtenir tous les timestamps uniques
        all_timestamps = pd.concat([
            self.event_log['timestamp_start'],
            self.event_log['timestamp_end']
        ]).sort_values().unique()

        wip_stats = []

        for station in self.event_log['station_id'].unique():
            station_events = self.event_log[self.event_log['station_id'] == station]

            wip_values = []
            for ts in all_timestamps:
                # Compter le WIP à ce timestamp
                in_progress = (
                    (station_events['timestamp_start'] <= ts) &
                    (station_events['timestamp_end'] >= ts)
                ).sum()
                wip_values.append(in_progress)

            wip_stats.append({
                'station_id': station,
                'wip_mean': np.mean(wip_values),
                'wip_max': np.max(wip_values),
                'wip_std': np.std(wip_values),
                'event_count': len(station_events)
            })

        wip_df = pd.DataFrame(wip_stats)
        wip_df = wip_df.sort_values('wip_mean', ascending=False)

        return wip_df

    def calculate_inventory_profile(self) -> Dict:
        """
        Calcule le profil d'inventaire (stock en cours)
        """
        # Lead time moyen
        lead_times = self.event_log.groupby('case_id').agg({
            'timestamp_start': 'min',
            'timestamp_end': 'max'
        })
        lead_times['lead_time'] = (
            lead_times['timestamp_end'] - lead_times['timestamp_start']
        ).dt.total_seconds() / 3600

        avg_lead_time = lead_times['lead_time'].mean()

        # Throughput (pièces/heure)
        periode_start = self.event_log['timestamp_start'].min()
        periode_end = self.event_log['timestamp_end'].max()
        periode_hours = (periode_end - periode_start).total_seconds() / 3600
        throughput = self.event_log['case_id'].nunique() / periode_hours

        # Little's Law: WIP = Throughput × Lead Time
        theoretical_wip = throughput * avg_lead_time

        # WIP réel moyen
        wip_over_time = self.calculate_wip_over_time(time_interval='1H')
        actual_wip = wip_over_time['wip_total'].mean()

        return {
            'avg_lead_time_hours': avg_lead_time,
            'throughput_pieces_per_hour': throughput,
            'theoretical_wip': theoretical_wip,
            'actual_wip': actual_wip,
            'wip_efficiency': (theoretical_wip / actual_wip * 100) if actual_wip > 0 else 0
        }

    def identify_wip_accumulation_points(self, threshold: float = 1.5) -> pd.DataFrame:
        """
        Identifie les points d'accumulation de WIP
        (activités où le WIP moyen est supérieur à threshold * WIP moyen global)
        """
        wip_by_activity = self.calculate_wip_by_activity()

        global_mean_wip = wip_by_activity['wip_mean'].mean()
        threshold_value = threshold * global_mean_wip

        accumulation_points = wip_by_activity[
            wip_by_activity['wip_mean'] > threshold_value
        ].copy()

        accumulation_points['wip_excess'] = (
            accumulation_points['wip_mean'] - global_mean_wip
        ).round(2)

        accumulation_points['wip_excess_pct'] = (
            (accumulation_points['wip_mean'] / global_mean_wip - 1) * 100
        ).round(1)

        return accumulation_points

    def calculate_flow_efficiency(self) -> Dict:
        """
        Calcule l'efficacité du flux (Value-Adding Time / Total Lead Time)
        """
        # Temps à valeur ajoutée = somme des temps de cycle
        value_adding_time = self.event_log.groupby('case_id')['temps_reel'].sum()

        # Lead time total
        lead_times = self.event_log.groupby('case_id').agg({
            'timestamp_start': 'min',
            'timestamp_end': 'max'
        })
        lead_times['lead_time'] = (
            lead_times['timestamp_end'] - lead_times['timestamp_start']
        ).dt.total_seconds() / 3600

        # Joindre
        efficiency_data = pd.DataFrame({
            'value_adding_time': value_adding_time,
            'lead_time': lead_times['lead_time']
        })

        efficiency_data['flow_efficiency'] = (
            efficiency_data['value_adding_time'] / efficiency_data['lead_time'] * 100
        )

        return {
            'avg_flow_efficiency': efficiency_data['flow_efficiency'].mean(),
            'median_flow_efficiency': efficiency_data['flow_efficiency'].median(),
            'min_flow_efficiency': efficiency_data['flow_efficiency'].min(),
            'max_flow_efficiency': efficiency_data['flow_efficiency'].max(),
            'avg_value_adding_time': efficiency_data['value_adding_time'].mean(),
            'avg_lead_time': efficiency_data['lead_time'].mean(),
            'avg_waste_time': (
                efficiency_data['lead_time'] - efficiency_data['value_adding_time']
            ).mean()
        }

    def get_wip_summary(self) -> Dict:
        """
        Résumé complet du WIP
        """
        wip_by_activity = self.calculate_wip_by_activity()
        inventory_profile = self.calculate_inventory_profile()
        flow_efficiency = self.calculate_flow_efficiency()
        accumulation_points = self.identify_wip_accumulation_points()

        summary = {
            'total_wip_mean': wip_by_activity['wip_mean'].sum(),
            'total_wip_max': wip_by_activity['wip_max'].sum(),
            'activities_with_highest_wip': wip_by_activity.head(3).to_dict('records'),
            'inventory_profile': inventory_profile,
            'flow_efficiency': flow_efficiency,
            'accumulation_points_count': len(accumulation_points),
            'accumulation_points': accumulation_points.to_dict('records')
        }

        return summary


print("✅ WIPAnalyzer class loaded")
