import logging
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseConfig(BaseSettings):
    database_uri: str = 'postgresql+asyncpg://zpanel:password@127.0.0.1/zpanel'

class ZabbixApiConfig(BaseSettings):
    user_name: str = 'user'
    password: str = 'password'
    url: str = 'http://url/'

class HttpAuthSettings(BaseSettings):
    login: str = 'zpanel'
    hash_password: str = '00000-HASH-0000'

class LoggingConfig(BaseModel):
    log_level: int = logging.INFO

class MiddleWareConfig(BaseModel):
    origins: list[str] = []

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        env_nested_delimiter="__",
        case_sensitive = False,
    )

    #В Zabbix v6.4.0 api и выше поле user поменялось на usernameorigins = []
    zabbix_api_user_field: str = 'username'

    middleware: MiddleWareConfig = MiddleWareConfig()
    logging: LoggingConfig = LoggingConfig()
    auth: HttpAuthSettings = HttpAuthSettings()
    api: ZabbixApiConfig = ZabbixApiConfig()
    db: DatabaseConfig = DatabaseConfig()

settings = Settings()
