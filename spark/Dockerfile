# Utiliser l'image officielle de Python comme image de base
FROM python:3.8-slim-buster

# Mettre à jour les paquets et installer les dépendances
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    openjdk-11-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

# Définir les variables d'environnement pour Spark et le connecteur MongoDB
ENV SPARK_VERSION=3.5.0 \
    HADOOP_VERSION=3 \
    SPARK_HOME=/opt/spark \
    MONGO_SPARK_CONNECTOR_VERSION=3.0.1 \
    BSON_VERSION=4.2.3 \
    MONGO_JAVA_DRIVER_VERSION=3.12.10

# Télécharger et installer Apache Spark
RUN wget -q "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
    && tar xzf "spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" -C /usr/local \
    && rm "spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
    && mv /usr/local/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME}

RUN echo >> ~/.bashrc \
    && echo "### Spark setup ###" >> ~/.bashrc \
    && echo "export SPARK_HOME=${SPARK_HOME}" >> ~/.bashrc \
    && echo "export PATH=\$PATH:\$SPARK_HOME/bin:\$SPARK_HOME/sbin" >> ~/.bashrc \
    && echo "export PYSPARK_PYTHON=python3" >> ~/.bashrc

RUN wget -q "https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/${MONGO_SPARK_CONNECTOR_VERSION}/mongo-spark-connector_2.12-${MONGO_SPARK_CONNECTOR_VERSION}.jar" -P "${SPARK_HOME}/jars/" && \
    wget -q "https://repo1.maven.org/maven2/org/mongodb/bson/${BSON_VERSION}/bson-${BSON_VERSION}.jar" -P "${SPARK_HOME}/jars/" && \
    wget -q "https://repo1.maven.org/maven2/org/mongodb/mongo-java-driver/${MONGO_JAVA_DRIVER_VERSION}/mongo-java-driver-${MONGO_JAVA_DRIVER_VERSION}.jar" -P "${SPARK_HOME}/jars/"

RUN sed -i 's/rootLogger.level = info/rootLogger.level = error/' ${SPARK_HOME}/conf/log4j2.properties.template \
    && mv ${SPARK_HOME}/conf/log4j2.properties.template ${SPARK_HOME}/conf/log4j2.properties

# Définissez le répertoire de travail dans le conteneur
WORKDIR /spark

COPY /spark/requirements.txt /spark/requirements.txt
COPY /spark/.env .

# Installation des dépendances
RUN pip install -r requirements.txt

# Définir la commande à exécuter lorsque le conteneur démarre
<<<<<<< Updated upstream
ENTRYPOINT ["tail", "-f", "/dev/null"]
=======
CMD ["tail", "-f", "/dev/null"]
>>>>>>> Stashed changes
