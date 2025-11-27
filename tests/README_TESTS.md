# 🧪 Suite de Tests - Manufacturing Operations Radar

Documentation complète de la suite de tests de validation.

## 📋 Vue d'Ensemble

Cette suite de tests garantit que :
- ✅ Les données Excel sont correctement chargées et exploitées
- ✅ L'event log est généré de manière cohérente
- ✅ Toutes les analyses produisent des résultats valides
- ✅ Le workflow complet fonctionne end-to-end
- ✅ Les KPIs sont correctement calculés
- ✅ Les recommandations sont pertinentes

## 📁 Structure des Tests

```
tests/
├── __init__.py
├── README_TESTS.md                 # Ce fichier
├── test_data_loader.py             # Tests du chargement des données
├── test_event_log_builder.py       # Tests de génération de l'event log
├── test_analysis.py                # Tests des modules d'analyse
├── test_integration.py             # Tests d'intégration end-to-end
└── run_all_tests.py                # Script principal
```

## 🚀 Exécution des Tests

### Option 1 : Tous les tests (Recommandé)

```bash
# Avec Python
python tests/run_all_tests.py

# Avec Docker
docker-compose run --rm analyzer python tests/run_all_tests.py
```

### Option 2 : Suite spécifique

```bash
# Tests du data loader uniquement
pytest tests/test_data_loader.py -v

# Tests de l'event log uniquement
pytest tests/test_event_log_builder.py -v

# Tests d'analyse uniquement
pytest tests/test_analysis.py -v

# Tests d'intégration uniquement
pytest tests/test_integration.py -v
```

### Option 3 : Test individuel

```bash
# Exécuter un test spécifique
pytest tests/test_data_loader.py::TestDataLoader::test_plm_structure -v

# Avec sortie détaillée
pytest tests/test_data_loader.py::TestDataLoader::test_plm_structure -v -s
```

## 📊 Suites de Tests Détaillées

### 1. test_data_loader.py

Valide le chargement et la structure des données Excel.

**Tests inclus** :
- ✅ `test_files_exist` : Vérifie que les fichiers Excel existent
- ✅ `test_load_all_data` : Vérifie que toutes les données sont chargées
- ✅ `test_plm_structure` : Valide la structure du PLM (40 pièces, colonnes requises)
- ✅ `test_mes_structure` : Valide la structure du MES (56 enregistrements)
- ✅ `test_erp_structure` : Valide la structure de l'ERP (150 opérateurs)
- ✅ `test_mes_operations` : Vérifie les opérations du MES (20+ opérations)
- ✅ `test_erp_qualifications` : Vérifie les qualifications ERP (10+ types)
- ✅ `test_data_consistency` : Vérifie la cohérence entre sources

**Couverture** :
- Chargement des 3 fichiers Excel
- Validation de toutes les colonnes essentielles
- Vérification des types de données
- Cohérence inter-fichiers

### 2. test_event_log_builder.py

Valide la génération de l'event log à partir des données sources.

**Tests inclus** :
- ✅ `test_operation_sequence` : Vérifie la séquence d'opérations (4-8 ops)
- ✅ `test_operation_stats` : Valide les statistiques par opération
- ✅ `test_generate_event_log` : Vérifie la génération complète
- ✅ `test_event_log_structure` : Valide la structure de l'event log
- ✅ `test_event_log_completeness` : Vérifie que toutes les pièces passent par toutes les ops
- ✅ `test_rework_logic` : Valide la logique de rework (5-25%)
- ✅ `test_resource_assignment` : Vérifie l'assignation des ressources
- ✅ `test_time_consistency` : Vérifie la cohérence temporelle
- ✅ `test_data_from_sources` : Vérifie que les données viennent bien des sources

**Couverture** :
- Génération de l'event log avec 150 pièces
- Validation de toutes les colonnes (16 colonnes)
- Cohérence des timestamps
- Traçabilité vers les sources (PLM, MES, ERP)

### 3. test_analysis.py

Valide tous les modules d'analyse.

**Tests inclus** :

**ProcessMining** :
- ✅ `test_process_overview` : Vérifie la vue d'ensemble
- ✅ `test_lead_times` : Valide les calculs de lead time
- ✅ `test_cycle_times` : Vérifie les temps de cycle

**BottleneckDetector** :
- ✅ `test_detect_bottlenecks_by_wait_time` : Détection par temps d'attente
- ✅ `test_detect_bottlenecks_by_wip` : Détection par WIP
- ✅ `test_bottleneck_impact` : Calcul de l'impact

**WIPAnalyzer** :
- ✅ `test_wip_by_activity` : Calcul du WIP par activité
- ✅ `test_inventory_profile` : Validation de Little's Law
- ✅ `test_flow_efficiency` : Calcul de l'efficacité du flux

**ReworkTracker** :
- ✅ `test_rework_rate_by_activity` : Taux de rework par opération
- ✅ `test_rework_impact_on_leadtime` : Impact sur le lead time
- ✅ `test_first_pass_yield` : Calcul du FPY
- ✅ `test_rework_summary` : Résumé complet

**Couverture** :
- 4 modules d'analyse validés
- Tous les KPIs clés vérifiés
- Cohérence mathématique

### 4. test_integration.py

Tests d'intégration end-to-end.

**Tests inclus** :
- ✅ `test_complete_workflow` : Workflow complet de bout en bout
- ✅ `test_data_consistency_through_pipeline` : Cohérence des données
- ✅ `test_kpis_calculation` : Calcul de tous les KPIs
- ✅ `test_output_files_generation` : Génération des fichiers de sortie
- ✅ `test_visualizations_generation` : Génération des visualisations
- ✅ `test_recommendations_quality` : Qualité des recommandations

**Couverture** :
- Pipeline complet : données → analyses → optimisation → rapports
- Validation de tous les outputs
- Cohérence globale du système

## 📈 Résultats Attendus

### KPIs Validés

| KPI | Valeur Attendue | Validation |
|-----|----------------|------------|
| **Nombre de pièces** | 150 | Exact |
| **Nombre d'opérations** | 8-16 | ≥ 4 |
| **Lead time moyen** | 0.5-3h | > 0 |
| **Taux de rework** | 5-25% | Entre 0-100% |
| **Nombre de goulots** | 3-10 | > 0 |
| **WIP moyen** | 0.01-5 | > 0 |
| **Flow efficiency** | 0-50% | 0-100% |

### Fichiers Validés

**Rapports** :
- ✅ `outputs/reports/kpis_summary.json`
- ✅ `outputs/reports/bottlenecks_wait_time.csv`
- ✅ `outputs/reports/wip_by_activity.csv`
- ✅ `outputs/reports/rework_rate.csv`
- ✅ `outputs/reports/RAPPORT_FINAL.md`

**Recommandations** :
- ✅ `outputs/recommendations/recommendations.json`
- ✅ `outputs/recommendations/recommendations.md`
- ✅ `outputs/recommendations/optimization_impact.json`

**Visualisations** :
- ✅ `outputs/visualizations/process_map.html`
- ✅ `outputs/visualizations/wip_heatmap.html`
- ✅ `outputs/visualizations/pareto_bottlenecks.html`
- ✅ `outputs/visualizations/gantt_chart.html`
- ✅ Et 4 autres...

## 🔍 Interprétation des Résultats

### Succès Complet (100%)

```
✅ TOUS LES TESTS SONT PASSÉS - SYSTÈME VALIDÉ
```

Tous les modules fonctionnent correctement. Le système est prêt pour la production.

### Succès Partiel (>80%)

```
⚠️ CERTAINS TESTS ONT ÉCHOUÉ - VÉRIFIER LES DÉTAILS
```

La plupart des fonctionnalités marchent, mais certaines nécessitent une attention. Consulter les logs détaillés.

### Échec (<80%)

```
❌ PLUSIEURS TESTS ONT ÉCHOUÉ - CORRECTION NÉCESSAIRE
```

Problèmes majeurs détectés. Vérifier les logs et corriger avant de continuer.

## 🐛 Debugging

### Test échoue : "Fichiers manquants"

```bash
# Vérifier que les fichiers Excel sont présents
ls -la data/raw/

# Copier les fichiers si nécessaire
cp path/to/PLM_DataSet.xlsx data/raw/
cp path/to/MES_Extraction.xlsx data/raw/
cp path/to/ERP_Equipes\ Airplus.xlsx data/raw/
```

### Test échoue : "Event log non trouvé"

```bash
# Générer l'event log
python src/data_processing/event_log_builder.py
```

### Test échoue : "Fichiers de sortie manquants"

```bash
# Exécuter toutes les analyses
python main.py
```

### Voir les logs détaillés

```bash
# Exécuter avec verbosité maximale
pytest tests/test_integration.py -v -s --tb=long
```

## 📊 Rapport de Test

Après chaque exécution, un rapport est généré :

**Emplacement** : `outputs/reports/test_report.txt`

**Contenu** :
- Date et heure d'exécution
- Résultats par suite de tests
- Résumé global
- Taux de réussite

## 🔧 Configuration

### Variables d'Environnement

```bash
# Définir le niveau de log pour pytest
export PYTEST_LOG_LEVEL=INFO

# Définir le mode de sortie
export PYTEST_VERBOSE=1
```

### Options Pytest

```bash
# Arrêter au premier échec
pytest -x

# Exécuter en parallèle (nécessite pytest-xdist)
pytest -n auto

# Générer un rapport de couverture
pytest --cov=src --cov-report=html
```

## 📝 Ajouter de Nouveaux Tests

### Template de Test

```python
import pytest

class TestMyFeature:
    """Tests pour ma nouvelle fonctionnalité"""

    @pytest.fixture
    def setup(self):
        """Setup pour les tests"""
        # Initialisation
        return data

    def test_my_functionality(self, setup):
        """Test de ma fonctionnalité"""
        # Arrange
        expected = ...

        # Act
        result = my_function()

        # Assert
        assert result == expected, "Message d'erreur"
```

### Conventions

- ✅ Utiliser des noms de tests descriptifs
- ✅ Un test = une assertion principale
- ✅ Utiliser des fixtures pour le setup
- ✅ Ajouter des messages d'erreur clairs
- ✅ Tester les cas limites

## 🚀 CI/CD

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          python tests/run_all_tests.py
```

### Docker

```bash
# Exécuter les tests dans Docker
docker-compose run --rm analyzer python tests/run_all_tests.py
```

## 📚 Ressources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)

---

**Dernière mise à jour** : 27 novembre 2025

**Mainteneur** : Manufacturing Operations Radar Team
