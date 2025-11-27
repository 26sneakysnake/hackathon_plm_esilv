# 🐳 Guide Docker - Manufacturing Operations Radar

Ce guide explique comment utiliser Docker pour exécuter le Manufacturing Operations Radar sans problèmes de dépendances Python.

## 📋 Prérequis

- **Docker Desktop** installé sur votre machine
  - Windows : [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
  - Mac : [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
  - Linux : [Docker Engine](https://docs.docker.com/engine/install/)

## 🚀 Démarrage Rapide

### Option 1 : Docker Compose (Recommandé)

```powershell
# 1. Cloner le repo (si pas déjà fait)
git clone https://github.com/26sneakysnake/hackathon_plm_esilv.git
cd hackathon_plm_esilv

# 2. Checkout la bonne branche
git checkout claude/manufacturing-operations-radar-01K8Kmj34pfFm78u3v1gRv55

# 3. Lancer le dashboard
docker-compose up dashboard
```

Le dashboard sera accessible sur **http://localhost:8501**

### Option 2 : Docker seul

```powershell
# 1. Build l'image
docker build -t manufacturing-radar .

# 2. Lancer le dashboard
docker run -p 8501:8501 -v ${PWD}/data:/app/data -v ${PWD}/outputs:/app/outputs manufacturing-radar
```

## 📊 Exécuter les Analyses

### Avec Docker Compose

```powershell
# Exécuter toutes les analyses
docker-compose run --rm analyzer

# OU exécuter des étapes spécifiques
docker-compose run --rm analyzer python main.py --step analysis
```

### Avec Docker seul

```powershell
# Exécuter les analyses
docker run --rm -v ${PWD}/data:/app/data -v ${PWD}/outputs:/app/outputs manufacturing-radar python main.py

# Exécuter une étape spécifique
docker run --rm -v ${PWD}/data:/app/data -v ${PWD}/outputs:/app/outputs manufacturing-radar python main.py --step analysis
```

## 🛠️ Commandes Utiles

### Gestion des conteneurs

```powershell
# Voir les conteneurs en cours d'exécution
docker-compose ps

# Arrêter les conteneurs
docker-compose down

# Redémarrer les conteneurs
docker-compose restart

# Voir les logs
docker-compose logs -f dashboard
```

### Accéder au conteneur

```powershell
# Ouvrir un shell dans le conteneur
docker-compose exec dashboard bash

# OU avec Docker seul
docker exec -it manufacturing-radar-dashboard bash
```

### Nettoyer

```powershell
# Supprimer les conteneurs
docker-compose down

# Supprimer les conteneurs ET les images
docker-compose down --rmi all

# Nettoyer tout Docker (ATTENTION : supprime TOUTES les images)
docker system prune -a
```

## 📁 Structure des Volumes

Les dossiers suivants sont montés en volumes pour persister les données :

- `./data` → `/app/data` : Données brutes et event logs
- `./outputs` → `/app/outputs` : Rapports, visualisations, recommandations
- `./src` → `/app/src` : Code source (en dev mode)

## 🔧 Configuration

### Modifier le port du dashboard

Éditez `docker-compose.yml` :

```yaml
services:
  dashboard:
    ports:
      - "8080:8501"  # Utiliser le port 8080 au lieu de 8501
```

### Variables d'environnement

Créez un fichier `.env` :

```env
# Exemple de variables
STREAMLIT_SERVER_PORT=8501
PYTHONUNBUFFERED=1
```

Puis référencez-le dans `docker-compose.yml` :

```yaml
services:
  dashboard:
    env_file: .env
```

## 🐛 Troubleshooting

### Le dashboard ne démarre pas

```powershell
# Vérifier les logs
docker-compose logs dashboard

# Reconstruire l'image
docker-compose build --no-cache
docker-compose up dashboard
```

### Problèmes de permissions (Linux/Mac)

```bash
# Donner les permissions nécessaires
chmod -R 755 data outputs
```

### Port déjà utilisé

Si le port 8501 est déjà utilisé :

```powershell
# Option 1 : Arrêter le processus qui utilise le port
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Option 2 : Utiliser un autre port
docker run -p 8080:8501 manufacturing-radar
```

### Les données ne persistent pas

Vérifiez que les volumes sont bien montés :

```powershell
docker-compose config
```

## 📝 Workflow Complet

```powershell
# 1. Cloner et setup
git clone https://github.com/26sneakysnake/hackathon_plm_esilv.git
cd hackathon_plm_esilv
git checkout claude/manufacturing-operations-radar-01K8Kmj34pfFm78u3v1gRv55

# 2. Générer les données et analyses
docker-compose run --rm analyzer

# 3. Lancer le dashboard
docker-compose up -d dashboard

# 4. Accéder au dashboard
# Ouvrir http://localhost:8501 dans votre navigateur

# 5. Consulter les rapports
# Les fichiers sont dans ./outputs/reports/

# 6. Arrêter quand terminé
docker-compose down
```

## 🎯 Avantages de Docker

✅ **Pas de problèmes de dépendances** : Environnement Python isolé et contrôlé
✅ **Portabilité** : Fonctionne sur Windows, Mac, Linux
✅ **Reproductibilité** : Même environnement pour tout le monde
✅ **Facilité** : Un seul `docker-compose up` et ça marche
✅ **Isolation** : N'affecte pas votre environnement Python local

## 📚 Ressources

- [Documentation Docker](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Streamlit Docker Guide](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)

## 🆘 Support

En cas de problème :

1. Vérifier les logs : `docker-compose logs`
2. Reconstruire l'image : `docker-compose build --no-cache`
3. Nettoyer et redémarrer : `docker-compose down && docker-compose up`

---

**Bonne analyse ! 🚀**
