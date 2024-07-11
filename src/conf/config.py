from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    A class to define and store settings for the application.

    Attributes:
    - sqlalchemy_database_url (str): The URL for the SQLAlchemy database.
    - secret_key (str): The secret key for the application.
    - algorithm (str): The algorithm used for encryption.
    - mail_username (str): The username for sending emails.
    - mail_password (str): The password for sending emails.
    - mail_from (str): The email address to send emails from.
    - mail_port (int): The port for the mail server.
    - mail_server (str): The server for sending emails.
    - redis_host (str): The host for the Redis server.
    - redis_port (int): The port for the Redis server.
    - postgres_db (str): The name of the PostgreSQL database.
    - postgres_user (str): The username for the PostgreSQL database.
    - postgres_password (str): The password for the PostgreSQL database.
    - postgres_port (int): The port for the PostgreSQL database.
    - cloudinary_name (str): The name of the Cloudinary account.
    - cloudinary_api_key (str): The API key for Cloudinary.
    - cloudinary_api_secret (str): The API secret for Cloudinary.

    Config:
    - env_file (str): The name of the environment file to load settings from.
    - env_file_encoding (str): The encoding of the environment file.
    """
    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis_host: str
    redis_port: int 
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
