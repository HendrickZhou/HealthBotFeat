from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # InfluxDB
    influx_url: str = "http://localhost:8086"
    influx_token: str = "mytoken"
    influx_org: str = "MyOrg"
    influx_bucket: str = "health_data"

    # MongoDB
    mongo_uri: str = "mongodb://root:secret@localhost:27017"
    mongo_db_name: str = "demographic"
    mongo_collection_name: str = "users"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()