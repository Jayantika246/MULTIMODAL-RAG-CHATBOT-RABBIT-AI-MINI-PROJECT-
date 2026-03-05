from groq import Groq
from config import Config

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.system_prompt = """You are a travel planning assistant.
Use the provided context and conversation history to answer questions.
Answer ONLY using the provided context.
If information is missing, say: "I don't have enough information in my travel database."
Do NOT use outside knowledge.
Be clear and structured.
If the user refers to previous messages, use the conversation history."""
    
    def generate_response(self, query, context_chunks, chat_history=""):
        """
        Generate response using Groq LLM with retrieved context and chat history
        Returns structured answer
        """
        if not context_chunks:
            return "I don't have enough information in my travel database. Please add travel documents first."
        
        # Build context from chunks
        context = "\n\n".join([
            f"Source {i+1} ({chunk['metadata']['source_title']}):\n{chunk['text']}" 
            for i, chunk in enumerate(context_chunks)
        ])
        
        # Build prompt with history
        prompt = f"""Conversation History:
{chat_history}

Context:
{context}

User Question: {query}

Provide a clear and structured answer based on the context above and conversation history."""

        try:
            response = self.client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
