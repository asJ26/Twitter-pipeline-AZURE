import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Azure Configuration
AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
AZURE_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')

# Key Vault Configuration
KEY_VAULT_NAME = os.getenv('KEY_VAULT_NAME')
KEY_VAULT_URL = f"https://{KEY_VAULT_NAME}.vault.azure.net/"

# Azure PostgreSQL Configuration
AZURE_POSTGRESQL_HOST = os.getenv('AZURE_POSTGRESQL_HOST')
AZURE_POSTGRESQL_NAME = os.getenv('AZURE_POSTGRESQL_NAME')
AZURE_POSTGRESQL_USER = os.getenv('AZURE_POSTGRESQL_USER')
AZURE_POSTGRESQL_PASSWORD = os.getenv('AZURE_POSTGRESQL_PASSWORD')

# Azure Cognitive Services
AZURE_COGNITIVE_ENDPOINT = os.getenv('AZURE_COGNITIVE_ENDPOINT')
AZURE_COGNITIVE_KEY = os.getenv('AZURE_COGNITIVE_KEY')

# Azure Application Insights
APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')

def get_secret(secret_name):
    """Retrieve a secret from Azure Key Vault"""
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)
    try:
        return client.get_secret(secret_name).value
    except Exception as e:
        print(f"Error retrieving secret {secret_name}: {str(e)}")
        return None

# Database Configuration for Azure PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': AZURE_POSTGRESQL_NAME,
        'USER': AZURE_POSTGRESQL_USER,
        'PASSWORD': AZURE_POSTGRESQL_PASSWORD,
        'HOST': AZURE_POSTGRESQL_HOST,
        'PORT': '5432',
        'OPTIONS': {'sslmode': 'require'},
    }
}
