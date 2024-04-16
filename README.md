### Hi there 👋

<!--
**EcoBalyse/ecobalyse** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I’m currently working on ...
- 🌱 I’m currently learning ...
- 👯 I’m looking to collaborate on ...
- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
-->

### For INDIVIDUAL ###

# Extraction

docker build -t ecobalyse-extract .

docker run -it --rm ecobalyse-extract

# PySpark

docker build -t ecobalyse-spark .

docker run -it --rm ecobalyse-spark

# API

docker build -t ecobalyse-api .

docker run -it --rm ecobalyse-api

### For ALL ###

docker-compose up -d