
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

