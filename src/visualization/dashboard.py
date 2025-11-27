"""
Dashboard Streamlit pour Manufacturing Operations Radar
Interface interactive pour visualiser les analyses et recommandations
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from visualization.charts import ChartsGenerator
from analysis.process_mining import ProcessMiner
from analysis.bottleneck_detector import BottleneckDetector
from analysis.wip_analyzer import WIPAnalyzer
from analysis.rework_tracker import ReworkTracker


# Configuration de la page
st.set_page_config(
    page_title="Manufacturing Operations Radar",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .recommendation-card {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 6px solid #ff7f0e;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Charge toutes les données nécessaires"""
    event_log = pd.read_csv("data/event_logs/manufacturing_event_log.csv")

    with open("outputs/reports/kpis_summary.json", "r") as f:
        kpis = json.load(f)

    with open("outputs/recommendations/recommendations.json", "r") as f:
        recommendations = json.load(f)

    with open("outputs/recommendations/optimization_impact.json", "r") as f:
        impact = json.load(f)

    return event_log, kpis, recommendations, impact


@st.cache_resource
def get_analyzers(event_log):
    """Crée les analyseurs"""
    pm = ProcessMiner(event_log)
    bd = BottleneckDetector(event_log)
    wip = WIPAnalyzer(event_log)
    rt = ReworkTracker(event_log)
    charts = ChartsGenerator(event_log)

    return pm, bd, wip, rt, charts


def main():
    """Application principale"""

    # Header
    st.markdown('<h1 class="main-header">🏭 Manufacturing Operations Radar</h1>', unsafe_allow_html=True)
    st.markdown("### 📊 Analyse et Optimisation de la Chaîne de Production Aéronautique")
    st.markdown("---")

    # Charger les données
    try:
        event_log, kpis, recommendations, impact = load_data()
        pm, bd, wip, rt, charts = get_analyzers(event_log)
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {str(e)}")
        st.info("💡 Assurez-vous d'avoir exécuté les analyses avant de lancer le dashboard.")
        return

    # Sidebar
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.radio(
        "Choisir une vue:",
        ["📊 Vue d'ensemble", "🔍 Analyse des goulots", "📦 Analyse WIP",
         "🔄 Analyse Rework", "💡 Recommandations", "🎨 Visualisations"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 KPIs Rapides")
    st.sidebar.metric("Lead Time", f"{kpis['lead_time_moyen_h']:.2f}h")
    st.sidebar.metric("WIP Moyen", f"{kpis['wip_moyen']:.2f}")
    st.sidebar.metric("Taux Rework", f"{kpis['taux_rework_pct']:.1f}%")

    # Pages
    if page == "📊 Vue d'ensemble":
        show_overview(event_log, kpis, pm, charts)

    elif page == "🔍 Analyse des goulots":
        show_bottleneck_analysis(event_log, bd, charts)

    elif page == "📦 Analyse WIP":
        show_wip_analysis(event_log, wip, charts)

    elif page == "🔄 Analyse Rework":
        show_rework_analysis(event_log, rt, charts)

    elif page == "💡 Recommandations":
        show_recommendations(recommendations, impact)

    elif page == "🎨 Visualisations":
        show_visualizations(charts)


def show_overview(event_log, kpis, pm, charts):
    """Page Vue d'ensemble"""
    st.header("📊 Vue d'Ensemble de la Production")

    # KPIs en haut
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Lead Time Moyen",
            f"{kpis['lead_time_moyen_h']:.2f}h",
            help="Temps total de passage d'une pièce dans la chaîne"
        )

    with col2:
        st.metric(
            "WIP Moyen",
            f"{kpis['wip_moyen']:.2f}",
            help="Nombre moyen de pièces en cours de production"
        )

    with col3:
        st.metric(
            "Débit",
            f"{kpis['throughput_pieces_par_jour']:.1f}/jour",
            help="Nombre de pièces produites par jour"
        )

    with col4:
        st.metric(
            "Taux de Rework",
            f"{kpis['taux_rework_pct']:.1f}%",
            delta=f"-{100-kpis['taux_rework_pct']:.0f}% de l'objectif (0%)",
            delta_color="inverse",
            help="Pourcentage d'opérations nécessitant un rework"
        )

    st.markdown("---")

    # Statistiques générales
    overview = pm.get_process_overview()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Statistiques Générales")
        st.write(f"**Nombre de pièces analysées:** {overview['nombre_pieces']}")
        st.write(f"**Nombre d'opérations:** {overview['nombre_operations']}")
        st.write(f"**Nombre total d'événements:** {overview['nombre_evenements']}")
        st.write(f"**Période analysée:** {overview['periode_debut']} → {overview['periode_fin']}")

    with col2:
        st.subheader("⏱️ Performance Temporelle")
        st.write(f"**Lead time min/max:** {overview['lead_time_min']:.2f}h / {overview['lead_time_max']:.2f}h")
        st.write(f"**Écart-type lead time:** {overview['lead_time_std']:.2f}h")
        st.write(f"**Débit:** {overview['throughput']:.3f} pièces/heure")

    st.markdown("---")

    # Process Map
    st.subheader("🗺️ Carte du Processus")
    fig_process = charts.create_process_map()
    st.plotly_chart(fig_process, use_container_width=True)

    # Gantt Chart
    st.subheader("📅 Timeline de Production (20 premières pièces)")
    fig_gantt = charts.create_gantt_chart(num_cases=20)
    st.plotly_chart(fig_gantt, use_container_width=True)


def show_bottleneck_analysis(event_log, bd, charts):
    """Page Analyse des goulots"""
    st.header("🔍 Analyse des Goulots d'Étranglement")

    # Détection des goulots
    bottlenecks_wait = bd.detect_bottlenecks_by_wait_time()
    bottlenecks_wip = bd.detect_bottlenecks_by_wip()

    # Pareto
    st.subheader("📊 Pareto des Goulots (par temps d'attente)")
    fig_pareto = charts.create_pareto_chart(bottlenecks_wait)
    st.plotly_chart(fig_pareto, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⏱️ Top Goulots par Temps d'Attente")
        top_wait = bottlenecks_wait.head(5)[['activity', 'wait_time_mean', 'cycle_time_mean', 'wait_to_cycle_ratio']]
        st.dataframe(top_wait, use_container_width=True)

    with col2:
        st.subheader("📦 Top Goulots par WIP")
        top_wip = bottlenecks_wip.head(5)[['activity', 'wip_mean', 'wip_max']]
        st.dataframe(top_wip, use_container_width=True)

    # Boxplot
    st.subheader("📦 Distribution des Temps d'Attente")
    fig_boxplot = charts.create_cycle_time_boxplot()
    st.plotly_chart(fig_boxplot, use_container_width=True)


def show_wip_analysis(event_log, wip, charts):
    """Page Analyse WIP"""
    st.header("📦 Analyse du WIP (Work In Progress)")

    # WIP par activité
    wip_by_activity = wip.calculate_wip_by_activity()

    st.subheader("📊 WIP Moyen par Activité")
    st.dataframe(wip_by_activity[['activity', 'wip_mean', 'wip_max', 'wip_std']],
                 use_container_width=True)

    # Heatmap
    st.subheader("🔥 Heatmap du WIP dans le Temps")
    fig_heatmap = charts.create_wip_heatmap(time_interval='2H')
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Métriques
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Profil d'Inventaire (Little's Law)")
        inventory = wip.calculate_inventory_profile()
        st.metric("WIP Théorique", f"{inventory['theoretical_wip']:.2f}")
        st.metric("WIP Réel Moyen", f"{inventory['actual_wip']:.2f}")
        st.metric("Efficacité WIP", f"{inventory['wip_efficiency']:.1f}%")

    with col2:
        st.subheader("⚡ Efficacité du Flux")
        flow_eff = wip.calculate_flow_efficiency()
        st.metric("Flow Efficiency", f"{flow_eff['avg_flow_efficiency']:.1f}%")
        st.metric("Temps à Valeur Ajoutée", f"{flow_eff['avg_value_adding_time']:.2f}h")
        st.metric("Temps de Gaspillage", f"{flow_eff['avg_waste_time']:.2f}h")


def show_rework_analysis(event_log, rt, charts):
    """Page Analyse Rework"""
    st.header("🔄 Analyse des Reworks")

    # Taux de rework
    rework_rate = rt.calculate_rework_rate_by_activity()

    st.subheader("📊 Taux de Rework par Activité")
    st.dataframe(rework_rate, use_container_width=True)

    # Sankey
    st.subheader("🌊 Flux de Rework (Sankey Diagram)")
    fig_sankey = charts.create_rework_sankey()
    st.plotly_chart(fig_sankey, use_container_width=True)

    # Impact sur lead time
    st.subheader("⏱️ Impact des Reworks sur le Lead Time")
    impact = rt.calculate_rework_impact_on_leadtime()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lead Time avec Rework", f"{impact['avg_leadtime_with_rework']:.2f}h")
    with col2:
        st.metric("Lead Time sans Rework", f"{impact['avg_leadtime_without_rework']:.2f}h")
    with col3:
        st.metric("Augmentation", f"+{impact['leadtime_increase_pct']:.1f}%",
                 delta_color="inverse")

    # FPY
    st.subheader("✅ First Pass Yield (FPY)")
    fpy = rt.calculate_first_pass_yield()
    st.dataframe(fpy, use_container_width=True)


def show_recommendations(recommendations, impact):
    """Page Recommandations"""
    st.header("💡 Recommandations d'Optimisation")

    st.info("""
    **Note**: Ces recommandations sont basées sur l'analyse des données et proposent
    des actions concrètes pour optimiser la chaîne de production.
    """)

    # Impact global
    st.subheader("📊 Impact Global des Top 3 Actions")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("ΔWIP", f"-{impact['delta']['wip_reduction_pct']:.1f}%")
    with col2:
        st.metric("ΔLead Time", f"-{impact['delta']['leadtime_reduction_pct']:.1f}%")
    with col3:
        st.metric("Investissement", f"{impact['delta']['total_investment_euros']:,.0f}€")
    with col4:
        st.metric("ROI Global", f"{impact['roi_global']:.1f}x")

    st.markdown("---")

    # Top 3 Recommandations
    st.subheader("🎯 Top 3 Actions Prioritaires")

    for i, rec in enumerate(recommendations[:3], 1):
        with st.container():
            st.markdown(f"""
            <div class="recommendation-card">
                <h3>🎯 Recommandation #{i} [{rec['priority']}]</h3>
                <h4>{rec['action']}</h4>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Problème identifié:** {rec['problem']}")
                st.write(f"**Détails:** {rec['details']}")
                st.write(f"**Durée d'implémentation:** {rec['implementation_time']}")

            with col2:
                st.metric("Impact WIP", f"-{rec['estimated_wip_reduction_pct']:.1f}%")
                st.metric("Impact Lead Time", f"-{rec['estimated_leadtime_reduction_pct']:.1f}%")
                st.metric("Coût", f"{rec['estimated_cost_euros']:,.0f}€")
                st.metric("ROI", f"{rec['roi']:.1f}x")
                st.metric("Payback", f"{rec['payback_months']:.0f} mois")

            st.markdown("---")

    # Toutes les recommandations
    with st.expander("📋 Voir toutes les recommandations"):
        for rec in recommendations:
            st.write(f"**#{rec['rank']} - {rec['action']}**")
            st.write(f"  - Priorité: {rec['priority']}")
            st.write(f"  - Impact WIP: -{rec['estimated_wip_reduction_pct']:.1f}%")
            st.write(f"  - Coût: {rec['estimated_cost_euros']:,.0f}€")
            st.write("")


def show_visualizations(charts):
    """Page Visualisations"""
    st.header("🎨 Visualisations Avancées")

    viz_type = st.selectbox(
        "Choisir une visualisation:",
        ["Process Map", "WIP Heatmap", "Pareto des Goulots", "Gantt Chart",
         "Cycle Time Boxplot", "Évolution du Débit", "Flux de Rework", "Dashboard KPIs"]
    )

    if viz_type == "Process Map":
        fig = charts.create_process_map()
    elif viz_type == "WIP Heatmap":
        fig = charts.create_wip_heatmap(time_interval='2H')
    elif viz_type == "Gantt Chart":
        fig = charts.create_gantt_chart(num_cases=20)
    elif viz_type == "Cycle Time Boxplot":
        fig = charts.create_cycle_time_boxplot()
    elif viz_type == "Évolution du Débit":
        fig = charts.create_throughput_evolution(time_interval='2H')
    elif viz_type == "Flux de Rework":
        fig = charts.create_rework_sankey()
    else:
        st.info("Chargement du dashboard KPIs...")
        return

    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
