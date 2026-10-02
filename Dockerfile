# Image officielle Python légère
FROM python:3.12-slim

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Empêche Python d'écrire des fichiers .pyc et active le mode unbuffered pour les logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copie et installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tout le code du projet
COPY . .

# Initialisation de la base SQLite avec les données de test
RUN python seed.py

# Exposition du port web
EXPOSE 8000

# Commande de démarrage du serveur
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
