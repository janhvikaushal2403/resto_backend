from pydantic_settings import BaseSettings, SettingsConfigDict
import os
class Settings(BaseSettings):
    database_username: str
    database_name: str
    database_password: str
    database_port: str
    database_host: str
    secret_key: str
    algorithm: str
    expiry_time_taken: int 
    postgresql_url : str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
# settings = Settings(
#     database_username=os.getenv("DATABASE_USERNAME", "postgres"),
#     database_name=os.getenv("DATABASE_NAME", "Resto"),
#     database_password=os.getenv("DATABASE_PASSWORD", "Jahan1024"),
#     database_port=os.getenv("DATABASE_PORT", "3306"),
#     database_host=os.getenv("DATABASE_HOST", "localhost"),
#     secret_key=os.getenv("SECRET_KEY", "09d2b8y3r03o4yih2a4nfaarw6ca2t3h4isuo4t3e5th0i0s2a53p2pacf63b88e8d3e7"),
#     algorithm=os.getenv("ALGORITHM", "HS256"),
#     expiry_time_taken=int(os.getenv("EXPIRY_TIME_TAKEN", "90"))
#     # Add other variables as needed
# )