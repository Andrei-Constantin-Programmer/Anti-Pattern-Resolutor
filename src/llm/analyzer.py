from langchain_community.chat_models import ChatOllama

PROMPT_TEMPLATE = """You are a senior Java code reviewer with deep experience in detecting software design antipatterns.
Below is the code to analyze:
{code}

Here is additional context from the codebase:
{context}

Your task is to:
- Carefully analyze the code.
- Identify any Java antipatterns or design smells present.
- For each antipattern you find, include:
  - [Name of the antipattern]
  - [File/class/method]
  - [Brief description]
  - [Why it's a problem]
  - [Suggested refactor]
Be thorough but concise. If no antipatterns are found, say so.
"""

def analyze_code(llm, code: str, context: str) -> str:
    prompt = PROMPT_TEMPLATE.format(code=code, context=context or "No context available.")
    response = llm.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)
