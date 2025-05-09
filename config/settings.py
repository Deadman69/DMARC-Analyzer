import os

LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

def str_to_bool(val: str) -> bool:
    return val.lower() in ("1", "true", "yes", "on")

def debug_level(level: str) -> bool:
    """Retourne True si le niveau demandé est inférieur ou égal au niveau courant."""
    level = level.upper()
    if level not in LOG_LEVELS:
        raise ValueError(f"Unknown log level: {level}")
    return LOG_LEVELS[level] >= DEBUG_LEVEL

DEBUG_LEVEL = LOG_LEVELS.get(os.getenv("DEBUG_LEVEL", "WARNING").upper(), 20) # Allows values : "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"

# For the database connection, we never use directly the values from the environment variables, instead we use the DATABASE_URL variable.
DB_USER = os.getenv("DB_USER", "dmarcuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dmarcpass")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "dmarcdb")
DB_DRIVER = os.getenv("DB_DRIVER", "mysql+pymysql")
DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.example.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
IMAP_SSL = str_to_bool(os.getenv("IMAP_SSL", "true"))
IMAP_EMAIL = os.getenv("IMAP_EMAIL", "email-fraud@example.com")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD", "MySecurePassword")

ROOT_DIR = os.getenv("ROOT_DIR", "/dmarc-guardian/")
FEEDER_DIR = os.getenv("FEEDER_DIR", os.path.join(ROOT_DIR, "feeder"))
IMAP_DOWNLOAD_DIR = os.getenv("IMAP_DOWNLOAD_DIR", os.path.join(ROOT_DIR, "email"))
WEB_APP_PORT = int(os.getenv("WEB_APP_PORT", "8000"))
