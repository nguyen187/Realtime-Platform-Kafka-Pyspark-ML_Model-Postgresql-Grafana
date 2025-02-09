SELECT
  "Time stream" AT TIME ZONE 'UTC-7' AT TIME ZONE 'UTC' AS "time",
  prediction
FROM raman_db
WHERE
  $__timeFilter("Time stream")
ORDER BY 1