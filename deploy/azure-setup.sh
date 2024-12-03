#!/bin/bash

# Exit on error
set -e

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Default values
LOCATION=${AZURE_LOCATION:-"eastus"}
RESOURCE_GROUP=${AZURE_RESOURCE_GROUP:-"railtweet-rg"}
APP_NAME=${AZURE_APP_NAME:-"railtweet"}
DB_SERVER_NAME=${AZURE_DB_SERVER:-"railtweet-db"}
DB_NAME=${AZURE_DB_NAME:-"railtweet"}
STORAGE_ACCOUNT=${AZURE_STORAGE_ACCOUNT:-"railtweet"}
COGNITIVE_SERVICE_NAME=${AZURE_COGNITIVE_NAME:-"railtweet-cognitive"}
KEYVAULT_NAME=${AZURE_KEYVAULT_NAME:-"railtweet-kv"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "Starting Azure resource deployment for RailTweet..."

# Create Resource Group
echo "Creating Resource Group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

# Create Azure PostgreSQL server
echo "Creating PostgreSQL server..."
az postgres server create \
    --resource-group $RESOURCE_GROUP \
    --name $DB_SERVER_NAME \
    --location $LOCATION \
    --admin-user railtweet_admin \
    --admin-password $DB_PASSWORD \
    --sku-name B_Gen5_1 \
    --version 11

# Create database
echo "Creating database..."
az postgres db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_SERVER_NAME \
    --name $DB_NAME

# Create Storage Account
echo "Creating Storage Account..."
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS \
    --kind StorageV2

# Create Blob Container
echo "Creating Blob Container..."
STORAGE_KEY=$(az storage account keys list -g $RESOURCE_GROUP -n $STORAGE_ACCOUNT --query '[0].value' -o tsv)
az storage container create \
    --name tweet-archives \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY

# Create Cognitive Services
echo "Creating Cognitive Services account..."
az cognitiveservices account create \
    --name $COGNITIVE_SERVICE_NAME \
    --resource-group $RESOURCE_GROUP \
    --kind TextAnalytics \
    --sku S0 \
    --location $LOCATION \
    --yes

# Create Key Vault
echo "Creating Key Vault..."
az keyvault create \
    --name $KEYVAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Create App Service Plan
echo "Creating App Service Plan..."
az appservice plan create \
    --name ${APP_NAME}-plan \
    --resource-group $RESOURCE_GROUP \
    --sku B1 \
    --is-linux

# Create Web App
echo "Creating Web App..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan ${APP_NAME}-plan \
    --name $APP_NAME \
    --runtime "PYTHON|3.9" \
    --deployment-local-git

# Enable managed identity for the web app
echo "Enabling managed identity..."
az webapp identity assign \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP

# Get the managed identity ID
IDENTITY_ID=$(az webapp identity show --name $APP_NAME --resource-group $RESOURCE_GROUP --query principalId -o tsv)

# Grant Key Vault access to the web app
echo "Granting Key Vault access..."
az keyvault set-policy \
    --name $KEYVAULT_NAME \
    --object-id $IDENTITY_ID \
    --secret-permissions get list

# Store secrets in Key Vault
echo "Storing secrets in Key Vault..."
az keyvault secret set --vault-name $KEYVAULT_NAME --name "DB-HOST" --value "${DB_SERVER_NAME}.postgres.database.azure.com"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "DB-NAME" --value "$DB_NAME"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "DB-USER" --value "railtweet_admin"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "DB-PASSWORD" --value "$DB_PASSWORD"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "STORAGE-CONNECTION-STRING" --value "$(az storage account show-connection-string -g $RESOURCE_GROUP -n $STORAGE_ACCOUNT -o tsv)"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "COGNITIVE-KEY" --value "$(az cognitiveservices account keys list -g $RESOURCE_GROUP -n $COGNITIVE_SERVICE_NAME --query 'key1' -o tsv)"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "COGNITIVE-ENDPOINT" --value "$(az cognitiveservices account show -g $RESOURCE_GROUP -n $COGNITIVE_SERVICE_NAME --query 'properties.endpoint' -o tsv)"

# Configure Web App settings
echo "Configuring Web App settings..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
        AZURE_KEYVAULT_URL="https://${KEYVAULT_NAME}.vault.azure.net/" \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE=true \
        SCM_DO_BUILD_DURING_DEPLOYMENT=true \
        DJANGO_SETTINGS_MODULE=railtweet.settings

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo "Resource Group: $RESOURCE_GROUP"
echo "Web App URL: https://${APP_NAME}.azurewebsites.net"
echo "Key Vault: https://${KEYVAULT_NAME}.vault.azure.net/"

echo -e "${RED}Important:${NC}"
echo "1. Update your .env file with the Key Vault URL"
echo "2. Deploy your code using Git"
echo "3. Run migrations using the Azure Web App SSH console"
echo "4. Configure your custom domain and SSL certificate if needed"
