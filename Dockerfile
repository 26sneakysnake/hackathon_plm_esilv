# Manufacturing Operations Radar - Dockerfile
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Manufacturing Ops Radar"
LABEL description="Hackathon A5 DPM/PLM - Manufacturing Operations Analytics"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Répertoire de travail
WORKDIR /app

# Copier requirements d'abord (pour cache Docker)
COPY requirements.txt .

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p data/raw data/event_logs outputs/reports outputs/visualizations outputs/recommendations

# Exposer le port pour Streamlit
EXPOSE 8501

# Commande par défaut : lancer le dashboard
CMD ["streamlit", "run", "src/visualization/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
