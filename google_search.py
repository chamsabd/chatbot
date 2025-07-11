
import json

from groq_wrapper import groq_classify_query_type


import re
import requests


import difflib




def extraire_entites(text):
    try:
        # 1. Supprimer toutes les occurrences [citation:X] dans tout le texte
        text_sans_citation = re.sub(r"\[citation:\d+\]", "", text)

        # 2. Appliquer la regex sur le texte nettoyé
        pattern = r"\d+\.\s*([^\n,:;\-]+)"
        matches = re.findall(pattern, text_sans_citation)

        entites = [m.strip() for m in matches if m.strip()]
        return entites
    except Exception as e:
        print(f"Erreur extraction entités: {e}")
        return []

def format_search_results(results):
    formatted = ""
    if isinstance(results, str):
        results = json.loads(results)
    for idx, item in enumerate(results, 1):
        formatted += f"[webpage {idx} begin]\n"
        formatted += f"Title: {item['title']}\n"
        formatted += f"Link: {item['link']}\n"
        formatted += f"Description: {item['description']}\n"
        formatted += f"[webpage {idx} end]\n\n"
    return formatted.strip()










def searxng_search(query, instance_url="http://localhost:8080", num_results=10):
    params = {
        "q": query,
        "format": "json",
        "categories": "general",
        "safesearch": 1,
        "language": "en"
        # Ne pas mettre "count" car non garanti par SearXNG
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(f"{instance_url}/search", headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for r in data.get("results", []):
            results.append({
                "title": r.get("title"),
                "link": r.get("url"),
                "description": r.get("content")
            })

        # Tronquer la liste à num_results (ex: 10)

        return results[:num_results]

    except Exception as e:
        print(f"Erreur lors de la recherche SearXNG: {e}")
        return []






def search_best_linkedin_match(name, instance_url="http://localhost:8080"):
    """
    Search LinkedIn profiles or companies with SearxNG and return the best match.
    """

    # 1. Classify the search type
    search_type = groq_classify_query_type(name)

    # 2. Build the query text
    if search_type == "company":
        # query_person = f'"CEO {name}" OR "Founder {name}"'
        query_person =f'"{name}"'
        query_company = f'"{name}"'
    elif search_type == "universities":
        query_person = f'"Professor {name}"'
        query_company = f'"{name}"'
    else:
        query_person = f'"{name}"'
        query_company = None

    # 3. Prepare queries separately
    queries = []
    if query_person:
        queries.append(f'{query_person} site:linkedin.com/in')
    if query_company:
        queries.append(f'"{name}" site:linkedin.com/company')

    best_match = None
    highest_score = -1  # Important: start with -1 to allow 0 score
    name_clean = name.strip().lower()
    name_words = set(name_clean.split())

    # 4. Search each query
    for q in queries:

        params = {
            "q": q,
            "format": "json",
            "language": "en",
            "safesearch": 1
        }

        try:
            response = requests.get(f"{instance_url}/search", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for result in data.get("results", []):
                url = result.get("url", "").lower()
                title = result.get("title", "").strip()
                content = result.get("content", "").strip()

                if "linkedin.com/in/" in url or "linkedin.com/company/" in url:
                    # Clean title and content
                    title_clean = title.strip().lower()
                    content_clean = content.strip().lower()

                    all_words = set(title_clean.split()).union(content_clean.split())
                    overlap = name_words.intersection(all_words)
                    similarity = difflib.SequenceMatcher(None, name_clean, title_clean).ratio()

                    # Base score from overlap and similarity
                    score = len(overlap) * 2 + similarity

                    # Priority bonuses
                    priority_bonus = 0

                    if search_type == "company":
                        if "linkedin.com/in/" in url:
                            if re.search(r"\b(ceo|founder)\b", title_clean):
                                priority_bonus = 800  #  priority for CEO/Founder profile
                            elif re.search(rf"\b{re.escape(name)}\b", title_clean):
                                priority_bonus = 1000  # Highest priority
                            else:
                                priority_bonus = 700  # Other profiles (less priority)
                        elif "linkedin.com/company/" in url:
                            priority_bonus = 800  # Company page (2nd priority)

                    elif search_type == "universities":
                        # For person or professor search
                        if "linkedin.com/in/" in url:
                            if re.search(r"\b(professor)\b", title_clean):
                                priority_bonus = 1000  # Highest priority for personal profile
                        elif "linkedin.com/company/" in url:
                            priority_bonus = 200  # Low priority if it's a company page
                    else:
                        # For person  search
                        if "linkedin.com/in/" in url:
                            priority_bonus = 1000  # Highest priority for personal profile
                        elif "linkedin.com/company/" in url:
                            priority_bonus = 200  # Low priority if it's a company page

                    total_score = score + priority_bonus
                    if total_score > highest_score:
                        highest_score = total_score
                        best_match = {
                            "title": title,
                            "description": re.sub(r'\s+', ' ', content).strip(),
                            "link": url
                        }


        except Exception as e:
            print(f"[SearxNG Error] {str(e)}")

    return best_match
