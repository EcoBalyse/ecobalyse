# Utilisez une image de base appropriée contenant Python
FROM python:3.8-slim-buster

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez tous les fichiers dans le conteneur
COPY . /app

# Installation des dépendances
RUN pip install -r requirements.txt

# Créer les répertoires nécessaires
RUN mkdir -p /json

# Définir la commande à exécuter lorsque le conteneur démarre
CMD [ "bash" ]