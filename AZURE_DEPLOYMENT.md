# 🚀 Azure App Service Deployment Guide

## 📋 Prerequisites

1. **Azure Account** with App Service access
2. **Azure CLI** or Azure Portal access
3. **Git repository** with your PocketOJ code

## 🛠️ Quick Azure Deployment

### **Option 1: Azure CLI (Recommended)**

```bash
# 1. Login to Azure
az login

# 2. Create Resource Group
az group create --name pocketoj-rg --location "East US"

# 3. Create App Service Plan (Linux)
az appservice plan create \
    --name pocketoj-plan \
    --resource-group pocketoj-rg \
    --sku B1 \
    --is-linux

# 4. Create Web App
az webapp create \
    --name your-pocketoj-app \
    --resource-group pocketoj-rg \
    --plan pocketoj-plan \
    --runtime "PYTHON|3.11"

# 5. Configure App Settings (IMPORTANT!)
az webapp config appsettings set \
    --name your-pocketoj-app \
    --resource-group pocketoj-rg \
    --settings \
        SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')" \
        FLASK_ENV="production" \
        POCKETOJ_CONFIG="config.prod.yaml" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true"

# 6. Deploy from Git
az webapp deployment source config \
    --name your-pocketoj-app \
    --resource-group pocketoj-rg \
    --repo-url https://github.com/yourusername/PocketOJ \
    --branch main \
    --manual-integration
```

### **Option 2: Azure Portal**

1. **Create Web App**:
   - Go to Azure Portal → Create Resource → Web App
   - **Runtime**: Python 3.11
   - **Operating System**: Linux
   - **Plan**: Basic B1 or higher

2. **Configure Application Settings** (Configuration → Application Settings):
   ```
   SECRET_KEY = [generate-32-char-hex-key]
   FLASK_ENV = production
   POCKETOJ_CONFIG = config.prod.yaml
   SCM_DO_BUILD_DURING_DEPLOYMENT = true
   ```

3. **Deploy**:
   - Go to Deployment Center
   - Choose GitHub/Local Git
   - Select your repository

## 🔧 Azure-Specific Files Created

✅ **`startup.sh`** - Azure App Service startup script  
✅ **`.deployment`** - Tells Azure to use custom startup  
✅ **`web.config`** - IIS configuration (if needed)  
✅ **`config.prod.yaml`** - Updated for Azure dynamic ports  

## 📊 Application Settings (Required)

Set these in Azure Portal → Your App → Configuration → Application Settings:

| Setting | Value | Purpose |
|---------|-------|---------|
| `SECRET_KEY` | `[32-char hex key]` | Flask session security |
| `FLASK_ENV` | `production` | Production mode |
| `POCKETOJ_CONFIG` | `config.prod.yaml` | Production config file |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | Build dependencies on Azure |

## 🔐 Generate Secure Secret Key

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy this value to Azure App Settings as `SECRET_KEY`.

## 🌐 Post-Deployment Verification

After deployment, your app will be available at:
```
https://your-pocketoj-app.azurewebsites.net
```

**Test endpoints:**
- Dashboard: `https://your-pocketoj-app.azurewebsites.net/`
- Health: `https://your-pocketoj-app.azurewebsites.net/health`
- API: `https://your-pocketoj-app.azurewebsites.net/api/problems`

## 📝 Troubleshooting

### **1. Check Logs**
```bash
az webapp log tail --name your-pocketoj-app --resource-group pocketoj-rg
```

### **2. Common Issues**
- **Build fails**: Ensure `SCM_DO_BUILD_DURING_DEPLOYMENT=true`
- **Import errors**: Check Python version (use 3.11)
- **Secret key error**: Verify `SECRET_KEY` in App Settings
- **502 errors**: Check startup script logs

### **3. SSH into Container** (Debug)
```bash
az webapp ssh --name your-pocketoj-app --resource-group pocketoj-rg
```

## 📈 Scaling & Performance

### **Recommended App Service Plans:**
- **Development**: F1 (Free) - Limited hours
- **Testing**: B1 (Basic) - $13/month
- **Production**: S1 (Standard) - $70/month
- **High Performance**: P1V2 (Premium) - $146/month

### **Auto-Scaling** (Standard+ plans):
- Scale based on CPU/Memory usage
- Scale out to multiple instances

## 🔒 Security Best Practices

1. **Custom Domain**: Use your own domain with SSL
2. **Authentication**: Enable Azure AD integration if needed  
3. **IP Restrictions**: Limit access by IP ranges
4. **Managed Identity**: For accessing other Azure resources

## 🚀 CI/CD Pipeline (Optional)

Create `.github/workflows/azure-deploy.yml`:
```yaml
name: Deploy to Azure App Service

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: pip install -r requirements.prod.txt
      
    - name: Deploy to Azure
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'your-pocketoj-app'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

## ✅ Ready for Azure!

Your PocketOJ system is now configured for Azure App Service deployment with:
- Production-ready configuration
- Secure environment variables
- Auto-scaling capabilities
- Built-in monitoring and logging

**Total deployment time**: ~5-10 minutes from first Azure CLI command! 🎯
