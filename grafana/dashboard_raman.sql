SELECT
  "Time stream" AT TIME ZONE 'UTC-7' AT TIME ZONE 'UTC' AS "time",
  prediction
FROM raman_db
ORDER BY 1