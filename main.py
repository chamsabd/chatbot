import logging
import os
from flask import Flask, request, jsonify
from prompt_rewriter import reformuler_en_requete,reformuler_en_requete_with_groq
from google_search import extraire_entites, format_search_results, searxng_search,search_best_linkedin_match
from groq_wrapper import groq_search, scorer_par_groq

import psutil
import time
import os
from functools import wraps

def monitor_resource_usage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())
        
        start_mem = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.cpu_percent(interval=None)
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_mem = process.memory_info().rss / 1024 / 1024  # MB
        end_cpu = psutil.cpu_percent(interval=None)
        
        print(f"⏱️ Execution time: {end_time - start_time:.3f} seconds")
        print(f"🧠 RAM used: {end_mem - start_mem:.3f} MB")
        print(f"⚙️ CPU usage: {end_cpu - start_cpu:.2f}%")
        
        return result
    return wrapper


app = Flask(__name__)

@app.route("/")
def home():
    return "API is running on Render 🚀"


@app.route("/api/chat", methods=["POST"])
@monitor_resource_usage
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    profil_ideal = data.get("profil_ideal", "")

    if not message:
        return jsonify({"error": "Message is required."}), 400

    try:
        logging.warning("Route /api/chat called")
        # Reformuler la requête
        requete = reformuler_en_requete_with_groq(message)
        logging.warning("reformuler_en_requete called")

        # Recherche avec searxng
        resultats = searxng_search(requete,instance_url="https://bidata.onrender.com")
        logging.warning("searxng_search called")

        # Générer la réponse avec groq
        reponse_groq = groq_search(requete, format_search_results(resultats))
        texte_reponse = reponse_groq.get("choices", [{}])[0].get("message", {}).get("content", "")
        logging.warning("groq_search called")

        # Extraire entités
        entites = extraire_entites(texte_reponse)
        linkedin_profiles = []
        if entites:
            for nom in entites:
                profil = search_best_linkedin_match(nom,instance_url="https://bidata.onrender.com")
                if profil:
                    linkedin_profiles.append({
                        "name": nom,
                        "link": profil["link"],
                        "title": profil["title"]
                    })

                else:
                    linkedin_profiles.append({
                         "name": nom,
                        "link": None,
                        "title": None
                    })

        # Scoring si nécessaire
        scoring = ""
        if entites and profil_ideal:
            score = scorer_par_groq(message, entites, profil_ideal, resultats)
            scoring = score.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Réponse JSON
        return jsonify({
            "requete": requete,
            "sources": resultats,
            "reponse": texte_reponse,
            "scoring": scoring,
            "linkedin_profiles": linkedin_profiles
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Port donné par Render
    app.run(host="0.0.0.0", port=port, debug=True)