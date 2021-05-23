DROP TABLE IF EXISTS squet;

CREATE TABLE squet (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rightarmangle REAL NOT NULL,
  rightbodyangle REAL NOT NULL,
  rightarmbodyangle REAL NOT NULL,
  rightupLegangle REAL NOT NULL,
  rightupLegbodyangle REAL NOT NULL
);

DROP TABLE IF EXISTS userProfile;

CREATE TABLE userProfile (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  fans INTEGER NOT NULL DEFAULT 0
);