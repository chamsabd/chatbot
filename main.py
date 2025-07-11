from flask import Flask, request, jsonify
from prompt_rewriter import reformuler_en_requete
from google_search import extraire_entites, format_search_results, searxng_search,search_best_linkedin_match
from groq_wrapper import groq_search, scorer_par_groq



app = Flask(__name__)

@app.route("/")
def home():
    return "API is running on Render 🚀"

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    profil_ideal = data.get("profil_ideal", "")

    if not message:
        return jsonify({"error": "Message is required."}), 400

    try:
        # Reformuler la requête
        requete = reformuler_en_requete(message)

        # Recherche avec searxng
        resultats = searxng_search(requete,instance_url="https://bidata.onrender.com")

        # Générer la réponse avec groq
        reponse_groq = groq_search(requete, format_search_results(resultats))
        texte_reponse = reponse_groq.get("choices", [{}])[0].get("message", {}).get("content", "")

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
    app.run(debug=True)