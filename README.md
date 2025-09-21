# Agent d'analyse de marché e-commerce

## Description

Ce projet a comme but de créer un agent d'analyse de marché automatisées et personnalisées basées sur des données en temps réel.
Le projet doit être capable de :
- Collecter des données produit
- Analyser la concurrence
- Évaluer le sentiment client
- Générer des recommandations business

---
## Setup du projet

### Prérequis :
Avant de commencer à utiliser ce projet, il faut installer pyenv et direnv.

`brew install pyenv direnv`

Il faut ensuite configurer le "shell".
- pour pyenv, suivre la documentation officielle: [ici](https://github.com/pyenv/pyenv?tab=readme-ov-file#b-set-up-your-shell-environment-for-pyenv)
- pour direnv, suivre la documentation officielle: [ici](https://direnv.net/docs/hook.html)

Enfin, il faut installer la version de python spécifiée dans le fichier .python-version :
```bash
pyenv install $(cat .python-version)
```

Il faut aussi installer docker et docker-compose.

### Installation:
Une fois les prérequis installés, il faut cloner le repo et installer les dépendances.

1. Cloner le repo:

```bash
git clone https://github.com/emiled16/ecommerce-research-agent.git
```

2. Entrer dans le dossier du projet et activer direnv:
```bash
cd ecommerce-research-agent
```

3. modifier le fichier `.env.example` en `.env` et remplir les variables d'environnement. Attention à la variable `DATABASE_URL`. Elle diffère si vous utilisez docker-compose ou le développement local.
Si vous utilisez le développement local, la variable `DATABASE_URL` doit être `sqlite:///./ecommerce_research.db`.
Si vous utilisez docker-compose, la variable `DATABASE_URL` doit être `sqlite:////app/database/ecommerce_research.db`.

4. Lancer le projet avec docker-compose:
```bash
docker-compose up -d
```

5. Utiliser le backend. Vous pouvez ouvrir `localhost:8000` dans votre navigateur.



---
## APIs disponibles :

- `GET /api/v1/health`: Retourne l'état de santé du backend.
- `POST /api/v1/analyze`: Lance une analyse de marché.
- `GET /api/v1/analyze`: Retourne la liste des analyses.
- `GET /api/v1/analysis/{analysis_id}`: Retourne le rapport d'analyse d'un id d'analyse.


## Comment la recherche fonctionne:

La recherche fonctionne de la façon suivante :
1. Le client envoie une requête à l'API.
2. L'API enregistre la requête dans la base de données.
3. L'API lance l'agent de recherche.
4. L'agent vérifie qu'il peut collecter des données sur le produit en question.
5. L'agent collecte les données sur le produit.
6. L'agent utilise un outil pour analyser les revues de produit et générer une analyse de sentiment.
7. L'agent utilise un outil pour analyser les tendances de marché du produit.
8. L'agent utilise un outil pour générer un rapport d'analyse.
9. L'API enregistre le rapport d'analyse dans la base de données.
10. L'API retourne le rapport d'analyse au client.


## Architecture du projet

Le backend est composé d'un serveur FastAPI qui gère les requêtes et les réponses.
Ces requêtes là peuvent faire appel à un agent LLM qui utilise des outils pour collecter des données, les analyser et générer un rapport d'analyse.
Le backend a aussi accès à une base de données SQLite qui stocke les requêtes et leurs métadonnées.
Chaque requête résulte en un rapport d'analyse qui est stocké dans un dossier reports.
Le chemin du rapport est stocké dans la base de données et est associé à la requête à travers son id.
Les outils de l'agent LLM sont mockés pour le moment. Il utilise des données stockées dans des fichiers json dans le dossier `data`.


## Choix des librairies :

1. FastAPI: Pour le backend.
2. SQLAlchemy: Pour la base de données.
3. Alembic: Pour la migration de la base de données.
3. Pydantic: Pour la validation des données.
4. pydantic-ai: Pour les agents LLM.

En ce qui concerne les agents LLM, j'ai choisi d'utiliser pydantic-ai. La raison est que je n'avais jamais eu la chance de l'utiliser. À travers mon expérience, j'ai beaucoup utilisé pydantic et je trouve que c'est une librairie puissante, élégante et facile à utiliser.
De plus, j'ai déjà développé un agent LLM à partir de zéro dans un projet précédent. Je pense que c'est une perte de temps de le développer de nouveau.
J'ai aussi utilisé Langchain dans le passé et j'ai trouvé que c'est une librairie qui est très compliquée à utiliser (à cause de beaucoup d'abstractions).
Enfin, Pydantic-ai offre un support pour le monitoring/l'observabilité (tracing) avec logfire.

Après avoir fini le développement de l'agent LLM, je trouve que pydantic-ai est bien conçu. J'ai bien aimé le concept de `RunContext` qui permet de passer des données entre les outils.
Une chose que j'aurais fait différemment, c'est d'utiliser plusieurs mini-agents pour chaque étape de l'analyse. Cependant, je n'étais pas sûr après avoir lu l'énoncé du projet si c'était ce qui était désiré.
Je pense que l'approche avec plusieurs mini-agents aurait été plus déterministe. Dans le cas actuel, l'agent peut décider de ne pas utiliser un outil par exemple et aucun rapport sera généré.

## Améliorations possibles :

Comme mentionné plus haut, une amélioration possible serait d'utiliser plusieurs mini-agents pour chaque étape de l'analyse.
De plus, l'utilisation de la base de données est très limitée. Je trouve que je ne gère pas assez bien le switch entre la base de données SQLite et la base de données PostgreSQL, et même sqlite entre développement local et docker-compose.


--- 
## Questions Théoriques

### 4. Architecture de données et stockage
En ce qui concerne la base de données, j'ai choisi d'utiliser SQLite pour le développement local.
Dans un développement plus avancé, j'utiliserai une base de données relationnelle comme PostgreSQL pour sauvegarder :
- l'historique des analyses
- les résultats de webscraping
- les configurations des LLMs
- l'historique des requêtes

J'utiliserai un stockage objet pour les rapports d'analyse (exemple : fichier html).
Enfin, j'utiliserai redis pour du caching si nécessaire. Ceci dépendra des besoins business (Nombre de requêtes estimées, temps de réponse des LLMs, etc.). 

### 5. Monitoring et observabilité
Pour ce qui est du monitoring, j'utiliserai logfire pour le tracing des LLMs.
Pydantic-ai offre un support natif pour le tracing avec logfire.
De plus, j'ai utilisé OpenTelemetry pour le monitoring des APIs.
Voici une liste de metrics que je choisirais de surveiller :
- Temps de réponse de l'API
- Nombre de requêtes entrantes
- Nombre de requêtes aux LLMs
- Nombre de requêtes aux APIs externes (outils)
- Nombre de tokens utilisés par l'agent LLM
- healthcheck de l'API
- mémoire utilisée par les différents processus
- temps de réponse des LLMs
- temps de réponse des APIs externes (outils)
- nombre de requêtes en erreur
- nombre de requêtes en succès


### 6. Scaling et optimisation
La réponse à cette question dépend vraiment de plusieurs facteurs :
- comment le projet est déployé
- est-ce que l'architecture LLM est la même ou si on change vers une architecture avec les mini-agents
- est-ce qu'on utilise des LLM hébergés localement ou en ligne

Supposons que nous utilisons kubernetes pour déployer le projet et que nous utilisons une architecture avec les mini-agents.
Supposons que les LLMs sont outsourcés (par exemple à Anthropic).

On pourrait déjà faire une optimisation en utilisant des mini-agents pour chaque étape de l'analyse. Dans ce cas, on pourrait utiliser celery pour paralléliser les étapes. les resultats de chaque etapes pourrait alors etre sauvegardés dans une cache redis.

Les étapes seraient alors parallélisées encore plus, plutôt que de faire une analyse séquentielle.
En ce qui concerne le scaling, on pourrait utiliser l'autoscaling de kubernetes pour scaler serveur backend et LLMs.
Autoscaling horizontal si on suppose que les ressources varient beaucoup.
Autoscaling vertical pour répondre aux nombreuses requêtes.

### 7. Amélioration continue et A/B testing
Pour l'amélioration continue, on pourrait utiliser un pipeline CI/CD pour déployer le projet.
À chaque fois qu'une PR (qui touche aux LLMs) est poussée, on aurait une suite de tests qui roule et évalue la performance de l'agent LLM.
Cette performance serait évaluée sur une suite de tests (LLM as Judge ou/et test fonctionnel). Les tests seraient alors sauvegardés dans une base de données qui fait référence aux commits.

De plus, on pourrait evaluer la perfomance en temps et argent pour les questions.
Finllement, la pipeline CI/CD pourrait populer une application ou un humain pourrait evaluer la performance de l'agent LLM.

---
## Rapport
Vous pouvez trouver des exemples de rapports générés dans le dossier `reports`.

---
## Disclaimer
Les données utilisées ont etes générées par des LLMs. Quelques outils aussi.