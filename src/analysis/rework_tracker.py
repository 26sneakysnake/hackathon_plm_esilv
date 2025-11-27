"""
Rework Tracker pour Manufacturing Operations Radar
Analyse et traçabilité des reworks
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class ReworkTracker:
    """Analyse les reworks dans la chaîne de production"""

    def __init__(self, event_log: pd.DataFrame):
        self.event_log = event_log.copy()
        self._prepare_data()

    def _prepare_data(self):
        """Prépare les données pour l'analyse"""
        if not pd.api.types.is_datetime64_any_dtype(self.event_log['timestamp_start']):
            self.event_log['timestamp_start'] = pd.to_datetime(self.event_log['timestamp_start'])
        if not pd.api.types.is_datetime64_any_dtype(self.event_log['timestamp_end']):
            self.event_log['timestamp_end'] = pd.to_datetime(self.event_log['timestamp_end'])

    def calculate_rework_rate_by_activity(self) -> pd.DataFrame:
        """
        Calcule le taux de rework par activité
        """
        # Filtrer les événements de rework
        rework_counts = self.event_log[self.event_log['rework_flag']].groupby('activity').size()
        total_counts = self.event_log.groupby('activity').size()

        rework_stats = pd.DataFrame({
            'activity': total_counts.index,
            'total_events': total_counts.values,
            'rework_events': rework_counts.reindex(total_counts.index, fill_value=0).values
        })

        rework_stats['rework_rate_pct'] = (
            rework_stats['rework_events'] / rework_stats['total_events'] * 100
        ).round(2)

        # Exclure les activités "_Rework" qui sont par définition à 100%
        rework_stats = rework_stats[~rework_stats['activity'].str.contains('_Rework', na=False)]

        rework_stats = rework_stats.sort_values('rework_rate_pct', ascending=False)

        return rework_stats

    def calculate_rework_cost(self) -> pd.DataFrame:
        """
        Calcule le coût des reworks
        """
        # Filtrer les événements de rework
        rework_events = self.event_log[self.event_log['rework_flag']].copy()

        # Calculer le coût (temps * coût horaire)
        rework_events['cost'] = rework_events['temps_reel'] * rework_events['cout_horaire']

        # Coût par activité
        rework_cost_by_activity = rework_events.groupby('activity').agg({
            'cost': ['sum', 'mean', 'count'],
            'temps_reel': 'sum'
        }).round(2)

        rework_cost_by_activity.columns = [
            'total_cost_euros', 'avg_cost_euros', 'rework_count', 'total_time_hours'
        ]

        rework_cost_by_activity = rework_cost_by_activity.reset_index()
        rework_cost_by_activity = rework_cost_by_activity.sort_values(
            'total_cost_euros', ascending=False
        )

        return rework_cost_by_activity

    def identify_rework_causes(self) -> pd.DataFrame:
        """
        Identifie les causes de rework basées sur les aléas
        """
        # Filtrer les événements avec rework et aléa
        rework_with_alea = self.event_log[
            (self.event_log['rework_flag']) & (self.event_log['alea'].notna())
        ].copy()

        if len(rework_with_alea) == 0:
            return pd.DataFrame(columns=['alea', 'count', 'activity'])

        # Compter les causes
        cause_counts = rework_with_alea.groupby(['alea', 'activity']).size().reset_index(name='count')
        cause_counts = cause_counts.sort_values('count', ascending=False)

        return cause_counts

    def calculate_rework_impact_on_leadtime(self) -> Dict:
        """
        Calcule l'impact des reworks sur le lead time
        """
        # Séparer les pièces avec et sans rework
        pieces_with_rework = self.event_log[self.event_log['rework_flag']]['case_id'].unique()

        # Lead time par pièce
        lead_times = self.event_log.groupby('case_id').agg({
            'timestamp_start': 'min',
            'timestamp_end': 'max'
        })
        lead_times['lead_time'] = (
            lead_times['timestamp_end'] - lead_times['timestamp_start']
        ).dt.total_seconds() / 3600

        # Séparer avec/sans rework
        with_rework = lead_times.loc[pieces_with_rework]['lead_time']
        without_rework = lead_times.loc[
            ~lead_times.index.isin(pieces_with_rework)
        ]['lead_time']

        impact = {
            'avg_leadtime_with_rework': with_rework.mean() if len(with_rework) > 0 else 0,
            'avg_leadtime_without_rework': without_rework.mean() if len(without_rework) > 0 else 0,
            'pieces_with_rework': len(pieces_with_rework),
            'pieces_without_rework': len(without_rework),
            'rework_rate_pct': (len(pieces_with_rework) / len(lead_times) * 100) if len(lead_times) > 0 else 0
        }

        # Calcul de l'augmentation
        if impact['avg_leadtime_without_rework'] > 0:
            impact['leadtime_increase_pct'] = (
                (impact['avg_leadtime_with_rework'] - impact['avg_leadtime_without_rework']) /
                impact['avg_leadtime_without_rework'] * 100
            )
        else:
            impact['leadtime_increase_pct'] = 0

        return impact

    def analyze_rework_patterns(self) -> pd.DataFrame:
        """
        Analyse les patterns de rework (quelles activités mènent à des reworks)
        """
        # Trier par case et timestamp
        df = self.event_log.sort_values(['case_id', 'timestamp_start']).copy()

        # Identifier l'activité précédente
        df['prev_activity'] = df.groupby('case_id')['activity'].shift(1)
        df['prev_result'] = df.groupby('case_id')['result'].shift(1)

        # Filtrer les événements de rework
        rework_events = df[df['rework_flag']]

        if len(rework_events) == 0:
            return pd.DataFrame(columns=['prev_activity', 'current_activity', 'count'])

        # Compter les patterns
        patterns = rework_events.groupby(['prev_activity', 'activity']).size().reset_index(name='count')
        patterns = patterns.sort_values('count', ascending=False)

        return patterns

    def calculate_first_pass_yield(self) -> pd.DataFrame:
        """
        Calcule le First Pass Yield (FPY) par activité
        FPY = % de pièces qui passent sans rework
        """
        # Exclure les activités de rework elles-mêmes
        main_activities = self.event_log[
            ~self.event_log['activity'].str.contains('_Rework', na=False)
        ].copy()

        fpy_stats = main_activities.groupby('activity').agg({
            'result': lambda x: (x == 'OK').sum(),
            'case_id': 'count'
        }).reset_index()

        fpy_stats.columns = ['activity', 'ok_count', 'total_count']

        fpy_stats['fpy_pct'] = (
            fpy_stats['ok_count'] / fpy_stats['total_count'] * 100
        ).round(2)

        fpy_stats = fpy_stats.sort_values('fpy_pct', ascending=True)

        return fpy_stats

    def get_rework_summary(self) -> Dict:
        """
        Résumé complet des reworks
        """
        rework_rate_by_activity = self.calculate_rework_rate_by_activity()
        rework_cost = self.calculate_rework_cost()
        rework_causes = self.identify_rework_causes()
        leadtime_impact = self.calculate_rework_impact_on_leadtime()
        fpy = self.calculate_first_pass_yield()

        # Statistiques globales
        total_events = len(self.event_log)
        total_rework = self.event_log['rework_flag'].sum()
        global_rework_rate = (total_rework / total_events * 100) if total_events > 0 else 0

        total_cost = rework_cost['total_cost_euros'].sum() if len(rework_cost) > 0 else 0

        summary = {
            'global_rework_rate_pct': global_rework_rate,
            'total_rework_events': int(total_rework),
            'total_rework_cost_euros': total_cost,
            'top_rework_activities': rework_rate_by_activity.head(3).to_dict('records'),
            'top_cost_activities': rework_cost.head(3).to_dict('records'),
            'leadtime_impact': leadtime_impact,
            'top_causes': rework_causes.head(5).to_dict('records') if len(rework_causes) > 0 else [],
            'worst_fpy_activities': fpy.head(3).to_dict('records')
        }

        return summary


print("✅ ReworkTracker class loaded")
