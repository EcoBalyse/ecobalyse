# Utilisez une image de base appropriée contenant Python
FROM python:3.8-slim-buster

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

COPY requirements.txt /app/requirements.txt

# Installation des dépendances
RUN pip install -r requirements.txt

# Copiez tous les fichiers dans le conteneur
COPY api/ /app

# Exposer le port sur lequel l'API FastAPI sera disponible
EXPOSE 8000

# Définir la commande à exécuter lorsque le conteneur démarre
CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8000", "--reload"]
