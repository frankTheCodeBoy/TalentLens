# ARCHIVED: Azure Deployment Configuration

**Status**: ❌ Not in use - Authentication issues

## Original Azure Setup

### Prerequisites
- Azure subscription
- Azure CLI installed
- GitHub Student Pack benefits

### Step 1: Create Resource Group
```bash
az group create --name resume-classifier-rg --location eastus
```

### Step 2: Create Container Registry
```bash
az acr create --resource-group resume-classifier-rg --name resumeclassifier --sku Basic
az acr login --name resumeclassifier
```

### Step 3: Build and Push Image
```bash
docker build -t resumeclassifier.azurecr.io/resume-classifier:latest .
docker push resumeclassifier.azurecr.io/resume-classifier:latest
```

### Step 4: Create App Service Plan
```bash
az appservice plan create --name resume-plan --resource-group resume-classifier-rg --sku B1 --is-linux
```

### Step 5: Create Web App
```bash
az webapp create --resource-group resume-classifier-rg --plan resume-plan --name resume-classifier-app --deployment-container-image-name resumeclassifier.azurecr.io/resume-classifier:latest
```

### Step 6: Set Environment Variables
```bash
az webapp config appsettings set --resource-group resume-classifier-rg --name resume-classifier-app --settings BACKEND_API_KEY=changeme123 ALLOWED_ORIGINS="*" HUGGINGFACE_API_KEY=<your-token>
```

### Step 7: Setup Container Registry Auth
```bash
az webapp deployment container config --name resume-classifier-app --resource-group resume-classifier-rg --docker-custom-image-name resumeclassifier.azurecr.io/resume-classifier:latest --docker-registry-server-url https://resumeclassifier.azurecr.io --docker-registry-server-user <username> --docker-registry-server-password <password>
```

### Step 8: Access App
- URL: `https://resume-classifier-app.azurewebsites.net`
- Streamlit: `:8501`
- API Docs: `:8000/docs`

## Why Not Used
- Required Azure subscription authentication
- Credit card verification needed
- Complex setup process

## To Reactivate
If you get Azure working, follow steps 1-8 above.
