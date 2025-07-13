
# prompt_rewriter.py

from ctransformers import AutoModelForCausalLM
from langdetect import detect

# Chargement du modèle Mistral (GGUF quantized)
model = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
    model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    model_type="mistral",
    max_new_tokens=100
)



def reformuler_en_requete(user_input: str) -> str:
    """
    Reformule une question de l'utilisateur en une requête Google optimisée,
    en conservant la langue principale (français ou anglais).
    """
    try:
        langue = detect(user_input)
    except:
        langue = "en"

    if langue == "fr":
        prompt = (
            "Tu es un optimiseur de recherche en ligne. Reformule la question de l'utilisateur en une requête Google claire, courte et naturelle. "
            "Utilise exclusivement la langue française. Ne traduis pas. Conserve les mots-clés importants.\n"
            f"Question : {user_input}\n"
            "Requête Google :"
        )
    else:
        prompt = (
            "You are a web search optimizer. Rewrite the user’s prompt as a clear and concise Google query. "
            "Use English only. Do not translate. Keep key terms.\n"
            f"User question: {user_input}\n"
            "Google query:"
        )

    response = model(prompt)
    return response.strip()




from config import GROQ_API_KEY1,GROQ_CHAT_URL,GROQ_MODEL1
import requests


def reformuler_en_requete_with_groq(user_input: str) -> str:
    """
    Reformule une question de l'utilisateur en une requête Google optimisée,
    en conservant la langue principale (français ou anglais), en utilisant Groq.
    """
    try:
        langue = detect(user_input)
    except:
        langue = "en"

    if langue == "fr":
        prompt = (
            "Tu es un optimiseur de recherche en ligne. Reformule la question de l'utilisateur en une requête Google claire, courte et naturelle. "
            "Utilise exclusivement la langue française. Ne traduis pas. Conserve les mots-clés importants.\n"
            f"Question : {user_input}\n"
            "Requête Google :"
        )
    else:
        prompt = (
            "You are a web search optimizer. Rewrite the user’s prompt as a clear and concise Google query. "
            "Use English only. Do not translate. Keep key terms.\n"
            f"User question: {user_input}\n"
            "Google query:"
        )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY1}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL1,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }

    response = requests.post(GROQ_CHAT_URL, headers=headers, json=body)
    
    if response.status_code != 200:
        raise Exception(f"Groq API error: {response.status_code}, {response.text}")

    reply = response.json()["choices"][0]["message"]["content"]
    return reply.strip()
