# RailTweet Azure Implementation

A Django-based application for analyzing railway-related tweets using Azure services. This implementation leverages various Azure services for robust, scalable, and secure operation.

## Azure Services Used

- **Azure App Service**: Hosts the Django web application
- **Azure Database for PostgreSQL**: Main database
- **Azure Cognitive Services**: Text Analytics for sentiment analysis
- **Azure Blob Storage**: For storing tweet archives
- **Azure Key Vault**: Secure secrets management
- **Azure Application Insights**: Application monitoring and analytics

## Prerequisites

- Azure CLI installed and configured
- Python 3.9 or higher
- PostgreSQL client
- Git

## Local Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd railtweet
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file:
```bash
cp .env.example .env
```

5. Update the .env file with your Azure credentials and configuration.

6. Run migrations:
```bash
python manage.py migrate
```

7. Start the development server:
```bash
python manage.py runserver
```

## Azure Deployment

1. Ensure you have Azure CLI installed and are logged in:
```bash
az login
```

2. Run the Azure setup script:
```bash
chmod +x deploy/azure-setup.sh
./deploy/azure-setup.sh
```

3. The script will:
   - Create all necessary Azure resources
   - Configure Azure Key Vault
   - Set up Azure Database for PostgreSQL
   - Configure Azure App Service
   - Set up Azure Cognitive Services
   - Create Azure Storage account and containers

4. Deploy the application:
```bash
az webapp up --runtime PYTHON:3.9
```

5. Run migrations on Azure:
```bash
az webapp ssh --name <app-name> --resource-group <resource-group>
python manage.py migrate
```

## Key Features

- **Tweet Analysis**: Sentiment analysis using Azure Cognitive Services
- **Emergency Detection**: Automated detection of emergency-related tweets
- **Data Archiving**: Automated archiving of tweets to Azure Blob Storage
- **Secure Configuration**: All sensitive information stored in Azure Key Vault
- **Scalable Infrastructure**: Built on Azure PaaS offerings for automatic scaling

## Project Structure

```
railtweet/
├── config/                 # Azure and Django configuration
├── deploy/                 # Deployment scripts
├── railtweet/             # Django project settings
├── scrapper/              # Tweet scraping and analysis
│   ├── models.py          # Data models with Azure integration
│   ├── views.py           # Views and API endpoints
│   └── sentiment.py       # Azure Cognitive Services integration
├── static/                # Static files
├── templates/             # HTML templates
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

## Environment Variables

Required environment variables for Azure integration:

```
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-client-secret>
AZURE_SUBSCRIPTION_ID=<your-subscription-id>

AZURE_POSTGRESQL_HOST=<your-db-host>
AZURE_POSTGRESQL_NAME=<your-db-name>
AZURE_POSTGRESQL_USER=<your-db-user>
AZURE_POSTGRESQL_PASSWORD=<your-db-password>

AZURE_STORAGE_CONNECTION_STRING=<your-storage-connection-string>
AZURE_COGNITIVE_ENDPOINT=<your-cognitive-services-endpoint>
AZURE_COGNITIVE_KEY=<your-cognitive-services-key>

APPLICATIONINSIGHTS_CONNECTION_STRING=<your-app-insights-connection-string>
```

## Monitoring and Maintenance

- Monitor application performance in Azure Application Insights
- View logs in Azure App Service logs
- Check Azure Portal for resource metrics
- Regular database backups are automated through Azure PostgreSQL

## Security Considerations

- All secrets are stored in Azure Key Vault
- Database connections use SSL
- Azure App Service is configured with managed identity
- CORS is properly configured for security
- Regular security updates are applied automatically

## Troubleshooting

1. **Database Connection Issues**:
   - Verify firewall rules in Azure PostgreSQL
   - Check connection string in Azure Key Vault
   - Ensure SSL is properly configured

2. **Cognitive Services**:
   - Verify API keys and endpoints
   - Check request quotas and limits
   - Monitor API response times

3. **Storage Issues**:
   - Verify storage account access keys
   - Check container permissions
   - Monitor storage metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
