# 📋 RAPPORT FINAL - MANUFACTURING OPERATIONS RADAR

**Date**: 27/11/2025 13:51

**Projet**: Hackathon A5 DPM/PLM - Manufacturing Ops Radar

**Sujet**: Analyse et Optimisation des Opérations de Production Aéronautique

---

## 📊 EXECUTIVE SUMMARY

### Contexte et Périmètre

Ce rapport présente l'analyse complète d'une chaîne de production aéronautique composée de 8 opérations principales :

1. Assemblage queue avion
2. Assemblage aile droite
3. Assemblage aile gauche
4. Assemblage fuselage centrale
5. Assemblage train atterrissage gauche
6. Fixation réacteur aile gauche
7. Assemblage train atterrissage droit
8. Fixation réacteur aile droite

L'analyse porte sur **150 pièces** et **1298 événements** sur la période du 1er au 4 septembre 2023.

### Principaux Résultats

- **Lead Time moyen**: 1.02 heures
- **WIP moyen**: 0.01 pièces
- **Débit**: 47.9 pièces/jour
- **Taux de rework**: 15.1%
- **Flow Efficiency**: 0.0%

### Top 3 Recommandations

1. **Ajouter une ressource au poste 'Assemblage aile droite_Rework'**
   - Impact WIP: -15.1%
   - Impact Lead Time: -10.1%
   - Coût: 57,581€
   - ROI: 0.3x

2. **Ajouter une ressource au poste 'Assemblage aile droite'**
   - Impact WIP: -12.6%
   - Impact Lead Time: -8.4%
   - Coût: 43,695€
   - ROI: 0.1x

3. **Standardiser le contrôle qualité pour 'Assemblage queue avion'**
   - Impact WIP: -9.5%
   - Impact Lead Time: -7.4%
   - Coût: 19,638€
   - ROI: 4.0x

---

## 1. ANALYSE DE LA CHAÎNE DE PRODUCTION

### 1.1 Cartographie du Flux

La chaîne de production analysée comporte 8 opérations principales avec les caractéristiques suivantes :

| Opération | Nombre d'événements | Temps moyen (h) |
|-----------|---------------------|------------------|
| Assemblage aile droite | 150 | 0.00 |
| Assemblage aile gauche | 150 | 0.00 |
| Assemblage fuselage centrale | 150 | 0.00 |
| Assemblage queue avion | 150 | 0.00 |

### 1.2 Métriques Clés

**Lead Time**:
- Moyen: 1.02h
- La variabilité du lead time indique des opportunités d'amélioration

**Work In Progress (WIP)**:
- WIP moyen: 0.01 pièces
- Points d'accumulation identifiés: 8

**Débit de Production**:
- 47.9 pièces/jour
- Capacité théorique non atteinte en raison des goulots

---

## 2. ANALYSE DES GOULOTS D'ÉTRANGLEMENT

### 2.1 Identification des Goulots

L'analyse a identifié **16 goulots** dans la chaîne de production.

**Top 3 Goulots (par temps d'attente)**:

1. **Assemblage aile droite**
   - Temps d'attente moyen: 0.10h
   - Ratio attente/cycle: inf
   - Impact sur le temps total: 2.0%

2. **Assemblage aile droite_Rework**
   - Temps d'attente moyen: 0.50h
   - Ratio attente/cycle: inf
   - Impact sur le temps total: 10.4%

3. **Assemblage aile gauche**
   - Temps d'attente moyen: 0.10h
   - Ratio attente/cycle: inf
   - Impact sur le temps total: 2.1%

### 2.2 Causes des Goulots

Les principaux facteurs identifiés sont:

- **Sous-capacité**: Certaines stations n'ont pas assez de ressources
- **Variabilité élevée**: Temps de cycle non standardisés
- **Reworks**: Retours en arrière qui créent des files d'attente

---

## 3. ANALYSE DU REWORK

### 3.1 Taux de Rework Global

Le taux de rework global est de **15.1%**, ce qui représente un coût significatif.

**Top 3 Opérations avec le plus de Rework**:

1. **Assemblage queue avion**: 11.3% (17 sur 150)
2. **Assemblage aile gauche**: 10.7% (16 sur 150)
3. **Fixation réacteur aile droite**: 8.7% (13 sur 150)

### 3.2 Impact du Rework

Le rework a un impact majeur sur la performance:

- **Augmentation du lead time**: Les pièces nécessitant un rework ont un lead time 96.8% plus élevé
- **Réduction du débit**: Chaque rework bloque une station et réduit la capacité
- **Coût additionnel**: Main d'œuvre et matériel supplémentaires

---

## 4. RECOMMANDATIONS D'OPTIMISATION

### 4.1 Plan d'Action Priorisé

#### Action #1: Ajouter une ressource au poste 'Assemblage aile droite_Rework'

**Priorité**: HIGH

**Problème identifié**:
Goulot d'étranglement avec ratio attente/cycle de inf

**Solution proposée**:
Cette opération représente 10.4% du temps d'attente total. Le temps d'attente moyen est de 0.50h, soit infx le temps de cycle.

**Impact estimé**:
- ΔWIP: -15.1%
- ΔLead Time: -10.1%

**Investissement**:
- Coût: 57,581€
- ROI: 0.3x
- Payback: 43 mois

**Mise en œuvre**:
- Durée: 2-4 semaines

---

#### Action #2: Ajouter une ressource au poste 'Assemblage aile droite'

**Priorité**: HIGH

**Problème identifié**:
Goulot d'étranglement avec ratio attente/cycle de inf

**Solution proposée**:
Cette opération représente 2.0% du temps d'attente total. Le temps d'attente moyen est de 0.10h, soit infx le temps de cycle.

**Impact estimé**:
- ΔWIP: -12.6%
- ΔLead Time: -8.4%

**Investissement**:
- Coût: 43,695€
- ROI: 0.1x
- Payback: 167 mois

**Mise en œuvre**:
- Durée: 2-4 semaines

---

#### Action #3: Standardiser le contrôle qualité pour 'Assemblage queue avion'

**Priorité**: HIGH

**Problème identifié**:
Taux de rework élevé de 11.3%

**Solution proposée**:
Sur 150 opérations, 17 nécessitent un rework. Mise en place de procédures de contrôle en amont et formation des opérateurs.

**Impact estimé**:
- ΔWIP: -9.5%
- ΔLead Time: -7.4%

**Investissement**:
- Coût: 19,638€
- ROI: 4.0x
- Payback: 3 mois

**Mise en œuvre**:
- Durée: 4-6 semaines

---

## 5. KPIs DE SUCCÈS

### 5.1 Gains Attendus (Top 3 Actions)

| Métrique | Baseline | Optimisé | Gain |
|----------|----------|----------|------|
| Lead Time | 1.02h | 0.81h | 21.2% |
| WIP moyen | 0.01 | 0.01 | 30.8% |
| Débit | 1.994 p/h | 2.205 p/h | +10.6% |

### 5.2 ROI Global

- **Investissement total**: 120,914€
- **ROI global**: 4.3x
- **Gain estimé (ΔWIP)**: -30.8%
- **Gain estimé (ΔLead Time)**: -21.2%

---

## 6. ANNEXES

### 6.1 Méthodologie

L'analyse a été réalisée en utilisant les techniques suivantes:

- **Process Mining**: Découverte du flux réel à partir des event logs
- **Analyse statistique**: Calcul des temps de cycle, WIP, et lead times
- **Little's Law**: Validation de la cohérence WIP = Débit × Lead Time
- **Analyse de Pareto**: Identification des 20% de causes générant 80% des problèmes
- **Simulation**: Estimation de l'impact des actions d'amélioration

### 6.2 Données Utilisées

- **PLM_DataSet.xlsx**: 40 pièces avec références, coûts, et temps CAO
- **MES_Extraction.xlsx**: 56 enregistrements d'opérations réelles
- **ERP_Equipes_Airplus.xlsx**: 150 opérateurs avec compétences

### 6.3 Outils et Technologies

- **Python 3.11**: Langage principal
- **Pandas**: Manipulation et analyse de données
- **Plotly**: Visualisations interactives
- **Streamlit**: Dashboard web interactif
- **NetworkX**: Analyse de graphes pour le process map

---

## 📝 CONCLUSION

Cette analyse a permis d'identifier des opportunités significatives d'amélioration de la chaîne de production aéronautique. Les 3 actions prioritaires permettraient de réduire le WIP de 30.8% et le lead time de 21.2%, pour un investissement de 120,914€.

Les prochaines étapes recommandées sont:

1. **Court terme (1-2 mois)**: Implémenter l'action #1 (ajout de ressource)
2. **Moyen terme (3-6 mois)**: Déployer les améliorations qualité (actions #2 et #3)
3. **Long terme (6-12 mois)**: Optimiser l'ensemble du flux et monitorer les gains

---

*Rapport généré le 27/11/2025 à 13:51*
