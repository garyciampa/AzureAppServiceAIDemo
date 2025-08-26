# Azure App Service AI Demo - Complete Setup Script
# Advanced RAG & Semantic Kernel Integration

# This script provides comprehensive setup instructions for deploying the Flask application
# with Azure AD authentication, Azure AI Search, Azure OpenAI integration, and Semantic Kernel framework

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Azure App Service AI Demo Setup" -ForegroundColor Cyan
Write-Host "  Advanced RAG & Semantic Kernel Integration" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Load local environment variables from env.ps1 (if present)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$envScript = Join-Path $scriptDir 'env.ps1'
if (Test-Path $envScript) {
    . $envScript
} else {
    Write-Host "env.ps1 not found. Create a .env file with LOCAL_USER=<your-username> and use dot-sourcing to load env.ps1 if you want to use LOCAL_USER in this script." -ForegroundColor Yellow
}

# Step 1: Azure AD App Registration
Write-Host "=== Step 1: Azure AD App Registration ===" -ForegroundColor Green
Write-Host "1. Go to Azure Portal > Azure Active Directory > App registrations"
Write-Host "2. Click 'New registration'"
Write-Host "3. Name: 'DemoAppServiceAi-RAG-SemanticKernel'"
Write-Host "4. Supported account types: Accounts in this organizational directory only"
Write-Host "5. Redirect URI: Web - https://your-app-name.azurewebsites.net/getAToken"
Write-Host "6. Click 'Register'"
Write-Host ""

Write-Host "=== After Azure AD Registration ===" -ForegroundColor Green
Write-Host "1. Copy the 'Application (client) ID' → AZURE_CLIENT_ID"
Write-Host "2. Go to 'Certificates & secrets' > 'New client secret'"
Write-Host "3. Copy the secret value (save immediately!) → AZURE_CLIENT_SECRET"
Write-Host "4. Go to 'Overview' and copy 'Directory (tenant) ID' → AZURE_TENANT_ID"
Write-Host ""

# Step 2: Azure AI Search Setup
Write-Host "=== Step 2: Azure AI Search Service ===" -ForegroundColor Magenta
Write-Host "1. Go to Azure Portal > Create Resource > Azure AI Search"
Write-Host "2. Create new resource group: 'rg-demoappserviceai'"
Write-Host "3. Service name: 'svc-searchaifoundry-01' (or your preferred name)"
Write-Host "4. Location: 'East US' (or your preferred region)"
Write-Host "5. Pricing tier: 'Basic' (sufficient for demo)"
Write-Host "6. Click 'Review + Create' > 'Create'"
Write-Host ""
Write-Host "After creation:"
Write-Host "• Go to service > Keys > copy 'Primary admin key' → AZURE_SEARCH_KEY"
Write-Host "• Copy the service URL → AZURE_SEARCH_ENDPOINT"
Write-Host "• Create an index named 'azureblob-index' with your documents"
Write-Host ""

# Step 3: Azure OpenAI Setup
Write-Host "=== Step 3: Azure OpenAI Service ===" -ForegroundColor Red
Write-Host "1. Go to Azure Portal > Create Resource > Azure OpenAI"
Write-Host "2. Use same resource group: 'rg-demoappserviceai'"
Write-Host "3. Service name: '$($env:LOCAL_USER)-azureopenai' (or your preferred name)"
Write-Host "4. Location: 'East US' (check model availability)"
Write-Host "5. Pricing tier: 'Standard S0'"
Write-Host "6. Click 'Review + Create' > 'Create'"
Write-Host ""
Write-Host "After creation:"
Write-Host "• Go to service > Keys and Endpoint > copy 'KEY 1' → AZURE_OPENAI_KEY"
Write-Host "• Copy the endpoint URL → AZURE_OPENAI_ENDPOINT"
Write-Host "• Go to 'Model deployments' > Create deployments:"
Write-Host "  - Model: 'gpt-35-turbo' or 'gpt-4'"
Write-Host "  - Deployment name: 'gpt-35-turbo' → AZURE_OPENAI_MODEL & AZURE_OPENAI_DEPLOYMENT"
Write-Host "  - Model: 'text-embedding-ada-002' (for Semantic Kernel)"
Write-Host "  - Deployment name: 'text-embedding-ada-002' → AZURE_EMBEDDING_DEPLOYMENT"
Write-Host ""

# Step 3.1: Semantic Kernel Additional Requirements
Write-Host "=== Step 3.1: Semantic Kernel Requirements ===" -ForegroundColor Magenta
Write-Host "🔧 ADDITIONAL SEMANTIC KERNEL SETUP:"
Write-Host "• Ensure Python 3.12+ runtime for full compatibility"
Write-Host "• Install semantic-kernel package (included in requirements.txt)"
Write-Host "• Text embedding model deployment is REQUIRED for SK functionality"
Write-Host "• Plugin architecture supports extensible AI capabilities"
Write-Host "• Modern chat completion API with enhanced context management"
Write-Host ""
Write-Host "🚀 SEMANTIC KERNEL BENEFITS:"
Write-Host "• Future-proof AI orchestration framework"
Write-Host "• Plugin-based extensibility for custom AI functions"
Write-Host "• Enhanced error handling and debugging capabilities"
Write-Host "• Side-by-side comparison with traditional approaches"
Write-Host "• Enterprise-grade AI workflow management"
Write-Host ""

# Step 4: Azure CLI Deployment Commands
Write-Host "=== Step 4: Azure CLI Deployment Commands ===" -ForegroundColor Blue
Write-Host "Prerequisites: Install Azure CLI and login"
Write-Host ""

Write-Host "# 1. Login to Azure" -ForegroundColor Yellow
Write-Host "az login"
Write-Host ""

Write-Host "# 2. Create resource group (if not already created)" -ForegroundColor Yellow
Write-Host "az group create --name rg-demoappserviceai --location 'East US'"
Write-Host ""

Write-Host "# 3. Create App Service plan" -ForegroundColor Yellow
Write-Host "az appservice plan create --name plan-demoappserviceai --resource-group rg-demoappserviceai --sku B1 --is-linux"
Write-Host ""

Write-Host "# 4. Create web app with Python 3.12 runtime" -ForegroundColor Yellow
Write-Host "az webapp create --resource-group rg-demoappserviceai --plan plan-demoappserviceai --name YOUR-UNIQUE-APP-NAME --runtime 'PYTHON|3.12' --deployment-local-git"
Write-Host ""

Write-Host "# 5. Configure comprehensive app settings (replace with your actual values)" -ForegroundColor Yellow
Write-Host "az webapp config appsettings set --resource-group rg-demoappserviceai --name YOUR-UNIQUE-APP-NAME --settings \\"
Write-Host "    AZURE_CLIENT_ID='your-azure-ad-client-id' \\"
Write-Host "    AZURE_CLIENT_SECRET='your-azure-ad-client-secret' \\"
Write-Host "    AZURE_TENANT_ID='your-azure-tenant-id' \\"
Write-Host "    AZURE_SEARCH_ENDPOINT='https://your-search-service.search.windows.net' \\"
Write-Host "    AZURE_SEARCH_KEY='your-search-admin-key' \\"
Write-Host "    AZURE_SEARCH_INDEX='azureblob-index' \\"
Write-Host "    AZURE_OPENAI_ENDPOINT='https://your-openai-service.openai.azure.com' \\"
Write-Host "    AZURE_OPENAI_KEY='your-openai-api-key' \\"
Write-Host "    AZURE_OPENAI_MODEL='gpt-35-turbo' \\"
Write-Host "    AZURE_OPENAI_DEPLOYMENT='gpt-35-turbo' \\"
Write-Host "    AZURE_OPENAI_API_VERSION='2024-12-01-preview' \\"
Write-Host "    AZURE_EMBEDDING_MODEL='text-embedding-ada-002' \\"
Write-Host "    AZURE_EMBEDDING_DEPLOYMENT='text-embedding-ada-002' \\"
Write-Host "    SECRET_KEY='your-random-secret-key-min-24-chars' \\"
Write-Host "    FLASK_DEBUG='false' \\"
Write-Host "    RAG_DEBUG='false' \\"
Write-Host "    SK_DEBUG='false'"
Write-Host ""

Write-Host "# 6. Update redirect URI for production" -ForegroundColor Yellow
Write-Host "# Go back to Azure AD App Registration and update redirect URI to:"
Write-Host "# https://YOUR-UNIQUE-APP-NAME.azurewebsites.net/getAToken"
Write-Host ""

Write-Host "# 7. Deploy the code" -ForegroundColor Yellow
Write-Host "git init"
Write-Host "git add ."
Write-Host "git commit -m 'Initial deployment: Advanced RAG & Semantic Kernel Integration'"
Write-Host "git remote add azure https://YOUR-UNIQUE-APP-NAME.scm.azurewebsites.net:443/YOUR-UNIQUE-APP-NAME.git"
Write-Host "git push azure main"
Write-Host ""

# Step 5: Local Development Environment
Write-Host "=== Step 5: Local Development Setup ===" -ForegroundColor Cyan
Write-Host "Create a .env file in your project root with the following configuration:"
Write-Host ""
Write-Host "# Azure AD Authentication" -ForegroundColor Gray
Write-Host "AZURE_CLIENT_ID=your-azure-ad-client-id"
Write-Host "AZURE_CLIENT_SECRET=your-azure-ad-client-secret"
Write-Host "AZURE_TENANT_ID=your-azure-tenant-id"
Write-Host ""
Write-Host "# Azure AI Search Configuration" -ForegroundColor Gray
Write-Host "AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net"
Write-Host "AZURE_SEARCH_KEY=your-search-admin-key"
Write-Host "AZURE_SEARCH_INDEX=azureblob-index"
Write-Host ""
Write-Host "# Azure OpenAI Configuration" -ForegroundColor Gray
Write-Host "AZURE_OPENAI_ENDPOINT=https://your-openai-service.openai.azure.com"
Write-Host "AZURE_OPENAI_KEY=your-openai-api-key"
Write-Host "AZURE_OPENAI_MODEL=gpt-35-turbo"
Write-Host "AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo"
Write-Host "AZURE_OPENAI_API_VERSION=2024-12-01-preview"
Write-Host ""
Write-Host "# Azure Embedding Configuration (for Semantic Kernel)" -ForegroundColor Gray
Write-Host "AZURE_EMBEDDING_MODEL=text-embedding-ada-002"
Write-Host "AZURE_EMBEDDING_DEPLOYMENT=text-embedding-ada-002"
Write-Host ""
Write-Host "# Flask Application Settings" -ForegroundColor Gray
Write-Host "SECRET_KEY=your-session-secret-key-min-24-chars"
Write-Host "FLASK_DEBUG=true"
Write-Host "RAG_DEBUG=true"
Write-Host "SK_DEBUG=true"
Write-Host ""
Write-Host "# Network Configuration" -ForegroundColor Gray
Write-Host "REDIRECT_URI=http://localhost:5000/getAToken"
Write-Host ""
Write-Host "# Local Development (add your local username here)" -ForegroundColor Gray
Write-Host "LOCAL_USER=your-local-username"
Write-Host ""

Write-Host "=== Step 6: Testing Your Setup ===" -ForegroundColor Green
Write-Host "1. Install dependencies: pip install -r requirements.txt"
Write-Host "2. Run locally: python app.py"
Write-Host "3. Navigate to: http://localhost:5000"
Write-Host "4. Test Azure AD authentication"
Write-Host "5. Try all four operation modes:"
Write-Host "   • Traditional: Search Documents & AI Chat + Search"
Write-Host "   • Modern SK: SK Search & SK AI Chat + RAG"
Write-Host "6. Compare traditional vs Semantic Kernel responses"
Write-Host "7. Verify persona selection (CEO/Financial Analyst)"
Write-Host ""

Write-Host "=== Important Security Notes ===" -ForegroundColor Yellow
Write-Host "🔒 SECURITY CHECKLIST:"
Write-Host "• Replace 'YOUR-UNIQUE-APP-NAME' with a globally unique name"
Write-Host "• Update redirect URI in Azure AD after deployment"
Write-Host "• NEVER commit .env file or secrets to version control"
Write-Host "• Use Azure Key Vault for production secrets"
Write-Host "• Set FLASK_DEBUG=false, RAG_DEBUG=false, SK_DEBUG=false in production"
Write-Host "• Enable HTTPS enforcement in App Service"
Write-Host "• Review App Service security settings"
Write-Host "• Ensure Python 3.12+ runtime for full Semantic Kernel compatibility"
Write-Host ""

Write-Host "=== Post-Deployment Verification ===" -ForegroundColor Magenta
Write-Host "✅ VERIFICATION CHECKLIST:"
Write-Host "• Azure AD authentication working"
Write-Host "• Azure AI Search returning documents"
Write-Host "• Azure OpenAI generating responses"
Write-Host "• Traditional RAG pipeline processing queries correctly"
Write-Host "• Semantic Kernel integration operational"
Write-Host "• Plugin system loading successfully (personas & rag plugins)"
Write-Host "• Four operation modes functional"
Write-Host "• Financial analyst simulation active"
Write-Host "• NovaTech branding displaying properly"
Write-Host "• Debug logging available for both architectures (if enabled)"
Write-Host ""

Write-Host "=== Troubleshooting Tips ===" -ForegroundColor Red
Write-Host "🛠️ COMMON ISSUES:"
Write-Host "• Authentication fails: Check redirect URI and client secret"
Write-Host "• Search not working: Verify Azure AI Search index name and content"
Write-Host "• OpenAI errors: Check model deployment name and endpoint"
Write-Host "• Traditional RAG not responding: Enable RAG_DEBUG=true for detailed logs"
Write-Host "• Semantic Kernel errors: Enable SK_DEBUG=true for plugin debugging"
Write-Host "• Plugin registration fails: Check [SK] Available plugins in logs"
Write-Host "• Embedding model missing: Ensure text-embedding-ada-002 deployment"
Write-Host "• Permission issues: Verify Azure service resource access"
Write-Host "• Python version compatibility: Ensure Python 3.12+ for full SK support"
Write-Host ""

Write-Host "=== Application Features ===" -ForegroundColor Blue
Write-Host "🚀 YOUR DUAL ARCHITECTURE APP INCLUDES:"
Write-Host "• Financial analyst earnings call simulation"
Write-Host "• Traditional RAG implementation with direct Azure API calls"
Write-Host "• Modern Semantic Kernel integration with plugin architecture"
Write-Host "• Four operation modes for architecture comparison:"
Write-Host "  - Search Documents (Traditional)"
Write-Host "  - AI Chat + Search (Traditional RAG)"
Write-Host "  - SK Search (Semantic Kernel)"
Write-Host "  - SK AI Chat + RAG (Modern SK Framework)"
Write-Host "• Dual persona support (CEO & Financial Analyst)"
Write-Host "• Plugin-based extensibility (personas & rag plugins)"
Write-Host "• Enhanced debug logging for both architectures"
Write-Host "• Professional NovaTech branding integration"
Write-Host "• Enterprise-grade Azure AD authentication"
Write-Host "• Responsive Bootstrap UI design"
Write-Host "• Future-proof AI orchestration framework"
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Setup Complete! 🎉" -ForegroundColor Cyan
Write-Host "  Ready for Advanced RAG & Semantic Kernel Demo" -ForegroundColor Cyan
Write-Host "  Compare Traditional vs Modern AI Architectures" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
