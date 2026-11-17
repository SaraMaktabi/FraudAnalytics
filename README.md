# FraudAnalytics

Projet académique Big Data de détection de fraude bancaire en batch et en temps réel, réalisé par trois étudiants.

## Objectif

Construire une plateforme analytique suivant une architecture Lambda : le batch layer traite les données historiques, le speed layer traite les événements en temps réel et la couche Gold réconcilie les résultats pour les usages analytiques et métier.

## Architecture cible

- **Sources et CDC** : PostgreSQL, Debezium et Kafka Connect.
- **Streaming** : Apache Kafka.
- **Traitements** : PySpark et Spark Structured Streaming.
- **Stockage** : MinIO avec Delta Lake et médaillon Bronze/Silver/Gold.
- **Qualité** : Great Expectations.
- **Analytique** : Spark SQL et cubes OLAP.
- **Machine Learning** : Spark MLlib, avec suivi MLflow.
- **Orchestration et exposition** : Airflow et Superset.
- **Observabilité** : Prometheus et Grafana.
- **Infrastructure** : Docker Compose.

## Données prévues

Les fichiers `transactions.csv`, `cards.csv`, `users.csv`, `mcc_codes.json` et `train_fraud_labels.json` sont attendus localement mais sont exclus du contrôle de version. Aucune donnée bancaire réelle ou sensible ne doit être commitée.

## Structure

Les dossiers sont séparés par responsabilité : infrastructure, ingestion, traitements médaillon, qualité, OLAP, machine learning, orchestration, dashboards, monitoring, gouvernance, tests et documentation. Les répertoires sont initialisés avec `.gitkeep` jusqu’à l’implémentation des composants.

## Démarrage du développement

Cette version initialise uniquement le squelette du projet. Les dépendances, services Docker, pipelines et logiques métier seront ajoutés progressivement après validation de l’architecture.

## Équipe

Projet réalisé par trois étudiants. Les responsabilités et décisions techniques seront documentées dans `docs/` et les conventions sont définies dans `AGENTS.md`.
