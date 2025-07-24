"""
Prompt templates for antipattern scanner
"""
ANTIPATTERN_SCANNER_KEY = "antipattern_scanner"
ANTIPATTERN_SCANNER_PROMPT = (
    "You are a senior Java software engineer and expert code reviewer, specializing in identifying software design antipatterns. "
    "You have extensive knowledge of common Java-related antipatterns"
    "Below is the code to analyze:\n"
    "```{code}```\n\n"
    "Here is additional context from the codebase:\n"
    "{context}\n\n"
    "Your task is to:\n"
    "- Carefully analyze the code for Java antipatterns and design smells.\n"
    "- Base your analysis strictly on the antipattern definitions provided earlier in this conversation. Do not invent new antipatterns.\n"
    "- Make sure your results are clear and actionable, so others can know how to address the identified issues.\n"
    "- Return your analysis in JSON format with the following structure:\n\n"
    '{{\n'
    '  "total_antipatterns_found": 0,\n'
    '  "antipatterns_detected": [\n'
    '    {{\n'
    '      "name": "<antipattern name>",\n'
    '      "location": "<class/method name/line number>",\n'
    '      "description": "<comprehensive description>",\n'
    '    }}\n'
    '  ]\n'
    '}}\n\n'
    "Be thorough but concise. Ensure the JSON is valid and properly formatted. "
    "If no antipatterns are found, set total_antipatterns_found to 0 and antipatterns_detected to an empty array."
)
