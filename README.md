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

# Installer des dépendances avec Poetry

1. Poetry:

**Installer Poetry:**

```
python -m pip install poetry
```

**Créer un projet Poetry:**

```
poetry new mon-projet-python
```

**Ajouter des dépendances au fichier pyproject.toml:**

```
[tool.poetry.dependencies]
python = "^3.11"
pandas = "^2.2.1"
ipykernel = "^6.29.3"
```

**Installer les dépendances:**

```
poetry install
```