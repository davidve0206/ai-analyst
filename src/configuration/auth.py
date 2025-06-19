from azure.identity import ClientSecretCredential
from .settings import app_settings

azure_credential = ClientSecretCredential(
    tenant_id=app_settings.azure_tenant_id,
    client_id=app_settings.azure_client_id,
    client_secret=app_settings.azure_client_secret,
)
