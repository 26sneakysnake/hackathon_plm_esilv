"""
Charts Generator pour Manufacturing Operations Radar
Génère toutes les visualisations avec Plotly
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
from typing import Dict, List, Tuple


class ChartsGenerator:
    """Générateur de graphiques pour le Manufacturing Ops Radar"""

    def __init__(self, event_log: pd.DataFrame):
        self.event_log = event_log.copy()
        self._prepare_data()

    def _prepare_data(self):
        """Prépare les données pour les visualisations"""
        if not pd.api.types.is_datetime64_any_dtype(self.event_log['timestamp_start']):
            self.event_log['timestamp_start'] = pd.to_datetime(self.event_log['timestamp_start'])
        if not pd.api.types.is_datetime64_any_dtype(self.event_log['timestamp_end']):
            self.event_log['timestamp_end'] = pd.to_datetime(self.event_log['timestamp_end'])

    def create_process_map(self) -> go.Figure:
        """
        Crée une carte du processus (Process Map) avec les flux
        """
        # Calculer les transitions entre activités
        df = self.event_log.sort_values(['case_id', 'timestamp_start']).copy()
        df['next_activity'] = df.groupby('case_id')['activity'].shift(-1)

        transitions = df.groupby(['activity', 'next_activity']).size().reset_index(name='flow')
        transitions = transitions[transitions['next_activity'].notna()]

        # Créer le graphe
        G = nx.DiGraph()

        # Ajouter les nœuds (activités)
        activities = pd.concat([transitions['activity'], transitions['next_activity']]).unique()
        for act in activities:
            G.add_node(act)

        # Ajouter les arcs (transitions)
        for _, row in transitions.iterrows():
            G.add_edge(row['activity'], row['next_activity'], weight=row['flow'])

        # Layout du graphe
        pos = nx.spring_layout(G, k=2, iterations=50)

        # Créer les traces Plotly
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            weight = G[edge[0]][edge[1]]['weight']

            edge_trace.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=weight/10, color='#888'),
                    hoverinfo='text',
                    text=f"{edge[0]} → {edge[1]}<br>Flux: {weight} pièces",
                    showlegend=False
                )
            )

        # Nœuds
        node_x = []
        node_y = []
        node_text = []
        node_size = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            # Compter le nombre de pièces passant par cette activité
            count = len(self.event_log[self.event_log['activity'] == node])
            node_text.append(f"{node}<br>Pièces: {count}")
            node_size.append(count / 5)  # Taille proportionnelle

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[n.split('<br>')[0] for n in node_text],
            hovertext=node_text,
            textposition="top center",
            marker=dict(
                size=node_size,
                color='#1f77b4',
                line=dict(width=2, color='white')
            ),
            showlegend=False
        )

        # Figure
        fig = go.Figure(data=edge_trace + [node_trace])

        fig.update_layout(
            title="Process Map - Flux de Production",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600
        )

        return fig

    def create_wip_heatmap(self, time_interval: str = '1H') -> go.Figure:
        """
        Crée une heatmap du WIP dans le temps
        """
        # Période d'observation
        start_time = self.event_log['timestamp_start'].min()
        end_time = self.event_log['timestamp_end'].max()

        # Créer une grille de temps
        time_range = pd.date_range(start=start_time, end=end_time, freq=time_interval)

        # Calculer le WIP par activité et timestamp
        activities = self.event_log['activity'].unique()
        wip_matrix = []

        for ts in time_range:
            wip_row = []
            for activity in activities:
                activity_events = self.event_log[self.event_log['activity'] == activity]
                in_progress = (
                    (activity_events['timestamp_start'] <= ts) &
                    (activity_events['timestamp_end'] >= ts)
                ).sum()
                wip_row.append(in_progress)
            wip_matrix.append(wip_row)

        # Créer la heatmap
        fig = go.Figure(data=go.Heatmap(
            z=wip_matrix,
            x=activities,
            y=time_range,
            colorscale='YlOrRd',
            colorbar=dict(title="WIP")
        ))

        fig.update_layout(
            title="WIP Heatmap - Work In Progress par Opération et Temps",
            xaxis_title="Opération",
            yaxis_title="Temps",
            height=600
        )

        fig.update_xaxes(tickangle=-45)

        return fig

    def create_pareto_chart(self, bottleneck_data: pd.DataFrame) -> go.Figure:
        """
        Crée un diagramme de Pareto des goulots d'étranglement
        """
        # Trier par impact
        data = bottleneck_data.sort_values('wait_time_impact_pct', ascending=False).head(10)

        # Calculer le cumul
        data['cumulative_pct'] = data['wait_time_impact_pct'].cumsum()

        # Créer la figure avec deux axes Y
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Barres (impact individuel)
        fig.add_trace(
            go.Bar(
                x=data['activity'],
                y=data['wait_time_impact_pct'],
                name="Impact (%)",
                marker_color='steelblue'
            ),
            secondary_y=False
        )

        # Courbe cumulative
        fig.add_trace(
            go.Scatter(
                x=data['activity'],
                y=data['cumulative_pct'],
                name="Cumul (%)",
                mode='lines+markers',
                marker=dict(color='red', size=8),
                line=dict(color='red', width=2)
            ),
            secondary_y=True
        )

        # Ligne 80%
        fig.add_hline(
            y=80,
            line_dash="dash",
            line_color="green",
            annotation_text="Seuil 80%",
            secondary_y=True
        )

        fig.update_xaxes(title_text="Opération", tickangle=-45)
        fig.update_yaxes(title_text="Impact (%)", secondary_y=False)
        fig.update_yaxes(title_text="Cumul (%)", secondary_y=True, range=[0, 100])

        fig.update_layout(
            title="Pareto des Goulots d'Étranglement",
            hovermode='x unified',
            height=600
        )

        return fig

    def create_gantt_chart(self, num_cases: int = 20) -> go.Figure:
        """
        Crée un diagramme de Gantt pour les premières pièces
        """
        # Sélectionner les premières pièces
        cases = self.event_log['case_id'].unique()[:num_cases]
        data = self.event_log[self.event_log['case_id'].isin(cases)].copy()

        # Créer le Gantt
        fig = px.timeline(
            data,
            x_start="timestamp_start",
            x_end="timestamp_end",
            y="case_id",
            color="activity",
            title=f"Gantt Chart - Timeline des {num_cases} Premières Pièces"
        )

        fig.update_yaxes(categoryorder='total ascending')
        fig.update_layout(height=600)

        return fig

    def create_cycle_time_boxplot(self) -> go.Figure:
        """
        Crée un boxplot des temps de cycle par opération
        """
        # Exclure les reworks pour la clarté
        main_activities = self.event_log[
            ~self.event_log['activity'].str.contains('_Rework', na=False)
        ].copy()

        fig = go.Figure()

        for activity in main_activities['activity'].unique():
            activity_data = main_activities[main_activities['activity'] == activity]

            fig.add_trace(go.Box(
                y=activity_data['wait_time'],
                name=activity,
                boxmean='sd'
            ))

        fig.update_layout(
            title="Distribution des Temps d'Attente par Opération",
            yaxis_title="Temps d'attente (heures)",
            showlegend=True,
            height=600
        )

        fig.update_xaxes(tickangle=-45)

        return fig

    def create_throughput_evolution(self, time_interval: str = '1H') -> go.Figure:
        """
        Crée un graphique de l'évolution du débit dans le temps
        """
        # Compter les pièces complètes par intervalle de temps
        df = self.event_log.groupby('case_id').agg({
            'timestamp_end': 'max'
        }).reset_index()

        df['completion_time'] = pd.to_datetime(df['timestamp_end'])
        df = df.set_index('completion_time')

        # Resampler par intervalle
        throughput = df.resample(time_interval).size().reset_index()
        throughput.columns = ['timestamp', 'completed_pieces']

        # Calculer le cumul
        throughput['cumulative'] = throughput['completed_pieces'].cumsum()

        # Figure avec deux axes
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Bar(
                x=throughput['timestamp'],
                y=throughput['completed_pieces'],
                name="Pièces/intervalle",
                marker_color='lightblue'
            ),
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=throughput['timestamp'],
                y=throughput['cumulative'],
                name="Cumul",
                mode='lines+markers',
                marker_color='darkblue'
            ),
            secondary_y=True
        )

        fig.update_xaxes(title_text="Temps")
        fig.update_yaxes(title_text="Pièces complètes", secondary_y=False)
        fig.update_yaxes(title_text="Cumul", secondary_y=True)

        fig.update_layout(
            title="Évolution du Débit de Production",
            hovermode='x unified',
            height=500
        )

        return fig

    def create_rework_sankey(self) -> go.Figure:
        """
        Crée un diagramme de Sankey pour les flux de rework
        """
        # Identifier les transitions vers rework
        df = self.event_log.sort_values(['case_id', 'timestamp_start']).copy()
        df['next_activity'] = df.groupby('case_id')['activity'].shift(-1)

        # Filtrer les transitions vers rework
        rework_transitions = df[
            (df['next_activity'].notna()) &
            (df['next_activity'].str.contains('_Rework', na=False))
        ].copy()

        if len(rework_transitions) == 0:
            # Pas de rework, créer une figure vide
            fig = go.Figure()
            fig.update_layout(
                title="Sankey Diagram - Flux de Rework",
                annotations=[{
                    'text': "Aucun flux de rework détecté",
                    'showarrow': False,
                    'xref': 'paper',
                    'yref': 'paper',
                    'x': 0.5,
                    'y': 0.5
                }]
            )
            return fig

        # Compter les transitions
        transitions = rework_transitions.groupby(['activity', 'next_activity']).size().reset_index(name='count')

        # Créer les listes pour Sankey
        all_nodes = list(set(transitions['activity'].tolist() + transitions['next_activity'].tolist()))
        node_dict = {node: idx for idx, node in enumerate(all_nodes)}

        sources = [node_dict[src] for src in transitions['activity']]
        targets = [node_dict[tgt] for tgt in transitions['next_activity']]
        values = transitions['count'].tolist()

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_nodes
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values
            )
        )])

        fig.update_layout(
            title="Sankey Diagram - Flux de Rework",
            height=600
        )

        return fig

    def create_kpi_dashboard(self, kpis: Dict) -> go.Figure:
        """
        Crée un dashboard de KPIs
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Lead Time Moyen",
                "WIP Moyen",
                "Taux de Rework",
                "Flow Efficiency"
            ),
            specs=[
                [{"type": "indicator"}, {"type": "indicator"}],
                [{"type": "indicator"}, {"type": "indicator"}]
            ]
        )

        # Lead Time
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=kpis.get('lead_time_moyen_h', 0),
            title={'text': "Lead Time (h)"},
            delta={'reference': 1.0},
            gauge={'axis': {'range': [None, 3]},
                   'bar': {'color': "darkblue"},
                   'threshold': {
                       'line': {'color': "red", 'width': 4},
                       'thickness': 0.75,
                       'value': 1.5
                   }}
        ), row=1, col=1)

        # WIP
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=kpis.get('wip_moyen', 0),
            title={'text': "WIP Moyen"},
            gauge={'axis': {'range': [None, 5]},
                   'bar': {'color': "steelblue"}}
        ), row=1, col=2)

        # Taux de Rework
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=kpis.get('taux_rework_pct', 0),
            title={'text': "Taux Rework (%)"},
            delta={'reference': 10, 'decreasing': {'color': "green"}},
            gauge={'axis': {'range': [None, 30]},
                   'bar': {'color': "orange"},
                   'threshold': {
                       'line': {'color': "red", 'width': 4},
                       'thickness': 0.75,
                       'value': 20
                   }}
        ), row=2, col=1)

        # Flow Efficiency
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=kpis.get('flow_efficiency_pct', 0),
            title={'text': "Flow Efficiency (%)"},
            delta={'reference': 50},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "green"}}
        ), row=2, col=2)

        fig.update_layout(
            title="Dashboard KPIs - Manufacturing Operations",
            height=600
        )

        return fig


print("✅ ChartsGenerator class loaded")
