"""
Flask web application with Azure AD authentication and Azure AI Search integration
"""
import os
import uuid
import json
import argparse
import sys

# Parse command line arguments early
parser = argparse.ArgumentParser(description='Flask Azure AI Demo App')
parser.add_argument('--debug', action='store_true', help='Enable debug mode and verbose logging')
args = parser.parse_args()

# Set debug flag - check command line arg first, then environment variable, then default to False
DEBUG_MODE = args.debug or os.environ.get('FLASK_DEBUG', '').lower() in ('true', '1', 'yes', 'on')

# RAG-specific debug flag (can be enabled independently)
RAG_DEBUG = DEBUG_MODE or os.environ.get('RAG_DEBUG', '').lower() in ('true', '1', 'yes', 'on')

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import msal
import requests
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Try to import Azure Search packages with fallback
try:
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_SEARCH_AVAILABLE = True
    if DEBUG_MODE:
        print("Azure Search packages loaded successfully")
except ImportError as e:
    AZURE_SEARCH_AVAILABLE = False
    if DEBUG_MODE:
        print(f"Azure Search packages not available: {e}")
    
    # Create dummy classes for graceful degradation
    class SearchClient:
        def __init__(self, *args, **kwargs):
            pass
        def search(self, *args, **kwargs):
            raise Exception("Azure Search not available - install azure-search-documents package")
        def get_document_count(self):
            raise Exception("Azure Search not available - install azure-search-documents package")
    
    class AzureKeyCredential:
        def __init__(self, *args, **kwargs):
            pass

# Try to import Semantic Kernel functionality with fallback
try:
    from semantic_kernel_service import (
        sk_process_chat_query,
        sk_process_search_query,
        sk_get_status,
        get_semantic_kernel_service
    )
    SEMANTIC_KERNEL_AVAILABLE = True
    if DEBUG_MODE:
        print("Semantic Kernel service loaded successfully")
except ImportError as e:
    SEMANTIC_KERNEL_AVAILABLE = False
    if DEBUG_MODE:
        print(f"Semantic Kernel service not available: {e}")
    
    # Create dummy functions for graceful degradation
    def sk_process_chat_query(*args, **kwargs):
        return {"response": "Semantic Kernel not available", "status": "error", "framework": "semantic_kernel"}
    
    def sk_process_search_query(*args, **kwargs):
        return {"response": "Semantic Kernel not available", "status": "error", "framework": "semantic_kernel"}
    
    def sk_get_status(*args, **kwargs):
        return {"initialized": False, "error": "Semantic Kernel not available"}
    
    def get_semantic_kernel_service(*args, **kwargs):
        return None

# Try to import Azure OpenAI packages with fallback
try:
    from openai import AzureOpenAI
    AZURE_OPENAI_AVAILABLE = True
    if DEBUG_MODE:
        print("Azure OpenAI packages loaded successfully")
except ImportError as e:
    AZURE_OPENAI_AVAILABLE = False
    if DEBUG_MODE:
        print(f"Azure OpenAI packages not available: {e}")
    
    # Create dummy class for graceful degradation
    class AzureOpenAI:
        def __init__(self, *args, **kwargs):
            pass
        def chat(self):
            raise Exception("Azure OpenAI not available - install openai package")

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', str(uuid.uuid4()))
app.config['COMPANY_URL'] = os.environ.get('COMPANY_URL', 'https://www.novatech-demo.test/')

@app.context_processor
def inject_company_url():
    """Inject COMPANY_URL into all templates so external links can be managed from configuration or env var."""
    from flask import current_app
    return dict(COMPANY_URL=current_app.config.get('COMPANY_URL'))

# Azure AD Configuration
CLIENT_ID = os.environ.get('AZURE_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET', '')
TENANT_ID = os.environ.get('AZURE_TENANT_ID', '')
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["User.Read"]
REDIRECT_PATH = "/getAToken"

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT = os.environ.get('AZURE_SEARCH_ENDPOINT', '')
AZURE_SEARCH_KEY = os.environ.get('AZURE_SEARCH_KEY', '')
AZURE_SEARCH_INDEX = os.environ.get('AZURE_SEARCH_INDEX', 'novatech-03')

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT', '')
AZURE_OPENAI_KEY = os.environ.get('AZURE_OPENAI_KEY', '')
AZURE_OPENAI_MODEL = os.environ.get('AZURE_OPENAI_MODEL', 'gpt-35-turbo')
AZURE_OPENAI_DEPLOYMENT = os.environ.get('AZURE_OPENAI_DEPLOYMENT', 'gpt-35-turbo')
AZURE_OPENAI_API_VERSION = os.environ.get('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')

if DEBUG_MODE:
    print("CLIENT_ID:", CLIENT_ID)
    print("CLIENT_SECRET:", CLIENT_SECRET)
    print("TENANT_ID:", TENANT_ID)
    print("AUTHORITY:", AUTHORITY)
    print("AZURE_SEARCH_ENDPOINT:", AZURE_SEARCH_ENDPOINT)
    print("AZURE_SEARCH_INDEX:", AZURE_SEARCH_INDEX)
    print("AZURE_SEARCH_AVAILABLE:", AZURE_SEARCH_AVAILABLE)
    print("AZURE_OPENAI_ENDPOINT:", AZURE_OPENAI_ENDPOINT)
    print("AZURE_OPENAI_MODEL:", AZURE_OPENAI_MODEL)
    print("AZURE_OPENAI_AVAILABLE:", AZURE_OPENAI_AVAILABLE)
    print("SEMANTIC_KERNEL_AVAILABLE:", SEMANTIC_KERNEL_AVAILABLE)
    print("RAG_DEBUG:", RAG_DEBUG)
def _load_cache():
    # Don't use session for token cache to avoid large cookies
    cache = msal.SerializableTokenCache()
    return cache

def _save_cache(cache):
    # Don't save cache to session to avoid large cookies
    pass

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=authority or AUTHORITY,
        client_credential=CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))

# Azure AI Search Helper Functions
def get_search_client():
    """Create and return Azure Search client"""
    if not AZURE_SEARCH_AVAILABLE:
        if DEBUG_MODE:
            print("Azure Search packages not available")
        return None
        
    try:
        credential = AzureKeyCredential(AZURE_SEARCH_KEY)
        search_client = SearchClient(
            endpoint=AZURE_SEARCH_ENDPOINT,
            index_name=AZURE_SEARCH_INDEX,
            credential=credential
        )
        return search_client
    except Exception as e:
        if DEBUG_MODE:
            print(f"Error creating search client: {e}")
        return None

def search_documents(query, top=5):
    """Search documents using Azure AI Search"""
    if not AZURE_SEARCH_AVAILABLE:
        return {
            "error": "Azure Search packages not installed. Please run: pip install azure-search-documents",
            "query": query,
            "status": "error"
        }
        
    try:
        search_client = get_search_client()
        if not search_client:
            return {"error": "Failed to create search client"}
        
        # Perform the search
        results = search_client.search(
            search_text=query,
            top=top,
            include_total_count=True
        )
        
        # Process the results
        documents = []
        total_count = 0
        
        if DEBUG_MODE:
            print(f"[SEARCH] Processing search results for query: '{query}'")
            sys.stdout.flush()
        
        for result in results:
            total_count = getattr(results, 'get_count', lambda: 0)()
            doc = {
                "score": result.get("@search.score", 0),
            }
            
            if DEBUG_MODE:
                print(f"[SEARCH] Result fields: {list(result.keys())}")
                sys.stdout.flush()
            
            # Add all fields from the document dynamically
            for key, value in result.items():
                if not key.startswith("@"):
                    doc[key] = value
                    if DEBUG_MODE:
                        print(f"[SEARCH] Added field '{key}': {str(value)[:100]}...")
                        sys.stdout.flush()
            
            documents.append(doc)
        
        if DEBUG_MODE:
            print(f"[SEARCH] Total documents processed: {len(documents)}")
            print(f"[SEARCH] Total count from index: {total_count}")
            sys.stdout.flush()
        
        return {
            "documents": documents,
            "total_count": total_count,
            "query": query,
            "status": "success"
        }
        
    except Exception as e:
        if DEBUG_MODE:
            print(f"Error searching documents: {e}")
        return {
            "error": f"Search error: {str(e)}",
            "query": query,
            "status": "error"
        }

# Azure OpenAI Helper Functions
def get_system_message_for_persona(persona):
    """Get the appropriate system message based on the selected persona"""
    
    if persona == "ceo":
        return """You are the CEO of a major company participating in a quarterly earnings call with financial analysts.

Your role is to provide detailed, professional responses about the company's quarterly performance, guidance, and strategy when answering analyst questions.

### Behavior Guidelines:
- Respond as a confident and knowledgeable CEO during an earnings call
- Provide specific insights about company performance, strategy, and outlook
- Reference actual data from financial documents when available
- Address analyst concerns with transparency and strategic vision
- Maintain a professional, authoritative tone
- Give forward-looking guidance when appropriate

### Response Style:
- Start responses acknowledging the question (e.g., "Thank you for that question...")
- Be informative and detailed in your explanations
- Include specific metrics, percentages, or financial figures when relevant
- Reference strategic initiatives and company direction
- End with confidence about the company's future prospects

### Constraints:
- Stay in character as a CEO throughout the interaction
- Base responses on the provided document context when available
- If specific data isn't available, acknowledge this professionally
- Maintain optimism while being realistic about challenges

Provide comprehensive, CEO-level responses that demonstrate deep understanding of the business and strategic vision."""

    else:  # Default to analyst persona
        return """You are a financial analyst participating in a quarterly earnings call with a company's CEO.

Your role is to ask relevant, probing questions about the company's quarterly performance, guidance, and strategy to help evaluate the company's prospects and performance.

### Behavior Guidelines:
- Begin conversations professionally, stating your firm name (e.g., "Thanks, this is Jamie from Morgan Stanley...")
- Ask specific, data-driven questions related to the quarterly report
- Follow up with 2-3 additional questions based on the CEO's responses
- Be professional but persistent in seeking detailed information
- Reference prior quarters, guidance, or industry benchmarks when relevant

### Question Types to Focus On:
- Revenue growth and segment performance
- Margin trends and cost management
- Capital allocation and investment priorities
- Market share and competitive positioning
- Forward guidance and outlook assumptions
- Key performance indicators and operational metrics

### Tone:
- Neutral and analytical — professional but not adversarial
- Persistent in seeking clarity on important metrics
- Respectful but thorough in your questioning approach

### Constraints:
- Your role is to ASK questions, not to provide answers or explanations
- Stay focused on financial and operational performance topics
- After 3-4 question cycles, thank the CEO and yield time gracefully

Stay fully in character as a financial analyst throughout the simulation."""

def get_openai_client():
    """Create and return Azure OpenAI client"""
    if not AZURE_OPENAI_AVAILABLE:
        if DEBUG_MODE:
            print("Azure OpenAI packages not available")
        return None
        
    try:
        # Validate required configuration
        if not AZURE_OPENAI_KEY:
            if RAG_DEBUG:
                print("[CLIENT] Azure OpenAI API key not configured")
                sys.stdout.flush()
            return None
            
        if not AZURE_OPENAI_ENDPOINT:
            if RAG_DEBUG:
                print("[CLIENT] Azure OpenAI endpoint not configured")
                sys.stdout.flush()
            return None
        
        if RAG_DEBUG:
            print(f"[CLIENT] Creating OpenAI client with endpoint: {AZURE_OPENAI_ENDPOINT}")
            print(f"[CLIENT] API version: {AZURE_OPENAI_API_VERSION}")
            sys.stdout.flush()
        
        # Import httpx to create a custom client without proxies
        import httpx
        
        # Create a custom HTTP client without proxy support to avoid the proxies parameter issue
        http_client = httpx.Client(
            timeout=30.0,
            follow_redirects=True
        )
        
        if RAG_DEBUG:
            print(f"[CLIENT] Created custom HTTP client")
            sys.stdout.flush()
        
        # Create client with explicit parameters and custom HTTP client
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            http_client=http_client
        )
        
        if RAG_DEBUG:
            print(f"[CLIENT] AzureOpenAI client created successfully")
            sys.stdout.flush()
        
        return client
    except TypeError as e:
        if RAG_DEBUG:
            print(f"[CLIENT] TypeError creating OpenAI client (parameter issue): {e}")
            sys.stdout.flush()
        # Fallback: try without custom http_client
        try:
            if RAG_DEBUG:
                print(f"[CLIENT] Trying fallback without custom HTTP client...")
                sys.stdout.flush()
            client = AzureOpenAI(
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION,
                azure_endpoint=AZURE_OPENAI_ENDPOINT
            )
            if RAG_DEBUG:
                print(f"[CLIENT] Fallback client creation successful")
                sys.stdout.flush()
            return client
        except Exception as fallback_e:
            if RAG_DEBUG:
                print(f"[CLIENT] Fallback client creation also failed: {fallback_e}")
                sys.stdout.flush()
            return None
    except Exception as e:
        if RAG_DEBUG:
            print(f"[CLIENT] Error creating OpenAI client: {e}")
            sys.stdout.flush()
        return None

def get_chat_completion(query, system_message="You are simulating a financial analyst participating in a quarterly earnings call. The user will take on the role of the CEO.\n\nYour role is to ask relevant, and realistic questions about the company's quarterly performance, guidance, and strategy, in order to help the CEO practice responding during an analyst call.\n\n### Behavior Guidelines:\n- Begin the conversation by thanking the CEO and stating your firm name (e.g., \"Thanks, this is Jamie from Morgan Stanley...\").\n- Ask specific, data-driven questions related to the quaterly report.\n- Ask 2–3 follow-up questions based on the CEO's responses.\n- Be professional\n- Reference prior quarters or industry benchmarks when relevant.\n\n### Tone:\n- Neutral and analytical — not adversarial, but persistent.\n\n### Constraints:\n- Do not answer questions — your role is to ask, not to explain.\n\n### Exit Criteria:\n- After ~3–4 full question-and-follow-up cycles, thank the CEO and yield to the next analyst in the queue (e.g., \"Thanks. I'll pass it on.\").\n\nStay fully in character as a financial analyst throughout the simulation.", max_tokens=500, temperature=0.7):
    """Get chat completion using Azure OpenAI"""
    if not AZURE_OPENAI_AVAILABLE:
        return {
            "error": "Azure OpenAI packages not installed. Please run: pip install openai",
            "query": query,
            "status": "error"
        }
    
    try:
        client = get_openai_client()
        if not client:
            if RAG_DEBUG:
                print("[OPENAI] Failed to create OpenAI client")
                sys.stdout.flush()
            return {"error": "Failed to create OpenAI client", "query": query, "status": "error"}
        
        if RAG_DEBUG:
            print(f"[OPENAI] Client created successfully")
            print(f"[OPENAI] Using deployment: {AZURE_OPENAI_DEPLOYMENT}")
            print(f"[OPENAI] Query length: {len(query)} characters")
            sys.stdout.flush()
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query}
        ]
        
        if RAG_DEBUG:
            print(f"[OPENAI] Messages prepared:")
            print(f"  - System message length: {len(system_message)} characters")
            print(f"  - User message length: {len(query)} characters")
            print(f"  - Max tokens: {max_tokens}, Temperature: {temperature}")
            sys.stdout.flush()
        
        if RAG_DEBUG:
            print(f"[OPENAI] Calling OpenAI API...")
            sys.stdout.flush()
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if RAG_DEBUG:
            print(f"[OPENAI] API call successful!")
            print(f"[OPENAI] Response type: {type(response)}")
            print(f"[OPENAI] Response has choices: {hasattr(response, 'choices') and len(response.choices) > 0}")
            if hasattr(response, 'choices') and len(response.choices) > 0:
                print(f"[OPENAI] First choice message content length: {len(response.choices[0].message.content) if response.choices[0].message.content else 0}")
                print(f"[OPENAI] Content preview: {response.choices[0].message.content[:100] if response.choices[0].message.content else 'None'}...")
            if hasattr(response, 'usage'):
                print(f"[OPENAI] Token usage: {response.usage}")
            sys.stdout.flush()
        
        # Check if we got a valid response
        if not response.choices or not response.choices[0].message.content:
            if RAG_DEBUG:
                print(f"[OPENAI] Warning: Empty or invalid response from OpenAI")
                print(f"[OPENAI] Response object: {response}")
                sys.stdout.flush()
            return {
                "error": "OpenAI returned empty response",
                "query": query,
                "status": "error"
            }
        
        content = response.choices[0].message.content
        if RAG_DEBUG:
            print(f"[OPENAI] Successfully extracted content: {len(content)} characters")
            sys.stdout.flush()
        
        return {
            "content": content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            },
            "query": query,
            "status": "success"
        }
        
    except Exception as e:
        if RAG_DEBUG:
            print(f"[OPENAI] Exception in chat completion: {e}")
            print(f"[OPENAI] Exception type: {type(e)}")
            import traceback
            print(f"[OPENAI] Full traceback:")
            traceback.print_exc()
            sys.stdout.flush()
        return {
            "error": f"Chat completion error: {str(e)}",
            "query": query,
            "status": "error"
        }

def process_chat_query(query, persona="analyst"):
    """
    Process user query using Retrieval-Augmented Generation (RAG)
    First search Azure AI Search for relevant context, then use Azure OpenAI for chat completion
    """
    try:
        # Get the appropriate system message based on persona
        system_message = get_system_message_for_persona(persona)
        
        if RAG_DEBUG:
            print(f"RAG Step 0: Using {persona.upper()} persona")
            print(f"RAG Step 1: Searching index for context related to: {query}")
            sys.stdout.flush()
        
        search_results = search_documents(query, top=3)  # Get top 3 most relevant documents
        
        # Step 2: Extract context from search results
        context_chunks = []
        if RAG_DEBUG:
            print(f"RAG Step 2: Search results structure: {type(search_results)}")
            print(f"RAG Step 2: Search results keys: {search_results.keys() if isinstance(search_results, dict) else 'Not a dict'}")
            print(f"RAG Step 2: Full search results: {search_results}")
            sys.stdout.flush()
            
        if search_results and search_results.get("status") == "success":
            documents = search_results.get("documents", [])
            if RAG_DEBUG:
                print(f"RAG Step 2: Documents type: {type(documents)}, length: {len(documents) if documents else 0}")
                if documents:
                    print(f"RAG Step 2: First document keys: {documents[0].keys() if documents[0] else 'No keys'}")
                sys.stdout.flush()
                
            if documents and len(documents) > 0:
                if RAG_DEBUG:
                    print(f"RAG Step 2: Found {len(documents)} relevant documents")
                    sys.stdout.flush()
                
                for idx, result in enumerate(documents):
                    # Try multiple possible field names for content
                    content = (result.get('content') or 
                              result.get('Content') or 
                              result.get('text') or 
                              result.get('Text') or 
                              result.get('description') or 
                              result.get('Description') or
                              str(result))  # Fallback to string representation
                    
                    if RAG_DEBUG:
                        print(f"  - Document {idx+1} fields: {list(result.keys())}")
                        print(f"  - Document {idx+1} content length: {len(str(content)) if content else 0}")
                        sys.stdout.flush()
                    
                    if content and str(content).strip():
                        # Use full content to ensure we capture all important information
                        content_str = str(content)
                        # Use full content but limit to 4000 characters to stay within token limits
                        # This should be enough to capture the complete document sections
                        truncated_content = content_str[:4000] + ("..." if len(content_str) > 4000 else "")
                        context_chunks.append(f"Document {idx+1}:\n{truncated_content}")
                        
                        if RAG_DEBUG:
                            print(f"  - Document {idx+1}: Added {len(content_str)} characters to context (truncated to {len(truncated_content)})")
                            # Check if CEO info is in the truncated content
                            if 'CEO' in truncated_content or 'Jordan Ellis' in truncated_content:
                                print(f"  - Document {idx+1}: ✅ CEO information found in truncated content")
                            else:
                                print(f"  - Document {idx+1}: ❌ CEO information NOT found in truncated content")
                            sys.stdout.flush()
                    else:
                        if RAG_DEBUG:
                            print(f"  - Document {idx+1}: No usable content found")
                            sys.stdout.flush()
            else:
                if RAG_DEBUG:
                    print("RAG Step 2: No documents found in search results")
                    sys.stdout.flush()
        else:
            if RAG_DEBUG:
                print(f"RAG Step 2: Search failed or returned error: {search_results}")
                sys.stdout.flush()
        
        # Step 3: Build enhanced prompt with context
        if context_chunks:
            context_text = "\n\n".join(context_chunks)
            enhanced_prompt = f"""Based on the following relevant documents from our knowledge base, please answer the user's question:

CONTEXT DOCUMENTS:
{context_text}

USER QUESTION: {query}

Please provide a helpful answer based on the context above. If the context doesn't contain relevant information, please say so and provide a general response."""
        else:
            if RAG_DEBUG:
                print("RAG Step 3: No relevant documents found, using general chat")
                sys.stdout.flush()
            enhanced_prompt = f"""The user asked: {query}

I couldn't find specific relevant documents in our knowledge base for this query. Please provide a helpful general response."""
        
        if RAG_DEBUG:
            print(f"RAG Step 3: Enhanced prompt length: {len(enhanced_prompt)} characters")
            print(f"RAG Step 3: Enhanced prompt content:\n{enhanced_prompt}")
            sys.stdout.flush()
        
        # Step 4: Get chat completion with enhanced prompt and persona-specific system message
        if RAG_DEBUG:
            print(f"RAG Step 4: Sending enhanced prompt to OpenAI with {persona.upper()} persona...")
            sys.stdout.flush()
            
        chat_result = get_chat_completion(enhanced_prompt, system_message)
        
        if chat_result.get("status") == "error":
            return {
                "response": chat_result.get("error", "Unknown error occurred"),
                "status": "error",
                "query": query
            }
        
        # Step 5: Format the response with context information
        if RAG_DEBUG:
            print("RAG Step 5: Formatting response with context information")
            sys.stdout.flush()
            
        content = chat_result.get("content", "No response generated")
        usage = chat_result.get("usage", {})
        
        # Add context information to response with persona indicator
        persona_display = "CEO" if persona == "ceo" else "Financial Analyst"
        response_text = f"{persona_display} Response (with knowledge base context):\n\n{content}"
        
        if context_chunks:
            response_text += f"\n\n📚 Based on {len(context_chunks)} relevant document(s) from the knowledge base."
        else:
            response_text += f"\n\n💭 No specific documents found in knowledge base for this query - providing general response."
        
        if usage and RAG_DEBUG:
            response_text += f"\n\n[Tokens used: {usage.get('total_tokens', 0)} (prompt: {usage.get('prompt_tokens', 0)}, completion: {usage.get('completion_tokens', 0)})]"
        
        if RAG_DEBUG:
            print(f"RAG Complete: Generated {persona.upper()} response with {len(context_chunks)} context documents")
            sys.stdout.flush()
        
        return {
            "response": response_text,
            "status": "success",
            "query": query,
            "persona": persona,
            "context_documents": len(context_chunks),
            "chat_result": chat_result
        }
        
    except Exception as e:
        if RAG_DEBUG:
            print(f"RAG processing error: {e}")
            sys.stdout.flush()
        error_response = f"Error processing your chat query with knowledge base: {str(e)}\n\n"
        error_response += f"Your query: '{query}'\n\n"
        error_response += "This might be due to:\n"
        error_response += "• Azure AI Search or OpenAI service configuration issues\n"
        error_response += "• Network connectivity problems\n"
        error_response += "• Invalid API endpoint or credentials"
        
        return {
            "response": error_response,
            "status": "error",
            "query": query
        }

def process_search_query(query):
    """
    Process user query using Azure AI Search
    """
    try:
        # Search documents using Azure AI Search
        search_results = search_documents(query)
        
        if search_results.get("status") == "error":
            return {
                "response": search_results.get("error", "Unknown error occurred"),
                "status": "error",
                "query": query
            }
        
        # Format the search results for display
        documents = search_results.get("documents", [])
        total_count = search_results.get("total_count", 0)
        
        if not documents:
            response_text = f"No documents found for query: '{query}'"
        else:
            response_text = f"Found {total_count} results for: '{query}'\n\n"
            
            for i, doc in enumerate(documents[:5], 1):  # Show top 5 results
                score = doc.get("score", 0)
                title = doc.get("title", doc.get("Title", f"Document {i}"))
                content = doc.get("content", doc.get("Content", doc.get("text", "No content available")))
                
                # Truncate content if too long
                if len(content) > 200:
                    content = content[:200] + "..."
                
                response_text += f"{i}. {title} (Score: {score:.2f})\n"
                response_text += f"   {content}\n\n"
        
        return {
            "response": response_text,
            "status": "success",
            "query": query,
            "search_results": search_results
        }
        
    except Exception as e:
        if DEBUG_MODE:
            print(f"Search query processing error: {e}")
        error_response = f"Error processing your search query: {str(e)}\n\n"
        error_response += f"Your query: '{query}'\n\n"
        error_response += "This might be due to:\n"
        error_response += "• Azure Search service configuration issues\n"
        error_response += "• Network connectivity problems\n"
        error_response += "• Invalid search index or credentials"
        
        return {
            "response": error_response,
            "status": "error",
            "query": query
        }

@app.route("/")
def index():
    if DEBUG_MODE:
        print("Index route called")
    user = session.get("user")
    if DEBUG_MODE:
        print("User in session:", user)
    
    if not user:
        if DEBUG_MODE:
            print("No user found, redirecting to login")
        return redirect(url_for("login"))
    
    if DEBUG_MODE:
        print("User found, rendering index template")
    return render_template('index.html', user=user)

@app.route("/login")
def login():
    session["flow"] = _build_auth_code_flow(scopes=SCOPE)
    return render_template("login.html", auth_url=session["flow"]["auth_uri"])

@app.route(REDIRECT_PATH)
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        
        if DEBUG_MODE:
            print("Authorization result:", result)
        
        if "error" in result:
            if DEBUG_MODE:
                print(f"Error in authorization: {result}")
            return render_template("auth_error.html", result=result)
        
        # Store user information
        user_claims = result.get("id_token_claims")
        if DEBUG_MODE:
            print("User claims:", user_claims)
        
        if not user_claims:
            if DEBUG_MODE:
                print("No user claims found in result")
            return render_template("auth_error.html", result={"error": "No user claims", "error_description": "Failed to get user information from token"})
        
        # Store only essential user data to avoid large session cookie
        essential_user_data = {
            'name': user_claims.get('name', 'Unknown User'),
            'preferred_username': user_claims.get('preferred_username', ''),
            'email': user_claims.get('preferred_username', ''),
            'oid': user_claims.get('oid', '')
        }
        
        # Try to get additional user info from Microsoft Graph (but don't store tokens)
        if "access_token" in result:
            try:
                if DEBUG_MODE:
                    print("Fetching additional user info from Graph API...")
                graph_response = requests.get(
                    'https://graph.microsoft.com/v1.0/me',
                    headers={'Authorization': 'Bearer ' + result['access_token']},
                    timeout=30,
                )
                
                if graph_response.status_code == 200:
                    graph_data = graph_response.json()
                    if DEBUG_MODE:
                        print("Graph data received:", graph_data)
                    
                    # Add only essential Graph data
                    if graph_data.get('mail'):
                        essential_user_data['email'] = graph_data.get('mail')
                    if graph_data.get('jobTitle'):
                        essential_user_data['job_title'] = graph_data.get('jobTitle')
                    if graph_data.get('displayName'):
                        essential_user_data['display_name'] = graph_data.get('displayName')
                else:
                    if DEBUG_MODE:
                        print(f"Graph API error: {graph_response.status_code} - {graph_response.text}")
            except Exception as e:
                if DEBUG_MODE:
                    print(f"Could not fetch additional user info: {e}")
        
        # Store only essential data in session
        session["user"] = essential_user_data
        if DEBUG_MODE:
            print("Stored user data in session:", essential_user_data)
        
        # Don't save token cache to avoid large session
        if DEBUG_MODE:
            print("Redirecting to index...")
        
    except ValueError as e:
        if DEBUG_MODE:
            print(f"ValueError in authorization: {e}")
        return render_template("auth_error.html", result={"error": "ValueError", "error_description": str(e)})
    except Exception as e:
        if DEBUG_MODE:
            print(f"Unexpected error in authorization: {e}")
        return render_template("auth_error.html", result={"error": "Unexpected error", "error_description": str(e)})
    
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    # Redirect directly to the app's login page instead of Azure logout
    return redirect(url_for("login"))

@app.route("/test_rag", methods=["GET", "POST"])
def test_rag():
    """Test route to verify RAG functionality without authentication (for debugging)"""
    if request.method == "GET":
        return jsonify({
            "message": "RAG Test Endpoint",
            "instructions": "Send POST request with {'prompt': 'your question'} to test RAG functionality"
        })
    
    user_prompt = request.json.get("prompt", "What is Azure?")
    debug_search = request.json.get("debug_search", False)
    
    if RAG_DEBUG:
        print(f"[TEST_RAG] Testing RAG with prompt: '{user_prompt}'")
        sys.stdout.flush()
    
    # If debug_search is requested, return raw search results instead of RAG
    if debug_search:
        if RAG_DEBUG:
            print(f"[TEST_RAG] Debug search mode - returning raw search results")
            sys.stdout.flush()
        
        search_results = search_documents(user_prompt, top=3)
        
        # Add CEO detection to the response
        documents = search_results.get("documents", [])
        for i, doc in enumerate(documents):
            content = str(doc.get('content', ''))
            doc['has_ceo_info'] = 'CEO' in content or 'Jordan Ellis' in content
            doc['content_length'] = len(content)
            if doc['has_ceo_info']:
                # Find CEO mentions
                lines = content.split('\n')
                ceo_lines = []
                for j, line in enumerate(lines):
                    if 'CEO' in line or 'Jordan Ellis' in line:
                        ceo_lines.append(f"Line {j}: {line.strip()}")
                doc['ceo_mentions'] = ceo_lines
        
        return jsonify({
            "test_endpoint": "test_rag_debug_search",
            "prompt": user_prompt,
            "search_results": search_results,
            "timestamp": str(uuid.uuid4())
        })
    
    # Test RAG functionality directly
    chat_response = process_chat_query(user_prompt)
    
    return jsonify({
        "test_endpoint": "test_rag",
        "prompt": user_prompt,
        "rag_response": chat_response,
        "timestamp": str(uuid.uuid4())
    })

@app.route("/test")
def test():
    """Test route to verify app is working"""
    return jsonify({
        "status": "ok",
        "message": "Flask app is running",
        "user_in_session": session.get("user") is not None,
        "session_keys": list(session.keys())
    })

@app.route("/auth_error_test")
def auth_error_test():
    """Test route to view the authentication error page"""
    return render_template("auth_error.html", result={
        "error": "Test Error", 
        "error_description": "This is a test of the authentication error page. This page would normally be shown when there's an issue with Azure AD authentication."
    })

@app.route("/process_prompt", methods=["POST"])
def process_prompt():
    """Process the user prompt using Azure AI Search and return search results"""
    if not session.get("user"):
        return jsonify({"error": "Not authenticated"}), 401
    
    user_prompt = request.json.get("prompt", "")
    mode = request.json.get("mode", "search")  # "search" or "chat"
    persona = request.json.get("persona", "analyst")  # "analyst" or "ceo"
    
    if RAG_DEBUG:
        print(f"[ROUTE] /process_prompt called with mode: {mode}, persona: {persona}, prompt: '{user_prompt[:50]}...'")
        sys.stdout.flush()
    
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    if mode == "chat":
        if RAG_DEBUG:
            print(f"[ROUTE] Processing in CHAT mode with {persona.upper()} persona - starting RAG...")
            sys.stdout.flush()
        # Process the query using Azure OpenAI Chat with persona-specific system message
        chat_response = process_chat_query(user_prompt, persona)
        
        # Return the chat response with the original query
        return jsonify({
            "response": chat_response.get("response", "No response generated"),
            "status": chat_response.get("status", "unknown"),
            "query": chat_response.get("query", user_prompt),
            "mode": "chat",
            "persona": persona,
            "chat_result": chat_response.get("chat_result", {})
        })
    else:
        if RAG_DEBUG:
            print("[ROUTE] Processing in SEARCH mode...")
            sys.stdout.flush()
        # Process the query using Azure AI Search (default)
        search_response = process_search_query(user_prompt)
        
        # Return the search response with the original query
        return jsonify({
            "response": search_response.get("response", "No response generated"),
            "status": search_response.get("status", "unknown"),
            "query": search_response.get("query", user_prompt),
            "mode": "search",
            "search_results": search_response.get("search_results", {})
        })

@app.route("/process_chat", methods=["POST"])
def process_chat():
    """Process the user prompt using Azure OpenAI Chat Completion and return AI response"""
    if not session.get("user"):
        return jsonify({"error": "Not authenticated"}), 401
    
    user_prompt = request.json.get("prompt", "")
    persona = request.json.get("persona", "analyst")  # Default to analyst for backward compatibility
    system_message = request.json.get("system_message", get_system_message_for_persona(persona))
    
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    # Process the query using Azure OpenAI Chat with persona
    chat_response = process_chat_query(user_prompt, persona)
    
    # Return the chat response with the original query
    return jsonify({
        "response": chat_response.get("response", "No response generated"),
        "status": chat_response.get("status", "unknown"),
        "query": chat_response.get("query", user_prompt),
        "persona": persona,
        "chat_result": chat_response.get("chat_result", {})
    })

@app.route("/process_search", methods=["POST"])
def process_search():
    """Process the user prompt using Azure AI Search and return search results"""
    if not session.get("user"):
        return jsonify({"error": "Not authenticated"}), 401
    
    user_prompt = request.json.get("prompt", "")
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    # Process the query using Azure AI Search
    search_response = process_search_query(user_prompt)
    
    # Return the search response with the original query
    return jsonify({
        "response": search_response.get("response", "No response generated"),
        "status": search_response.get("status", "unknown"),
        "query": search_response.get("query", user_prompt),
        "search_results": search_response.get("search_results", {})
    })

@app.route("/process_sk_chat", methods=["POST"])
def process_sk_chat():
    """Process the user prompt using Semantic Kernel Chat Completion with RAG and return AI response"""
    if not session.get("user"):
        return jsonify({"error": "Not authenticated"}), 401
    
    user_prompt = request.json.get("prompt", "")
    persona = request.json.get("persona", "analyst")  # Default to analyst for backward compatibility
    
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    if not SEMANTIC_KERNEL_AVAILABLE:
        return jsonify({
            "error": "Semantic Kernel service not available",
            "response": "Semantic Kernel is not configured or installed. Please check your installation.",
            "status": "error",
            "framework": "semantic_kernel"
        }), 503
    
    # Process the query using Semantic Kernel
    try:
        sk_response = sk_process_chat_query(user_prompt, persona, debug_mode=RAG_DEBUG)
        
        # Return the chat response with the original query
        return jsonify({
            "response": sk_response.get("response", "No response generated"),
            "status": sk_response.get("status", "unknown"),
            "query": sk_response.get("query", user_prompt),
            "persona": persona,
            "framework": "semantic_kernel",
            "context_found": sk_response.get("context_found", False),
            "context_documents": sk_response.get("context_documents", 0),
            "sk_result": sk_response
        })
    except Exception as e:
        if DEBUG_MODE:
            print(f"Error in Semantic Kernel chat processing: {e}")
        return jsonify({
            "error": f"Semantic Kernel processing error: {str(e)}",
            "response": f"Error processing request with Semantic Kernel: {str(e)}",
            "status": "error",
            "framework": "semantic_kernel"
        }), 500

@app.route("/process_sk_search", methods=["POST"])
def process_sk_search():
    """Process the user prompt using Semantic Kernel Search and return search results"""
    if not session.get("user"):
        return jsonify({"error": "Not authenticated"}), 401
    
    user_prompt = request.json.get("prompt", "")
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    if not SEMANTIC_KERNEL_AVAILABLE:
        return jsonify({
            "error": "Semantic Kernel service not available",
            "response": "Semantic Kernel is not configured or installed. Please check your installation.",
            "status": "error",
            "framework": "semantic_kernel"
        }), 503
    
    # Process the query using Semantic Kernel search
    try:
        sk_response = sk_process_search_query(user_prompt, debug_mode=RAG_DEBUG)
        
        # Return the search response with the original query
        return jsonify({
            "response": sk_response.get("response", "No response generated"),
            "status": sk_response.get("status", "unknown"),
            "query": sk_response.get("query", user_prompt),
            "framework": "semantic_kernel",
            "results_count": sk_response.get("results_count", 0),
            "sk_result": sk_response
        })
    except Exception as e:
        if DEBUG_MODE:
            print(f"Error in Semantic Kernel search processing: {e}")
        return jsonify({
            "error": f"Semantic Kernel processing error: {str(e)}",
            "response": f"Error processing search with Semantic Kernel: {str(e)}",
            "status": "error",
            "framework": "semantic_kernel"
        }), 500

@app.route("/ai_status")
def ai_status():
    """Check if Azure AI Search, Azure OpenAI, and Semantic Kernel services are configured and available"""
    status = {
        "overall_status": "Ready"
    }
    
    # Check Azure Search
    if not AZURE_SEARCH_AVAILABLE:
        status["azure_search"] = {
            "available": False,
            "status": "Azure Search packages not installed",
            "endpoint": AZURE_SEARCH_ENDPOINT,
            "index": AZURE_SEARCH_INDEX,
            "document_count": 0,
            "error": "Please install: pip install azure-search-documents",
            "service_status": "Package Missing"
        }
        status["overall_status"] = "Partial"
    else:
        try:
            search_client = get_search_client()
            if search_client:
                # Try to get index statistics
                index_stats = search_client.get_document_count()
                search_service_status = "Ready"
                search_available = True
            else:
                index_stats = 0
                search_service_status = "Configuration Error"
                search_available = False
        except Exception as e:
            index_stats = 0
            search_service_status = f"Error: {str(e)}"
            search_available = False
        
        status["azure_search"] = {
            "available": search_available,
            "status": search_service_status,
            "endpoint": AZURE_SEARCH_ENDPOINT,
            "index": AZURE_SEARCH_INDEX,
            "document_count": index_stats,
            "service_status": search_service_status,
            "packages_available": AZURE_SEARCH_AVAILABLE
        }
        
        if not search_available:
            status["overall_status"] = "Partial"
    
    # Check Azure OpenAI
    if not AZURE_OPENAI_AVAILABLE:
        status["azure_openai"] = {
            "available": False,
            "status": "Azure OpenAI packages not installed",
            "endpoint": AZURE_OPENAI_ENDPOINT,
            "model": AZURE_OPENAI_MODEL,
            "deployment": AZURE_OPENAI_DEPLOYMENT,
            "error": "Please install: pip install openai",
            "service_status": "Package Missing"
        }
        status["overall_status"] = "Partial"
    else:
        try:
            openai_client = get_openai_client()
            if openai_client:
                openai_service_status = "Ready"
                openai_available = True
            else:
                openai_service_status = "Configuration Error"
                openai_available = False
        except Exception as e:
            openai_service_status = f"Error: {str(e)}"
            openai_available = False
        
        status["azure_openai"] = {
            "available": openai_available,
            "status": openai_service_status,
            "endpoint": AZURE_OPENAI_ENDPOINT,
            "model": AZURE_OPENAI_MODEL,
            "deployment": AZURE_OPENAI_DEPLOYMENT,
            "api_version": AZURE_OPENAI_API_VERSION,
            "service_status": openai_service_status,
            "packages_available": AZURE_OPENAI_AVAILABLE
        }
        
        if not openai_available:
            status["overall_status"] = "Partial"
    
    # Check Semantic Kernel
    if not SEMANTIC_KERNEL_AVAILABLE:
        status["semantic_kernel"] = {
            "available": False,
            "status": "Semantic Kernel packages not installed",
            "error": "Please install: pip install semantic-kernel",
            "service_status": "Package Missing",
            "initialized": False
        }
        status["overall_status"] = "Partial"
    else:
        try:
            sk_status = sk_get_status(debug_mode=RAG_DEBUG)
            sk_available = sk_status.get("initialized", False)
            
            status["semantic_kernel"] = {
                "available": sk_available,
                "status": "Ready" if sk_available else "Not Initialized",
                "service_status": "Ready" if sk_available else "Initialization Required",
                "packages_available": SEMANTIC_KERNEL_AVAILABLE,
                "initialized": sk_available,
                "chat_completion_available": sk_status.get("chat_completion_available", False),
                "text_embedding_available": sk_status.get("text_embedding_available", False),
                "search_available": sk_status.get("search_available", False),
                "azure_search_configured": sk_status.get("azure_search_configured", False),
                "azure_openai_configured": sk_status.get("azure_openai_configured", False),
                "plugins_loaded": sk_status.get("plugins_loaded", [])
            }
            
            if not sk_available:
                status["overall_status"] = "Partial"
                
        except Exception as e:
            status["semantic_kernel"] = {
                "available": False,
                "status": f"Error: {str(e)}",
                "service_status": f"Error: {str(e)}",
                "packages_available": SEMANTIC_KERNEL_AVAILABLE,
                "initialized": False,
                "error": str(e)
            }
            status["overall_status"] = "Partial"
    
    # Set overall status
    if status["overall_status"] == "Ready":
        # Check if core services are actually available
        search_ready = status.get("azure_search", {}).get("available", False)
        openai_ready = status.get("azure_openai", {}).get("available", False)
        sk_ready = status.get("semantic_kernel", {}).get("available", False)
        
        # At least one AI service should be available
        if not search_ready and not openai_ready and not sk_ready:
            status["overall_status"] = "Error"
        elif not (search_ready and openai_ready):
            status["overall_status"] = "Partial"
    
    return jsonify(status)

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE, host='127.0.0.1', port=int(os.environ.get('PORT', 5000)))
