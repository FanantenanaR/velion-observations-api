-- Requête analytique type — list observations paginées
--
-- Cible : bigquery-public-data.usda_nass_agriculture.crops (USDA NASS QuickStats)
--         Table publique, non partitionnée/clusterisée.
--
-- Paramètres :
--   @essai_id STRING - filtre exact sur state_alpha (ex: 'IA')
--   @year_min INT64 - année min (incluse), dérivée de date_min côté code
--   @year_max INT64 - année max (incluse), dérivée de date_max côté code
--   @limit INT64 - taille de page
--   @offset INT64 - décalage de pagination
--
-- Mapping appliqué dans le SELECT (cf. app/sources/bigquery_source.py) :
--   state_alpha -> essai_id
--   county_name -> parcelle_id
--   DATE(year, 12, 31) -> date_observation
--   value       -> mesure_valeur
--   CONCAT(commodity_desc, '_', statisticcat_desc) -> mesure_type
--

-- --------------------------------------------------------------------------------
-- Justification de la stratégie de scan
--
-- La table publique n'a pas de partition/clustering : BigQuery est obligé de
-- scanner toutes les lignes correspondant aux filtres. Trois leviers actionnés
-- pour minimiser le coût :
--
-- 1. SELECT colonnaire ciblé (6 colonnes sur 41)
--    BigQuery facture par colonnes scannées (stockage colonnaire). En ne
--    sélectionnant que ce dont on a besoin, on divise le scan par ~7x vs
--    SELECT *. Sur ~7 GB de table totale, on tombe à ~1 GB.
--
-- 2. Filtres ciblés sur des colonnes très sélectives :
--    - agg_level_desc = 'COUNTY' : limite aux 11M rows comté (vs 6M state, etc.)
--    - value IS NOT NULL : exclut les rows supprimées pour confidentialité
--    - state_alpha = @essai_id : un seul état (1/50)
--    - year >= @year_min : filtre temporel
--    Combiné, le scan effectif descend généralement à 200-500 MB.
--
-- 3. Filtre sur `year` (INT) plutôt que DATE(year, 12, 31)
--    Évite l'appel de fonction sur la colonne dans le WHERE -> permet à BQ
--    d'utiliser au mieux ses statistiques de blocs.
--
-- Sur une table HYPOTHÉTIQUE partitionnée+clusterisée (cf. sql/ddl_demo.sql),
-- la même requête scannerait < 50 MB à -90% supplémentaires.

SELECT
  state_alpha                                    AS essai_id,
  county_name                                    AS parcelle_id,
  DATE(year, 12, 31)                             AS date_observation,
  value                                          AS mesure_valeur,
  CONCAT(commodity_desc, '_', statisticcat_desc) AS mesure_type
FROM `bigquery-public-data.usda_nass_agriculture.crops`
WHERE agg_level_desc = 'COUNTY'
  AND value IS NOT NULL
  AND (@essai_id IS NULL OR state_alpha = @essai_id)
  AND (@year_min IS NULL OR year >= @year_min)
  AND (@year_max IS NULL OR year <= @year_max)
ORDER BY year DESC, county_name ASC
LIMIT @limit OFFSET @offset;
