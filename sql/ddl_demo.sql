-- DDL HYPOTHÉTIQUE — Documentation des choix d'architecture data
--
-- Ce DDL N'EST PAS exécuté contre la table publique
-- bigquery-public-data.usda_nass_agriculture.crops (read-only, non partitionnée
-- ni clusterisée — limite imposée par BigQuery sur les datasets publics).
--
-- Il décrit la table OPTIMALE que l'on créerait si l'on possédait le schéma
-- cible (cas réel chez Bayer Crop Science par exemple).
--
-- Hypothèses sur le pattern d'accès :
--   - 95% des requêtes filtrent par fenêtre temporelle (essai annuel, dernier
--     trimestre, dernière campagne, etc.)
--   - Filtrage fréquent secondaire par essai (état, région, programme expé)
--   - Drill-down occasionnel par type de mesure ou par parcelle

-- remplacer "anythinghere" par le nom du projet

CREATE TABLE IF NOT EXISTS `anythinghere.observations.observations_terrain`
(
  essai_id STRING NOT NULL OPTIONS(description="Cadre expérimental régional (ex: 'IA', 'TX')"),
  parcelle_id STRING NOT NULL OPTIONS(description="Lieu physique d'observation (ex: 'LINN', 'POLK')"),
  date_observation DATE NOT NULL OPTIONS(description="Date de l'observation (ISO)"),
  mesure_valeur FLOAT64 OPTIONS(description="Valeur numérique de la mesure (NULL si supprimée)"),
  mesure_type STRING NOT NULL OPTIONS(description="Type '<COMMODITY>_<STATISTIC>'"),
  loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() OPTIONS(description="Horodatage d'ingestion (audit)")
)

-- ----------------------------------------------------------------------------
-- PARTITIONNEMENT : par date_observation (DAY)
-- Pourquoi : la majorité des requêtes filtrent par date. Le partitionnement
-- élimine PHYSIQUEMENT du scan toutes les partitions hors fenêtre.
-- Sur 5 ans de données journalières : 1825 partitions. Filtre 1 mois = scan
-- ~30 partitions = ~1,6% du volume total.
-- ----------------------------------------------------------------------------
PARTITION BY date_observation

-- ----------------------------------------------------------------------------
-- CLUSTERING : (essai_id, mesure_type, parcelle_id) — ordre choisi
-- Le clustering trie physiquement les lignes DANS chaque partition. L'ordre
-- des colonnes est critique : la 1ère est la plus efficace pour le filtrage.
--
--   1. essai_id (cardinalité moyenne, ~50 valeurs)
--      - filtre métier le plus fréquent ; cardinalité moyenne = idéal en 1er
--   2. mesure_type (~ quelques centaines de valeurs)
--      - dimension analytique secondaire (« rendement », « production »...)
--   3. parcelle_id (cardinalité élevée, ~3000 valeurs)
--      - drill-down occasionnel ; cardinalité élevée = moins efficace, donc 3e
--
-- Combiné avec le partitionnement : un filtre {date + essai} ne scanne que
-- les blocs concernés dans les partitions concernées -> réduction typique
-- 80-95% du scan vs une table non optimisée.
-- ----------------------------------------------------------------------------
CLUSTER BY essai_id, mesure_type, parcelle_id

OPTIONS (
  description = "Observations terrain — partitionnée par date_observation et clusterisée par essai_id puis mesure_type puis parcelle_id.",

  -- Garde-fou : refuse toute requête sans filtre de partition.
  -- Évite le scan complet par accident (économie potentielle énorme en prod).
  require_partition_filter = TRUE,

  -- Rétention 5 ans (à ajuster selon la politique métier).
  partition_expiration_days = 1825
);
