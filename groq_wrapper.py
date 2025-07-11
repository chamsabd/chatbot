
from config import GROQ_API_KEY, GROQ_MODEL,GROQ_CHAT_URL
import requests
def groq_search(query,search_results):
    """Search using Groq API with better prompt"""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"""You are a knowledgeable assistant. Below are search results related to the user's message:
{search_results}

Each search result is formatted using tags: [webpage X begin] ... [webpage X end], where X is the number of the source. When you write your answer, cite the sources in-line using [citation:X]. If multiple sources contribute to a sentence, you can use [citation:3][citation:5].

Instructions:

- Only use information that is relevant to the user's question.
- If the user's question asks for a list (for example, "top 10", "best", "list of", "key", "examples of"), provide a clear, concise numbered list with up to 10 key items.
- Make sure the list is explicit and easy to extract (one item per line with numbering).
- Mention to the user that more details can be found in the original sources if applicable.
- For other types of questions, answer thoroughly and professionally with proper citation.
- Avoid repeating the same citation multiple times.
- Keep the response in the same language as the user's message unless asked otherwise.

Now, based on the information above, answer the user’s question thoroughly and professionally.

# User question:
{query}
"""



        data = {
            "model": GROQ_MODEL,
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "temperature": 0.3,
            "max_tokens": 1500
        }


        response = requests.post(GROQ_CHAT_URL, headers=headers, json=data, timeout=20)

        response.raise_for_status()

        json_data = response.json()  # Parse la réponse JSON

        return json_data
    except Exception as e:
        return {
            "error": f"Groq search failed: {str(e)}",
            "choices": [{"message": {"content": ""}}]
        }



def groq_classify_query_type(query):
    """Classify the client question type (universities, company, person, other) using Groq API."""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # Focused prompt for classification
        prompt = f"""
You are a classification assistant. Your task is to analyze the user's question and output ONLY ONE WORD from the following list that best describes what the user is searching for:

universities
company
person
other

Rules:
- Output only the single word, no explanations, no formatting.
- If you are unsure, output "other".

# User question:
{query}
"""

        data = {
            "model": GROQ_MODEL,
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "temperature": 0,
            "max_tokens": 10
        }

        response = requests.post(GROQ_CHAT_URL, headers=headers, json=data, timeout=20)
        response.raise_for_status()
        json_data = response.json()

        # Extract the text response
        content = json_data["choices"][0]["message"]["content"].strip().lower()

        # Validate the output
        valid_types = {"universities", "company", "person", "other"}
        if content not in valid_types:
            content = "other"

        return content

    except Exception as e:
        return "other"

def scorer_par_groq(question_client,liste_entites,profil_ideal, search_results):
    """Search using Groq API with better prompt"""
    try:

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"""
        You are a knowledgeable assistant. Below are search results related to the user's message:
        {search_results}

        Each search result is formatted using tags: [webpage X begin] ... [webpage X end], where X is the number of the source. When you write your answer, cite the sources in-line using [citation:X]. If multiple sources contribute to a sentence, you can use [citation:3][citation:5].

        User's question:
        "{question_client}"

        Here is a list of entities to evaluate:
        {liste_entites}

        Here is the ideal profile or criteria to evaluate them:
        {profil_ideal}

        Instructions:

        - Before evaluating, **remove any entity that is too vague or generic** (for example: entries that are unclear, ambiguous, or lack distinctive information).
        - For each remaining entity in the list, evaluate how well it matches the ideal profile by assigning a score from 0 to 100.
        - Provide a brief but clear explanation (1-2 sentences) for each score.
        - Extract the **official website URL** of each entity from the search results, if available.
        - Present the answer in a **sorted list** (from highest score to lowest), using the following format for each entity:

        1. <Entity name> <official website URL> (score: <score>)  
           <Short explanation> [citation:X]

        2. ...

        - If the URL is not found in the sources, write "(URL not found)" instead.
        - Cite the source number where the website URL or useful information was found using [citation:X].
        - Avoid hallucinating any URLs — only use what's found in the search results.
        - Answer in **the same language as the user's question** ("{question_client}"). Detect and use the appropriate language automatically.
        """

        data = {
            "model": GROQ_MODEL,
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "temperature": 0.3,
            "max_tokens": 1500
        }

        response = requests.post(GROQ_CHAT_URL, headers=headers, json=data, timeout=20)

        response.raise_for_status()
        json_data = response.json()

        # Parse la réponse JSON

        return json_data
    except Exception as e:
        return {
            "error": f"Groq search failed: {str(e)}",
            "choices": [{"message": {"content": ""}}]
        }
