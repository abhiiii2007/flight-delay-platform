CREATE TABLE IF NOT EXISTS flights (
    flight_date DATE NOT NULL,
    carrier VARCHAR(3) NOT NULL,
    flight_number INTEGER NOT NULL,
    origin VARCHAR(3) NOT NULL,
    destination VARCHAR(3) NOT NULL,
    scheduled_departure_hour INTEGER NOT NULL CHECK (scheduled_departure_hour BETWEEN 0 AND 23),
    departure_delay_minutes REAL NOT NULL,
    distance_miles REAL NOT NULL,
    cancelled INTEGER NOT NULL CHECK (cancelled IN (0, 1)),
    weather_severity REAL NOT NULL,
    month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    is_delayed INTEGER NOT NULL CHECK (is_delayed IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_flight_date ON flights(flight_date);
CREATE INDEX IF NOT EXISTS idx_route ON flights(origin, destination);
CREATE INDEX IF NOT EXISTS idx_carrier ON flights(carrier);
