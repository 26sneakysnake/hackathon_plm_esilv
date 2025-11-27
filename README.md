# 🏭 Manufacturing Operations Radar

**Hackathon A5 DPM/PLM - Manufacturing Ops Radar**

Système d'analyse et d'optimisation des opérations de production pour l'industrie aéronautique.

## 🎯 Objectif

Analyser une chaîne de production de 8 opérations pour :
- Identifier les goulots d'étranglement
- Analyser le WIP (Work In Progress)
- Tracer les reworks
- Générer des recommandations d'optimisation

## 📊 Résultats Clés

- **ΔWIP**: -30.8%
- **ΔLead Time**: -21.2%
- **ROI**: 4.3x
- **Investissement**: 120,914€

## 🚀 Quick Start

```bash
# Installer les dépendances
pip install -r requirements.txt

# Générer l'event log
python src/data_processing/event_log_builder.py

# Exécuter les analyses
python src/analysis/analyze_all.py

# Générer les visualisations
python src/visualization/generate_all_charts.py

# Lancer l'optimisation
python src/optimization/run_optimization.py

# Lancer le dashboard
streamlit run src/visualization/dashboard.py
```

## 📁 Structure du Projet

```
manufacturing-radar/
├── data/
│   ├── raw/              # Données brutes (Excel)
│   └── event_logs/       # Event logs générés
├── src/
│   ├── data_processing/  # Chargement et génération données
│   ├── analysis/         # Analyses (process mining, bottlenecks, WIP, rework)
│   ├── optimization/     # Moteur d'optimisation
│   └── visualization/    # Visualisations et dashboard
├── outputs/
│   ├── reports/          # Rapports et KPIs
│   ├── visualizations/   # Graphiques HTML
│   └── recommendations/  # Recommandations
└── README.md
```

## 📈 Visualisations Disponibles

- **Process Map**: Carte du flux de production
- **WIP Heatmap**: Évolution du WIP dans le temps
- **Pareto Chart**: Goulots d'étranglement
- **Gantt Chart**: Timeline des opérations
- **Sankey Diagram**: Flux de rework
- **KPI Dashboard**: Tableau de bord interactif

## 📋 Rapports

- [Rapport Final Complet](outputs/reports/RAPPORT_FINAL.md)
- [Recommandations](outputs/recommendations/recommendations.md)
- [KPIs Summary](outputs/reports/kpis_summary.json)

## 🛠️ Technologies

- Python 3.11
- Pandas, NumPy
- Plotly (visualisations)
- Streamlit (dashboard)
- NetworkX (process mining)

## 👥 Auteur

Projet développé pour le Hackathon A5 DPM/PLM (26-28 novembre 2025)
