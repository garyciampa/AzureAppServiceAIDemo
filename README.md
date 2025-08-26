# Azure App Service AI Demo - Advanced RAG & Semantic Kernel Integration

## 🆕 Recent Changes (August 2025)

- **Dependencies Updated:**
  - All core packages are now up-to-date, including:
    - Flask 3.0.0
    - semantic-kernel 1.35.1
    - openai 1.55.0
    - azure-search-documents 11.4.0
    - msal 1.25.0
  - See `requirements.txt` for full details.

- **Environment Variable Defaults:**
  - `AZURE_OPENAI_API_VERSION` now defaults to `2024-12-01-preview`.
  - `AZURE_SEARCH_INDEX` defaults to `novatech-03` in Semantic Kernel service (override in `.env` as needed).

- **Integration/Status Docs:**
  - New files for Semantic Kernel integration and status tracking are present for future documentation.

- **Codebase Maintenance:**
  - `semantic_kernel_integration.py` is a placeholder for future expansion.
  - All main service and test files are present and organized.

- **No Breaking Changes:**
  - No major architectural changes or breaking updates since last release.

A sophisticated Flask web application featuring Azure AD authentication, dual RAG architectures (traditional and Semantic Kernel), and financial analyst simulation for earnings call interactions with professional corporate branding.

## 🚀 Overview

This application demonstrates cutting-edge AI integration approaches by implementing **both traditional direct API integration and modern Semantic Kernel orchestration** side-by-side. Users can experience and compare different AI architectures while simulating CEO-Financial Analyst earnings call environments using Azure AI services.

### 🎯 **Dual Architecture Design**
- **Traditional Approach**: Direct Azure API calls for search and chat
- **Modern Approach**: Semantic Kernel framework with plugin-based architecture
- **Side-by-Side Comparison**: Experience both approaches in the same application
- **Enterprise Ready**: Production-grade implementations of both patterns

## ✨ Key Features

### 🔐 **Enterprise Authentication**
- **Azure AD Integration**: Secure OAuth 2.0 authentication flow
- **Session Management**: Persistent user sessions with secure token caching
- **Corporate Branding**: Professional enterprise integration and theming

### 🤖 **Dual AI Architecture System**

#### **Traditional RAG Implementation**
- **Direct API Integration**: Classic Azure AI Search + Azure OpenAI approach
- **Search Documents**: Direct document retrieval from Azure AI Search
- **AI Chat + Search**: Traditional RAG pipeline with direct OpenAI calls
- **Performance Optimized**: Streamlined API calls with custom error handling

#### **Semantic Kernel Integration** 🆕
- **Modern AI Orchestration**: Enterprise-grade Semantic Kernel framework
- **Plugin Architecture**: Modular, extensible design with persona and RAG plugins
- **SK Search**: Advanced document search through Semantic Kernel plugins
- **SK AI Chat + RAG**: Modern AI orchestration with enhanced context management
- **Future-Proof Design**: Framework that evolves with AI ecosystem

### 💼 **Enhanced User Experience**
- **Four Operation Modes**: Compare traditional vs modern AI approaches
  - Traditional: Search Documents & AI Chat + Search
  - Modern: SK Search & SK AI Chat + RAG
- **Dual Persona Support**: CEO and Financial Analyst personas with sophisticated role-playing
- **Mode Comparison**: Side-by-side evaluation of different AI architectures
- **Clear Visual Differentiation**: Distinct icons and styling for each approach
- **Real-time Switching**: Dynamic mode selection with instant feedback

### 🏗️ **Advanced Technical Features**
- **Plugin System**: Extensible architecture for adding new AI capabilities
- **Enhanced Error Handling**: Comprehensive fallback patterns and debug logging
- **Service Abstraction**: Clean separation between AI services and business logic
- **Status Monitoring**: Real-time monitoring of all AI services and frameworks
- **Debug Transparency**: Detailed logging for both traditional and SK approaches

## 📋 Prerequisites

### **Development Environment**
- **Python 3.12+** (Required for full Semantic Kernel compatibility)
- **Azure Subscription** with appropriate service quotas
- **Visual Studio Code** or your preferred IDE
- **Git** for version control

### **Azure Resources Required**
- **Azure AD App Registration** with OAuth 2.0 permissions
- **Azure OpenAI Service** with GPT-3.5-Turbo or GPT-4 deployment
- **Azure AI Search Service** with configured index (`azureblob-index`)
- **Azure App Service** (for production deployment)

### **Development Libraries**
- **Traditional Stack**: Flask 3.0.0, Azure SDK libraries, MSAL authentication
- **Modern Stack**: Semantic Kernel 1.35.1, enhanced AI orchestration framework
- **UI Framework**: Bootstrap 5.3 via CDN, responsive design components
- **Both Approaches**: Unified authentication and session management

## 🛠️ Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd DemoAppServiceAi
pip install -r requirements.txt
```

### 2. Azure Services Configuration

#### Azure AI Search Setup
- Create an Azure AI Search service
- Index your documents with the name: `azureblob-index`
- Note the service endpoint and admin key

#### Azure OpenAI Setup
- Deploy a GPT-3.5-Turbo model in Azure OpenAI
- Note the endpoint, API key, and deployment name

#### Azure AD Application Registration
- Register application in Azure AD
- Configure redirect URI: `http://localhost:5000/getAToken` (development)
- Generate client secret and note credentials

### 3. Environment Configuration

Create a `.env` file with comprehensive configuration:

```env
# Azure AD Authentication
AZURE_CLIENT_ID=your-azure-ad-client-id
AZURE_CLIENT_SECRET=your-azure-ad-client-secret
AZURE_TENANT_ID=your-azure-tenant-id

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your-search-admin-key
AZURE_SEARCH_INDEX=azureblob-index

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-service.openai.azure.com
AZURE_OPENAI_KEY=your-openai-api-key
AZURE_OPENAI_MODEL=your-gpt-35-turbo-deployment-name

# Flask Application Settings
SECRET_KEY=your-session-secret-key
FLASK_DEBUG=true
RAG_DEBUG=true

# Network Configuration
REDIRECT_URI=http://localhost:5000/getAToken
```

### 4. Run the Application
```bash
python app.py
```

Navigate to `http://localhost:5000` and experience the financial analyst simulation.

## 📁 Project Architecture

```
DemoAppServiceAi/
├── app.py                         # Main Flask application with RAG & SK integration
├── env.ps1                        # PowerShell helper to load .env (resolves $env:VAR placeholders)
├── .env.example                   # Environment variables template (do not commit secrets)
├── .env                           # Local environment config (ignored by git; optional)
├── azure-setup.ps1                # Setup script for Azure resources (documentation + azure cli snippets)
├── Procfile                       # Azure App Service startup configuration
├── requirements.txt               # Python dependencies
├── requirements_sk.txt            # Semantic Kernel specific dependencies
├── runtime.txt                    # Python runtime specification
├── semantic_kernel_integration.py # Semantic Kernel integration helpers (placeholder/extension)
├── semantic_kernel_service.py     # Semantic Kernel service implementation
├── final_test.py                  # Local testing script
├── templates/                     # Jinja2 HTML templates (index, login, auth_error)
│   ├── index.html
│   ├── login.html
│   └── auth_error.html
├── __azurite_db_queue__.json      # Azurite emulator storage (local, not tracked)
├── __azurite_db_queue_extent__.json
└── __queuestorage__/              # Azurite queue storage files (local, not tracked)
```

> Notes:
> - `.env` is intentionally a local file and is included in `.gitignore`. Use `.env.example` as a template.
> - To load local environment variables into PowerShell (including expanding `$env:VARIABLE` references), dot-source `env.ps1` from the project root:
>   `. .\env.ps1`

## 🧠 Dual Architecture System

### 🔄 **Architecture Overview**
This application implements two parallel AI architectures, allowing direct comparison between traditional and modern approaches:

#### **Traditional RAG Implementation** 
- **Direct API Integration**: Classic Azure services with custom orchestration
- **Performance Optimized**: Streamlined API calls with minimal overhead
- **Proven Stability**: Battle-tested approach with comprehensive error handling

#### **Semantic Kernel Implementation** 🆕
- **Modern AI Orchestration**: Enterprise-grade framework with plugin architecture
- **Future-Proof Design**: Framework that evolves with AI ecosystem
- **Enhanced Capabilities**: Plugin-based extensibility and advanced context management

### 📊 **Traditional RAG Pipeline Flow**
1. **User Query Reception**: Flask receives user prompt via POST `/process_chat_query`
2. **Document Retrieval**: Azure AI Search finds relevant context documents
3. **Context Extraction**: System extracts up to 4000 characters of relevant content
4. **Prompt Enhancement**: Context combined with persona-specific system message
5. **AI Processing**: Direct Azure OpenAI API call generates response
6. **Response Delivery**: Formatted response returned to user interface

### 🔧 **Semantic Kernel Pipeline Flow** 
1. **User Query Reception**: Flask receives user prompt via POST `/process_sk_chat`
2. **Plugin Orchestration**: SK framework coordinates plugin execution
3. **RAG Plugin Execution**: `search_documents` function retrieves context
4. **Persona Plugin Selection**: CEO or Financial Analyst persona applied
5. **SK AI Processing**: Modern chat completion API with enhanced context
6. **Response Delivery**: Plugin-orchestrated response with enhanced formatting

### 🎭 **Enhanced Persona System**
Both architectures support sophisticated role-playing simulations:

#### **CEO Persona**
```python
# Traditional Implementation
system_message = """You are the CEO of a major company participating in a quarterly earnings call..."""

# Semantic Kernel Plugin
@kernel_function(description="CEO persona for earnings calls")
def ceo_persona(self, context: str, query: str) -> str:
    """Sophisticated CEO role-playing with enhanced context management"""
```

#### **Financial Analyst Persona**
```python
# Traditional Implementation  
system_message = """You are a financial analyst participating in a quarterly earnings call..."""

# Semantic Kernel Plugin
@kernel_function(description="Financial analyst persona for earnings analysis")
def analyst_persona(self, context: str, query: str) -> str:
    """Advanced analyst questioning with strategic follow-up patterns"""
```

### 🔌 **Semantic Kernel Plugin Architecture**

#### **Plugin Registration System**
```python
# Plugin initialization in semantic_kernel_service.py
self.kernel.add_function(function=search_documents, plugin_name="rag")
self.kernel.add_function(function=ceo_persona, plugin_name="personas") 
self.kernel.add_function(function=analyst_persona, plugin_name="personas")
```

#### **Available Plugins**
- **`rag` Plugin**: Document search and retrieval capabilities
- **`personas` Plugin**: CEO and Financial Analyst role-playing functions
- **Extensible Design**: Framework ready for additional custom plugins

## 🔧 Technical Implementation

### **Core Components Overview**

#### **Dual Service Architecture (`app.py`)**
- **Traditional Routes**: `/process_search`, `/process_chat_query` for direct API integration
- **Semantic Kernel Routes**: `/process_sk_search`, `/process_sk_chat` for modern orchestration
- **Status Monitoring**: Real-time monitoring of both AI frameworks
- **Graceful Degradation**: Fallback patterns when services are unavailable

#### **Authentication Flow (Shared)**
- **MSAL Integration**: Azure AD OAuth 2.0 for enterprise authentication
- **Secure Session Management**: Persistent user sessions with token caching
- **Automatic Token Refresh**: Seamless credential renewal

### **Traditional Implementation**

#### **Direct RAG Processing (`process_chat_query()`)**
```python
@app.route('/process_chat_query', methods=['POST'])
def process_chat_query():
    # Direct Azure AI Search integration
    search_client = azure_search_client.get_search_client()
    
    # Custom OpenAI client with httpx proxy workaround
    openai_client = azure_chat_client.get_openai_client()
    
    # Manual context optimization (4000 character limit)
    # Persona-specific system message generation
    # Direct API orchestration
```

#### **Search Implementation (`process_search()`)**
```python
@app.route('/process_search', methods=['POST'])  
def process_search():
    # Direct Azure AI Search client
    # Manual result formatting and filtering
    # Traditional error handling patterns
```

### **Semantic Kernel Implementation** 🆕

#### **Modern RAG Processing (`process_sk_chat()`)**
```python
@app.route('/process_sk_chat', methods=['POST'])
def process_sk_chat():
    # Semantic Kernel service initialization
    sk_service = semantic_kernel_service.SemanticKernelService()
    
    # Plugin-based orchestration
    # Enhanced context management
    # Modern chat completion API
```

#### **Plugin-Based Search (`process_sk_search()`)**
```python
@app.route('/process_sk_search', methods=['POST'])
def process_sk_search():
    # Semantic Kernel plugin execution
    # Enhanced search with AI orchestration
    # Plugin-based result processing
```

### **Service Layer Architecture**

#### **SemanticKernelService Class**
```python
class SemanticKernelService:
    def __init__(self):
        self.kernel = sk.Kernel()
        self._register_plugins()
        
    def _register_plugins(self):
        # RAG plugin for document search
        self.kernel.add_function(function=search_documents, plugin_name="rag")
        
        # Persona plugins for role-playing
        self.kernel.add_function(function=ceo_persona, plugin_name="personas")
        self.kernel.add_function(function=analyst_persona, plugin_name="personas")
```

### **Enhanced Debug System**
Both architectures support comprehensive debugging:

#### **Traditional Debug Logging**
```python
RAG_DEBUG = os.getenv('RAG_DEBUG', 'false').lower() == 'true'
# [CLIENT] - Search service interactions
# [OPENAI] - AI model processing  
# RAG Step X - Pipeline stage tracking
```

#### **Semantic Kernel Debug Logging**
```python
SK_DEBUG = os.getenv('SK_DEBUG', 'false').lower() == 'true'
# [SK] - Kernel operations and plugin execution
# [SK_PLUGIN] - Individual plugin performance
# [SK_CHAT] - Chat completion API interactions
```

## 🚀 Deployment Guide

### Azure App Service Deployment

#### Using Azure CLI
```bash
# Create resource group
az group create --name myResourceGroup --location "East US"

# Create App Service plan
az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --sku B1 --is-linux

# Create web app
az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name myUniqueAppName --runtime "PYTHON|3.12"

# Configure environment variables
az webapp config appsettings set --resource-group myResourceGroup --name myUniqueAppName \
  --settings \
  AZURE_CLIENT_ID="your-client-id" \
  AZURE_CLIENT_SECRET="your-client-secret" \
  AZURE_TENANT_ID="your-tenant-id" \
  AZURE_SEARCH_ENDPOINT="your-search-endpoint" \
  AZURE_SEARCH_KEY="your-search-key" \
  AZURE_OPENAI_ENDPOINT="your-openai-endpoint" \
  AZURE_OPENAI_KEY="your-openai-key" \
  SECRET_KEY="your-secret-key"

# Deploy from local git
git remote add azure <deployment-url>
git push azure main
```

#### Production Environment Variables
Update redirect URI for production:
```env
REDIRECT_URI=https://your-app-name.azurewebsites.net/getAToken
```

## 🎯 Usage Guide

### **Getting Started**
1. **Authentication**: Click "Sign in with Microsoft" for Azure AD authentication
2. **Architecture Selection**: Choose your preferred AI approach for comparison
3. **Mode Selection**: Pick from four available operation modes
4. **Persona Selection**: Choose Financial Analyst or CEO persona (Chat modes only)
5. **Query Submission**: Enter financial or business questions in the input area
6. **Response Analysis**: Compare responses between traditional and modern approaches

### **Four Operation Modes** ⚡

#### **Traditional Approaches**
- **🔍 Search Documents**: Direct Azure AI Search integration for document retrieval
- **💬 AI Chat + Search**: Classic RAG pipeline with direct OpenAI API calls

#### **Modern Semantic Kernel Approaches** 🆕
- **🔍 SK Search**: Plugin-based document search with AI orchestration
- **🤖 SK AI Chat + RAG**: Advanced plugin-orchestrated responses with enhanced context

### **Architecture Comparison Guide**

#### **When to Use Traditional Approach**
- **Performance Priority**: Optimized for speed with minimal overhead
- **Proven Stability**: Battle-tested approach with comprehensive error handling
- **Simple Integration**: Direct API calls with straightforward debugging
- **Resource Efficiency**: Lower memory footprint and faster response times

#### **When to Use Semantic Kernel Approach** 🚀
- **Future-Proof Development**: Framework that evolves with AI ecosystem
- **Enhanced Capabilities**: Plugin-based extensibility and advanced context management
- **Enterprise Features**: Modern AI orchestration with sophisticated error handling
- **Scalable Architecture**: Framework designed for complex AI workflows

### **Example Interactions**

#### **Financial Analyst Persona** (Both Architectures)
```
Traditional Query: "What were our Q3 revenue numbers?"
Traditional Response: Direct API response with extracted context...

SK Query: "What were our Q3 revenue numbers?"  
SK Response: Plugin-orchestrated response with enhanced formatting...
```

**Sample Questions:**
- "Thanks, this is Sarah from Goldman Sachs. Can you walk us through the revenue performance this quarter?"
- "Following up on margins - what specific cost management initiatives drove the improvement?"
- "Looking at your forward guidance, what assumptions are you making about market conditions?"

#### **CEO Persona** (Both Architectures)
```
Query: "How is our market expansion strategy progressing?"

Traditional Response: "Thank you for that question. Our market expansion initiatives are exceeding expectations..."

SK Response: [Enhanced with plugin-based context management and sophisticated formatting]
```

### **Debug Mode Comparison**

#### **Traditional Debug**
```env
RAG_DEBUG=true
FLASK_DEBUG=true
```
Output: `[CLIENT]`, `[OPENAI]`, `RAG Step X` tracking

#### **Semantic Kernel Debug**
```env
SK_DEBUG=true
FLASK_DEBUG=true  
```
Output: `[SK]`, `[SK_PLUGIN]`, `[SK_CHAT]` detailed logging

### **Performance Monitoring**
Real-time status indicators for both architectures:
- **Traditional Services**: Azure AI Search + Azure OpenAI connectivity
- **Semantic Kernel Services**: Plugin availability + Framework status
- **Shared Services**: Authentication + Session management

## 🔒 Security Considerations

### Authentication Security
- OAuth 2.0 with Azure AD for enterprise-grade authentication
- Secure session token management with automatic refresh
- Protected routes requiring valid authentication

### Data Protection
- Environment variables for sensitive configuration
- No credential storage in source code
- Secure Azure service-to-service communication

### Production Best Practices
- Azure Key Vault integration for credential management
- HTTPS enforcement for all communications
- Regular dependency updates and security scanning
- Proper CORS configuration for cross-origin requests

## 🧪 Development and Testing

### Local Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Set up pre-commit hooks (optional)
pre-commit install

# Run with debug mode
python app.py
```

### VS Code Integration
Configured tasks for seamless development:
```json
{
  "label": "Run Flask App",
  "type": "shell",
  "command": "python",
  "args": ["app.py", "--debug"],
  "group": "build",
  "isBackground": true
}
```

### Testing RAG Functionality
The application includes comprehensive logging for debugging:
- Document retrieval verification
- Context extraction validation
- AI response generation tracking
- Error condition handling

## 🎭 Persona System

### Overview
The application features a sophisticated persona system that allows users to experience earnings call interactions from different perspectives:

### **Financial Analyst Persona**
- **Role**: Probing financial analyst asking detailed questions
- **Behavior**: Professional, persistent, data-driven questioning
- **Focus Areas**:
  - Revenue growth and segment performance
  - Margin trends and cost management
  - Capital allocation and investment priorities
  - Market share and competitive positioning
  - Forward guidance and outlook assumptions

### **CEO Persona**
- **Role**: Company executive providing strategic insights
- **Behavior**: Confident, authoritative, transparent leadership
- **Response Style**:
  - Acknowledges questions professionally
  - Provides detailed explanations with metrics
  - References strategic initiatives
  - Demonstrates business understanding

### **Implementation**
```python
# Persona selection in frontend
const persona = document.querySelector('input[name="personaSelection"]:checked')?.value || 'analyst';

# Backend persona handling
def get_system_message_for_persona(persona):
    if persona == "ceo":
        return """You are the CEO of a major company..."""
    else:  # analyst
        return """You are a financial analyst..."""
```

### **Usage**
1. Select "Chat+RAG" mode to enable persona selection
2. Choose between "Financial Analyst" or "CEO" persona
3. Enter your query - the AI will respond according to the selected persona
4. Experience realistic earnings call interactions

## 📈 Monitoring and Observability

### Application Insights Integration
Ready for Azure Application Insights integration:
- Request tracking and performance monitoring
- Exception and error logging
- User interaction analytics
- Custom telemetry for RAG pipeline

### Health Checks
Built-in status endpoints for monitoring:
- Authentication service connectivity
- Azure AI Search availability
- Azure OpenAI service status

## 🤝 Contributing

### Development Guidelines
1. Follow Flask best practices for route handling
2. Implement proper error handling for all Azure service interactions
3. Use Bootstrap classes for consistent UI styling
4. Keep sensitive configuration in environment variables
5. Add comprehensive logging for debugging

### Code Quality Standards
- Type hints for function parameters and returns
- Comprehensive error handling with user-friendly messages
- Security-first approach for all external integrations
- Performance optimization for AI service calls

## 📚 Additional Resources

### **Azure Documentation**
- [Azure AD Authentication](https://docs.microsoft.com/en-us/azure/active-directory/)
- [Azure AI Search](https://docs.microsoft.com/en-us/azure/search/)
- [Azure OpenAI Service](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/)

### **Semantic Kernel Resources** 🆕
- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [Semantic Kernel Python SDK](https://pypi.org/project/semantic-kernel/)
- [Plugin Development Guide](https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/)
- [AI Orchestration Patterns](https://learn.microsoft.com/en-us/semantic-kernel/concepts/ai-orchestration/)

### **Flask Resources**
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MSAL Python Library](https://msal-python.readthedocs.io/)
- [Bootstrap Framework](https://getbootstrap.com/)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For technical support or questions:

### **Traditional Architecture Debugging**
1. Check debug logs: `RAG_DEBUG=true`
2. Verify Azure service connectivity and credentials
3. Review authentication flow and session management
4. Consult Azure service documentation for API issues

### **Semantic Kernel Architecture Debugging** 🆕
1. Enable SK debugging: `SK_DEBUG=true`
2. Check plugin registration: Look for `[SK] Available plugins: ['personas', 'rag']`
3. Monitor plugin execution: Track `[SK_PLUGIN]` messages
4. Verify chat completion API: Review `[SK_CHAT]` interactions

### **General Troubleshooting**
- Compare responses between traditional and SK approaches
- Check Azure service quotas and rate limits
- Verify Python 3.12+ environment compatibility
- Review plugin availability and registration status

---

**Built with ❤️ using Azure AI Services, Semantic Kernel, and Flask**
