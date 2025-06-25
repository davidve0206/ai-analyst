import os
import struct
import time
import urllib.parse

from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential

from .settings import app_settings

# If the variables are read from a .env file, they should be set in the environment
if app_settings.azure_client_id is not None:
    os.environ["AZURE_CLIENT_ID"] = app_settings.azure_client_id
if app_settings.azure_tenant_id is not None:
    os.environ["AZURE_TENANT_ID"] = app_settings.azure_tenant_id
if app_settings.azure_client_secret is not None:
    os.environ["AZURE_CLIENT_SECRET"] = (
        app_settings.azure_client_secret.get_secret_value()
    )

azure_credential = DefaultAzureCredential()

# Token cache
_db_token_cache: AccessToken | None = None
TOKEN_REFRESH_PERIOD = 300  # 5 minutes before expiration


def get_azure_sql_access_token_bytes() -> bytes:
    global _db_token_cache

    # Refresh if no token or it's expiring
    if (
        _db_token_cache is None
        or _db_token_cache.expires_on - time.time() < TOKEN_REFRESH_PERIOD
    ):
        _db_token_cache = azure_credential.get_token(
            "https://database.windows.net/.default"
        )

    return _db_token_cache.token.encode("utf-16-le")


# TODO: Review if this is the right place for the following functions.
# The logic to putting it here is that this is closely related to azure authentication
def get_db_connection_string() -> str:
    """
    Generates the connection string for Azure SQL Database using the ClientSecretCredential.
    """
    connection_string = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={app_settings.azure_db_server};"
        f"Database={app_settings.azure_db_database};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        f"Connection Timeout={app_settings.azure_db_connection_timeout};"
        f"LoginTimeout={app_settings.azure_db_connection_timeout};"
    )

    encoded = urllib.parse.quote_plus(connection_string)
    return f"mssql+aioodbc:///?odbc_connect={encoded}"


def provide_azure_sql_token(dialect, conn_rec, cargs, cparams):
    """
    Called before the engine creates a new connection. Injects Azure token into
    the connection parameters.
    """

    token_bytes = get_azure_sql_access_token_bytes()
    token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
    SQL_COPT_SS_ACCESS_TOKEN = 1256  # Defied by microsoft

    cparams["attrs_before"] = {SQL_COPT_SS_ACCESS_TOKEN: token_struct}
