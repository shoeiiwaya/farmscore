import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FarmScore"
    VERSION: str = "1.0.0"
    ENV: str = "development"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/farmscore",
    )

    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    API_KEY_PREFIX: str = "fs_"

    # External APIs
    JMA_MESH_BASE: str = "https://www.data.jma.go.jp/gmd/risk/obsdl/show/table"
    GSI_ELEVATION_API: str = "https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php"
    GSI_GEOCODE_API: str = "https://msearch.gsi.go.jp/address-search/AddressSearch"

    # MQTT (sensor integration)
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_TOPIC_PREFIX: str = "farmscore/sensors/"

    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # Rate limiting
    RATE_LIMIT_FREE: str = "100/day"
    RATE_LIMIT_PRO: str = "5000/day"

    class Config:
        env_file = ".env"


settings = Settings()
