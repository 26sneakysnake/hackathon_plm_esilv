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

### 🐳 Méthode Recommandée : Docker (Aucun problème de dépendances)

```bash
# Cloner le repo
git clone https://github.com/26sneakysnake/hackathon_plm_esilv.git
cd hackathon_plm_esilv
git checkout claude/manufacturing-operations-radar-01K8Kmj34pfFm78u3v1gRv55

# Lancer le dashboard avec Docker
docker-compose up dashboard

# Accéder au dashboard sur http://localhost:8501
```

📖 **Guide complet Docker** : Voir [DOCKER.md](DOCKER.md)

### 💻 Méthode Alternative : Installation Locale (Python 3.11 requis)

⚠️ **Attention** : Nécessite Python 3.11 (pas 3.13) pour éviter les problèmes de compilation

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

# OU tout exécuter d'un coup
python main.py
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

## 🧪 Tests et Validation

Suite complète de tests pour garantir la qualité et la fiabilité.

### Exécuter les tests

```bash
# Avec Docker (recommandé)
docker-compose run --rm tests

# Avec Python local
python tests/run_all_tests.py

# Tests spécifiques
pytest tests/test_data_loader.py -v
pytest tests/test_analysis.py -v
```

### Couverture des tests

- ✅ **Test du chargement des données** : Validation des 3 fichiers Excel
- ✅ **Test de l'event log** : Génération et cohérence de 1298 événements
- ✅ **Test des analyses** : ProcessMining, Bottlenecks, WIP, Rework
- ✅ **Test d'intégration** : Workflow complet end-to-end
- ✅ **Test des KPIs** : Validation de tous les indicateurs
- ✅ **Test des outputs** : Rapports et visualisations

📖 **Documentation complète** : Voir [tests/README_TESTS.md](tests/README_TESTS.md)

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
