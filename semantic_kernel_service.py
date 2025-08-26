"""
Semantic Kernel Service for Azure AI Demo Application
Replaces direct OpenAI and Azure Search calls with Semantic Kernel framework
"""
import os
import asyncio
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Semantic Kernel imports
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.prompt_template import PromptTemplateConfig

# For Azure Search integration (fallback to direct API calls)
try:
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_SEARCH_AVAILABLE = True
except ImportError:
    AZURE_SEARCH_AVAILABLE = False
    class SearchClient:
        def __init__(self, *args, **kwargs): pass
        def search(self, *args, **kwargs): return []
    class AzureKeyCredential:
        def __init__(self, *args, **kwargs): pass

# Load environment variables
load_dotenv()

class SemanticKernelService:
    """
    Semantic Kernel service that handles all AI operations for the Flask app
    """
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.kernel = None
        self.search_client = None
        self._initialized = False
        
        # Configuration from environment
        self.azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.azure_openai_key = os.getenv('AZURE_OPENAI_KEY')
        self.azure_openai_model = os.getenv('AZURE_OPENAI_MODEL', 'gpt-35-turbo')
        self.azure_openai_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-35-turbo')
        self.azure_openai_api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
        
        self.azure_search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        self.azure_search_key = os.getenv('AZURE_SEARCH_KEY')
        self.azure_search_index = os.getenv('AZURE_SEARCH_INDEX', 'novatech-03')
        
        # Embedding model configuration
        self.embedding_model = os.getenv('AZURE_EMBEDDING_MODEL', 'text-embedding-ada-002')
        self.embedding_deployment = os.getenv('AZURE_EMBEDDING_DEPLOYMENT', 'text-embedding-ada-002')
    
    async def initialize(self):
        """Initialize the Semantic Kernel and all services"""
        if self._initialized:
            return
            
        try:
            if self.debug_mode:
                print("[SK] Initializing Semantic Kernel...")
            
            # Create kernel
            self.kernel = sk.Kernel()
            
            # Add Azure OpenAI Chat Completion service
            chat_service = AzureChatCompletion(
                deployment_name=self.azure_openai_deployment,
                endpoint=self.azure_openai_endpoint,
                api_key=self.azure_openai_key,
                api_version=self.azure_openai_api_version,
                service_id="azure_chat_completion"
            )
            self.kernel.add_service(chat_service)
            
            # Add Azure Text Embedding service
            embedding_service = AzureTextEmbedding(
                deployment_name=self.embedding_deployment,
                endpoint=self.azure_openai_endpoint,
                api_key=self.azure_openai_key,
                api_version=self.azure_openai_api_version,
                service_id="azure_text_embedding"
            )
            self.kernel.add_service(embedding_service)
            
            # Initialize Azure Search client (direct API call as fallback)
            if AZURE_SEARCH_AVAILABLE and self.azure_search_endpoint and self.azure_search_key:
                self.search_client = SearchClient(
                    endpoint=self.azure_search_endpoint,
                    index_name=self.azure_search_index,
                    credential=AzureKeyCredential(self.azure_search_key)
                )
            
            # Add custom plugins
            self._add_persona_plugins()
            self._add_rag_plugins()
            
            self._initialized = True
            
            if self.debug_mode:
                print("[SK] Semantic Kernel initialized successfully!")
                
        except Exception as e:
            if self.debug_mode:
                print(f"[SK] Failed to initialize Semantic Kernel: {e}")
            raise
    
    def _add_persona_plugins(self):
        """Add persona-specific plugins to the kernel"""
        
        @kernel_function(
            description="Get system message for Financial Analyst persona",
            name="get_analyst_persona"
        )
        def get_analyst_persona() -> str:
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
        
        @kernel_function(
            description="Get system message for CEO persona",
            name="get_ceo_persona"
        )
        def get_ceo_persona() -> str:
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
        
        # Add personas to kernel as a plugin
        self.kernel.add_function(
            function=get_analyst_persona,
            plugin_name="personas"
        )
        self.kernel.add_function(
            function=get_ceo_persona,
            plugin_name="personas"
        )
    
    def _add_rag_plugins(self):
        """Add RAG-specific plugins to the kernel"""
        
        @kernel_function(
            description="Search Azure AI Search for relevant documents",
            name="search_documents"
        )
        def search_documents(query: str, top: int = 3) -> List[str]:
            """Search for relevant documents using Azure AI Search"""
            try:
                if not self.search_client:
                    return []
                
                search_results = self.search_client.search(
                    search_text=query,
                    top=top,
                    include_total_count=True
                )
                
                documents = []
                for result in search_results:
                    # Extract content from various possible fields
                    content = (result.get('content') or 
                              result.get('Content') or 
                              result.get('text') or 
                              result.get('Text') or
                              str(result))
                    
                    if content and str(content).strip():
                        # Limit content to 4000 characters
                        content_str = str(content)[:4000]
                        documents.append(content_str)
                
                return documents[:3]  # Return top 3 documents
                
            except Exception as e:
                if self.debug_mode:
                    print(f"[SK] Error searching documents: {e}")
                return []
        
        # Add search function to kernel as a plugin
        self.kernel.add_function(
            function=search_documents,
            plugin_name="rag"
        )
    
    async def process_chat_query(self, query: str, persona: str = "analyst") -> Dict[str, Any]:
        """
        Process a chat query using Semantic Kernel RAG pipeline
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            if self.debug_mode:
                print(f"[SK] Processing chat query with {persona} persona: {query[:50]}...")
                print(f"[SK] Available plugins: {list(self.kernel.plugins.keys()) if hasattr(self.kernel, 'plugins') else 'No plugins attribute'}")
            
            # Step 1: Search for relevant documents using our plugin
            try:
                if hasattr(self.kernel, 'plugins') and "rag" in self.kernel.plugins:
                    search_function = self.kernel.plugins["rag"]["search_documents"]
                    search_results = await self.kernel.invoke(search_function, query=query, top=3)
                    if self.debug_mode:
                        print(f"[SK] Search completed, results type: {type(search_results)}")
                else:
                    if self.debug_mode:
                        print("[SK] RAG plugin not found, using empty search results")
                    search_results = []
            except Exception as e:
                if self.debug_mode:
                    print(f"[SK] Error in search step: {e}")
                search_results = []
            
            # Step 2: Get persona system message
            try:
                if hasattr(self.kernel, 'plugins') and "personas" in self.kernel.plugins:
                    if persona == "ceo":
                        persona_function = self.kernel.plugins["personas"]["get_ceo_persona"]
                    else:
                        persona_function = self.kernel.plugins["personas"]["get_analyst_persona"]
                    
                    system_msg_result = await self.kernel.invoke(persona_function)
                    system_message = str(system_msg_result)
                    if self.debug_mode:
                        print(f"[SK] Persona message retrieved for {persona}")
                else:
                    # Fallback to direct persona messages
                    if persona == "ceo":
                        system_message = "You are a CEO providing detailed responses about company performance and strategy."
                    else:
                        system_message = "You are a financial analyst asking probing questions about company performance."
                    if self.debug_mode:
                        print(f"[SK] Using fallback persona message for {persona}")
            except Exception as e:
                if self.debug_mode:
                    print(f"[SK] Error in persona step: {e}")
                system_message = "You are an AI assistant providing helpful responses."
            
            # Step 3: Build enhanced prompt with context
            context_documents = search_results.value if hasattr(search_results, 'value') else search_results
            
            if context_documents and len(context_documents) > 0:
                context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context_documents)])
                enhanced_prompt = f"""Based on the following relevant documents from our knowledge base, please respond as the specified persona:

CONTEXT DOCUMENTS:
{context}

USER QUESTION: {query}

Please provide a response based on the context above and stay in character according to your persona."""
            else:
                enhanced_prompt = f"""The user asked: {query}

No specific relevant documents were found in the knowledge base for this query. Please provide a helpful general response while staying in character according to your persona."""
            
            # Step 4: Create a simple prompt template and execute
            prompt_template = f"""{system_message}

User: {enhanced_prompt}
Assistant:"""
            
            # Step 5: Execute the chat completion using kernel's chat service
            chat_service = self.kernel.get_service("azure_chat_completion")
            
            # Prepare messages for the chat service
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": enhanced_prompt}
            ]
            
            # Use the correct method name for chat completion
            try:
                # Try the newer API first
                if hasattr(chat_service, 'get_chat_message_contents'):
                    from semantic_kernel.contents.chat_history import ChatHistory
                    chat_history = ChatHistory()
                    chat_history.add_system_message(system_message)
                    chat_history.add_user_message(enhanced_prompt)
                    
                    response = await chat_service.get_chat_message_contents(
                        chat_history=chat_history,
                        settings=self.kernel.get_prompt_execution_settings_from_service_id("azure_chat_completion")
                    )
                    response_content = str(response[0].content) if response and len(response) > 0 else "No response generated"
                else:
                    # Fallback to older API
                    response = await chat_service.complete_chat(messages)
                    response_content = str(response) if response else "No response generated"
                    
            except Exception as chat_error:
                if self.debug_mode:
                    print(f"[SK] Chat completion error: {chat_error}")
                response_content = f"Chat completion error: {str(chat_error)}"
            
            if self.debug_mode:
                print(f"[SK] Generated response length: {len(response_content)} characters")
            
            # Format response
            persona_display = "CEO" if persona == "ceo" else "Financial Analyst"
            formatted_response = f"{persona_display} Response (powered by Semantic Kernel):\n\n{response_content}"
            
            if context_documents and len(context_documents) > 0:
                formatted_response += f"\n\n📚 Based on {len(context_documents)} relevant document(s) from the knowledge base."
            else:
                formatted_response += f"\n\n💭 No specific documents found in knowledge base for this query - providing general response."
            
            return {
                "response": formatted_response,
                "status": "success",
                "query": query,
                "persona": persona,
                "context_found": bool(context_documents and len(context_documents) > 0),
                "framework": "semantic_kernel",
                "context_documents": len(context_documents) if context_documents else 0
            }
            
        except Exception as e:
            if self.debug_mode:
                print(f"[SK] Error processing chat query: {e}")
                import traceback
                traceback.print_exc()
            
            return {
                "response": f"Error processing chat query with Semantic Kernel: {str(e)}",
                "status": "error",
                "query": query,
                "persona": persona,
                "framework": "semantic_kernel"
            }
    
    async def process_search_query(self, query: str) -> Dict[str, Any]:
        """
        Process a search-only query using Semantic Kernel
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            if self.debug_mode:
                print(f"[SK] Processing search query: {query[:50]}...")
            
            if not self.search_client:
                return {
                    "response": "Search service not available - Azure AI Search not configured",
                    "status": "error",
                    "query": query,
                    "framework": "semantic_kernel"
                }
            
            # Use our search plugin
            search_function = self.kernel.plugins["rag"]["search_documents"]
            search_results = await self.kernel.invoke(search_function, query=query, top=5)
            
            # Format results
            documents = search_results.value if hasattr(search_results, 'value') else search_results
            
            if not documents or len(documents) == 0:
                response_text = f"No documents found for query: '{query}'"
            else:
                response_text = f"Found {len(documents)} results for: '{query}' (powered by Semantic Kernel)\n\n"
                
                for i, content in enumerate(documents, 1):
                    # Truncate content if too long for display
                    display_content = content[:200] + "..." if len(content) > 200 else content
                    response_text += f"{i}. {display_content}\n\n"
            
            return {
                "response": response_text,
                "status": "success",
                "query": query,
                "framework": "semantic_kernel",
                "results_count": len(documents) if documents else 0
            }
            
        except Exception as e:
            if self.debug_mode:
                print(f"[SK] Error processing search query: {e}")
            
            return {
                "response": f"Error processing search query with Semantic Kernel: {str(e)}",
                "status": "error",
                "query": query,
                "framework": "semantic_kernel"
            }
    
    async def get_kernel_status(self) -> Dict[str, Any]:
        """
        Get status of Semantic Kernel services
        """
        status = {
            "initialized": self._initialized,
            "chat_completion_available": False,
            "text_embedding_available": False,
            "search_available": False,
            "azure_search_configured": bool(self.azure_search_endpoint and self.azure_search_key),
            "azure_openai_configured": bool(self.azure_openai_endpoint and self.azure_openai_key),
            "plugins_loaded": []
        }
        
        if self._initialized and self.kernel:
            # Check available services
            services = self.kernel.services
            status["chat_completion_available"] = "azure_chat_completion" in services
            status["text_embedding_available"] = "azure_text_embedding" in services
            status["search_available"] = self.search_client is not None
            status["plugins_loaded"] = list(self.kernel.plugins.keys()) if hasattr(self.kernel, 'plugins') else []
            
        return status

# Global instance
_sk_service = None

def get_semantic_kernel_service(debug_mode: bool = False) -> SemanticKernelService:
    """
    Get or create the global Semantic Kernel service instance
    """
    global _sk_service
    if _sk_service is None:
        _sk_service = SemanticKernelService(debug_mode=debug_mode)
    return _sk_service

# Async wrapper functions for Flask app
def run_async(coro):
    """Helper to run async functions in Flask context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def sk_process_chat_query(query: str, persona: str = "analyst", debug_mode: bool = False) -> Dict[str, Any]:
    """Synchronous wrapper for chat query processing"""
    sk_service = get_semantic_kernel_service(debug_mode)
    return run_async(sk_service.process_chat_query(query, persona))

def sk_process_search_query(query: str, debug_mode: bool = False) -> Dict[str, Any]:
    """Synchronous wrapper for search query processing"""
    sk_service = get_semantic_kernel_service(debug_mode)
    return run_async(sk_service.process_search_query(query))

def sk_get_status(debug_mode: bool = False) -> Dict[str, Any]:
    """Synchronous wrapper for getting kernel status"""
    sk_service = get_semantic_kernel_service(debug_mode)
    return run_async(sk_service.get_kernel_status())
