import os
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from db.mongodb import get_user_history, save_message
from rag.retriever import search_knowledge_base
from utils.language import detect_language, is_arabic
from dotenv import load_dotenv

load_dotenv()

class CustomerSupportAgent:
    def __init__(self):
        # Use the latest OpenAI model with optimized settings
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",  # Latest cost-effective model
            temperature=0.7,
            max_tokens=800,
            timeout=30,
            max_retries=3
        )
        
        # Define tools available to the agent
        self.tools = [
            Tool(
                name="TaxiFAQSearch",
                func=search_knowledge_base,
                description="Search the taxi company's comprehensive FAQ database for answers to customer questions about bookings, payments, policies, locations, pricing, and general support. Use this tool for any customer inquiry."
            )
        ]
    
    def _create_memory_with_history(self, user_id: str) -> ConversationBufferMemory:
        """Create memory object with user's chat history"""
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        # Load previous conversation history (limited to recent exchanges)
        history = get_user_history(user_id, limit=8)  # Last 8 exchanges for context
        
        for msg in history:
            if msg.startswith("User: "):
                memory.chat_memory.add_user_message(msg[6:])  # Remove "User: " prefix
            elif msg.startswith("Assistant: "):
                memory.chat_memory.add_ai_message(msg[11:])  # Remove "Assistant: " prefix
        
        return memory
    
    def _get_system_instructions(self, language: str) -> str:
        """Get system instructions based on detected language"""
        if language == 'ar':
            return """أنت وكيل دعم عملاء محترف لشركة تطبيق تاكسي في المملكة العربية السعودية.

مهامك الأساسية:
- تقديم إجابات دقيقة ومفيدة لاستفسارات العملاء
- استخدام أداة البحث في قاعدة الأسئلة الشائعة للحصول على معلومات محدثة
- الرد باللغة العربية عندما يسأل العميل بالعربية
- إذا لم تجد الإجابة، انصح العميل بالاتصال بالدعم على 920000000
- كن مهذبًا ومفيدًا دائمًا

معلومات مهمة:
- الشركة تعمل في: الرياض، جدة، مكة، المدينة، الدمام، الخبر، والطائف
- رقم الدعم: 920000000
- طرق الدفع: Apple Pay، STC Pay، البطاقات الائتمانية، مدى، النقد"""
        else:
            return """You are a professional customer support agent for a taxi app company in Saudi Arabia.

Your primary responsibilities:
- Provide accurate and helpful answers to customer inquiries
- Use the FAQ search tool to find up-to-date information
- Respond in English when the customer asks in English
- If you can't find the answer, advise contacting support at 920000000
- Always be polite and helpful

Important information:
- Service areas: Riyadh, Jeddah, Mecca, Medina, Dammam, Khobar, and Taif
- Support number: 920000000
- Payment methods: Apple Pay, STC Pay, credit cards, Mada cards, cash"""
    
    def run_agent(self, user_id: str, message: str) -> str:
        """
        Process user message and return agent response
        """
        try:
            # Detect language for appropriate response
            language = detect_language(message)
            
            # Create memory with conversation history
            memory = self._create_memory_with_history(user_id)
            
            # Initialize the agent with the latest settings
            agent = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                memory=memory,
                verbose=False,  # Set to True for debugging
                handle_parsing_errors=True,
                max_iterations=3,
                early_stopping_method="generate"
            )
            
            # Create contextualized prompt with system instructions
            system_instructions = self._get_system_instructions(language)
            contextualized_message = f"{system_instructions}\n\nCustomer: {message}"
            
            # Get agent response with improved error handling
            try:
                response = agent.run(contextualized_message)
            except Exception as agent_error:
                print(f"Agent execution error: {agent_error}")
                # Fallback to direct FAQ search
                response = search_knowledge_base(message)
                
                # If FAQ search also fails, provide fallback response
                if "technical difficulties" in response.lower():
                    if is_arabic(message):
                        response = "أعتذر، أواجه مشكلة تقنية. يرجى الاتصال بخدمة العملاء على 920000000."
                    else:
                        response = "I apologize for the technical issue. Please contact customer support at 920000000."
            
            # Ensure response is not empty
            if not response or len(response.strip()) < 5:
                if is_arabic(message):
                    response = "شكرًا لتواصلك معنا. كيف يمكنني مساعدتك اليوم؟"
                else:
                    response = "Thank you for contacting us. How can I help you today?"
            
            # Save the conversation
            save_message(user_id, message, response, language)
            
            return response.strip()
            
        except Exception as e:
            print(f"Critical error in agent execution: {e}")
            
            # Final fallback response based on language
            if is_arabic(message):
                return "أعتذر، أواجه مشكلة تقنية حاليًا. يرجى الاتصال بخدمة العملاء على 920000000 للمساعدة الفورية."
            else:
                return "I'm sorry, I'm experiencing technical difficulties. Please contact our customer support at 920000000 for immediate assistance."

# Create global instance
customer_agent = CustomerSupportAgent()

# Convenience function for backward compatibility
def run_agent(user_id: str, message: str) -> str:
    return customer_agent.run_agent(user_id, message) 