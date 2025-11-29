"""Prompt templates for the GenAI agent."""


def build_rag_prompt(query: str, retrieved_data: dict) -> str:
    """
    Build the strict ChromaDB retrieval prompt.
    
    Args:
        query: The user question
        retrieved_data: The retrieved chunks from ChromaDB (result from collection.query())
    
    Returns:
        Formatted prompt string
    """
    # Extract the documents from the ChromaDB results
    # retrieved_data['documents'] is a list of lists, so we take the first list
    documents = retrieved_data.get('documents', [[]])[0]
    
    # Format the documents as numbered context items
    context_text = "\n".join([f"{i+1}. {doc}" for i, doc in enumerate(documents)])

    prompt = f"""
ROLE: Chroma Retrieval Executor

PRIMARY DIRECTIVE:
Use only the information contained inside the DELIMITED CONTEXT BLOCK to answer the query.
Base every part of your response solely on those context details.

CONSTRAINTS (MANDATORY):
- Maintain a zero-hallucination standard.
- When the context supports the answer, state it directly and concisely.
- When the context lacks the required information, respond exactly:
  "Not found in ChromaDB."
- Produce only the final answer with no additional commentary.

OPERATIONAL RULES:
1. Treat the DELIMITED CONTEXT BLOCK as the authoritative source.
2. Ground every statement directly in the context.
3. Respond only when the context provides explicit support.
4. Keep the answer minimal, precise, and context-bound.

===== DELIMITED CONTEXT BLOCK START =====
{context_text}
===== DELIMITED CONTEXT BLOCK END =====

USER QUERY:
{query}

RESPONSE POLICY:
- If the context contains the answer → return it.
- If the context does not contain the answer → return: Not found in ChromaDB.
"""
    return prompt
