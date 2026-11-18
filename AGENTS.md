# Contexte et conventions — FraudAnalytics

## Contexte

FraudAnalytics est un projet académique de détection de fraude bancaire, combinant traitements batch et temps réel dans une architecture Lambda. Le dépôt doit rester dépourvu de données bancaires sensibles, de secrets et de logique métier tant que l’initialisation n’est pas validée.

## Conventions de développement

- Utiliser Python 3.11+ et respecter PEP 8.
- Organiser le code par responsabilité et conserver la séparation Bronze/Silver/Gold.
- Préférer des modules courts, testables et documentés.
- Ne jamais versionner de secrets, identifiants, dumps ou datasets.
- Documenter les décisions structurantes dans `docs/adr/`.
- Ajouter ou mettre à jour les tests lors de toute implémentation.
- Nommer les jobs et DAGs avec des noms explicites, en minuscules et avec des underscores.
- Versionner les schémas, contrats de données et règles de qualité.
- Utiliser des branches de travail et des commits atomiques décrivant une seule évolution.

## Gouvernance des données

Les données sources doivent rester hors Git. Les accès, rétentions, classifications, lineage et contrats sont documentés dans `governance/`. Toute donnée de test doit être explicitement synthétique et validée avant ajout.

## Dataset de travail réduit

Avant l’EDA, exécuter `python scripts/prepare_dataset.py`. Le script lit les transactions par chunks de 100 000 lignes, conserve les dates à partir du 01/01/2015 et filtre les labels en flux via un index SQLite temporaire. Les fichiers sources ne sont jamais modifiés ; les sorties sont écrites dans `data/prepared/`, exclu de Git. Les montants négatifs et les transactions non labellisées sont conservés.

Les transactions 2015–2018 constituent le périmètre batch et celles de 2019 le périmètre streaming. Les notebooks EDA doivent utiliser `data/prepared/transactions.csv` et `data/prepared/train_fraud_labels.json`.

## Validation attendue

Avant une revue : tests automatisés, contrôles de qualité, vérification de configuration sans secrets et documentation de l’impact sur les couches concernées.
