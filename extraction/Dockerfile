# Utilisez une image de base appropriée contenant Python
FROM python:3.8-slim-buster

# Définissez le répertoire de travail dans le conteneur
WORKDIR /extraction

# Copiez tous les fichiers dans le conteneur
COPY . /extraction

# Installation des dépendances
RUN pip install -r requirements.txt

# Définir le script make_all.sh comme exécutable
RUN chmod +x /extraction/make_all.sh

# Définir la commande à exécuter lorsque le conteneur démarre
CMD [ "bash" ]