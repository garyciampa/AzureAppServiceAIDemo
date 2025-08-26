<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Copilot Instructions for Azure App Service AI Demo

This is a Python Flask web application designed to run on Azure App Service with the following key features:

## Project Structure
- **Flask web application** with Azure AD OAuth authentication
- **Frontend**: Bootstrap-based responsive UI with input/output dialogs
- **Backend**: Flask routes handling authentication and prompt processing
- **Deployment**: Configured for Azure App Service

## Key Components
1. **Azure AD Authentication**: Uses MSAL library for OAuth flow
2. **Input Dialog**: Text area for user prompts with send/clear buttons
3. **Output Dialog**: Display area for responses with clear button
4. **Session Management**: Secure token caching and user sessions

## Development Guidelines
- Follow Flask best practices for route handling and templating
- Use Bootstrap classes for consistent UI styling
- Implement proper error handling for authentication flows
- Keep sensitive configuration in environment variables
- Use async/await patterns for API calls in JavaScript

## Azure Integration
- Configured for Azure App Service deployment
- Uses Azure AD for authentication
- Ready for integration with Azure AI services
- Environment variables for secure configuration

When working on this project, prioritize security, user experience, and Azure best practices.
