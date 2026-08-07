-- Delay rate and average delay by airline
SELECT carrier,
       COUNT(*) AS flights,
       ROUND(100.0 * AVG(is_delayed), 2) AS delay_rate_percent,
       ROUND(AVG(departure_delay_minutes), 2) AS average_delay_minutes
FROM flights
WHERE cancelled = 0
GROUP BY carrier
ORDER BY delay_rate_percent DESC;

-- Busiest routes with enough observations for meaningful comparison
SELECT origin, destination,
       COUNT(*) AS flights,
       ROUND(100.0 * AVG(is_delayed), 2) AS delay_rate_percent
FROM flights
WHERE cancelled = 0
GROUP BY origin, destination
HAVING COUNT(*) >= 10
ORDER BY flights DESC
LIMIT 20;

-- Hourly departure-delay pattern
SELECT scheduled_departure_hour,
       COUNT(*) AS flights,
       ROUND(100.0 * AVG(is_delayed), 2) AS delay_rate_percent
FROM flights
WHERE cancelled = 0
GROUP BY scheduled_departure_hour
ORDER BY scheduled_departure_hour;
