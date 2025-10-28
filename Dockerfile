FROM python:3.11-slim

# Métadonnées
LABEL maintainer="DNA-Sec Project"
LABEL description="DNA-Sec - Malware detection in DNA sequences"
LABEL version="0.1.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=web/app_demo.py
ENV FLASK_ENV=production

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système (gcc pour BioPython, optionnel pour YARA)
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY dna_sec/ ./dna_sec/
COPY web/ ./web/
COPY examples/ ./examples/
COPY setup.py .
COPY README.md ./README.md

# Installer le package DNA-Sec
RUN pip install -e .

# Créer le dossier uploads
RUN mkdir -p web/uploads

# Exposer le port
EXPOSE 5000

# Santé du container
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 dna-sec && \
    chown -R dna-sec:dna-sec /app
USER dna-sec

# Commande de démarrage
CMD ["python", "web/app_demo.py"]
