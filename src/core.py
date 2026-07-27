"""
localmind - Moteur de routage intelligent
Route la question vers le modèle le plus adapté.
"""

import ollama

ROUTER_MODEL = "llama3.2:1b"

MODELS = {
    "code": "qwen2.5-coder:7b",
    "creative": "mistral",
    "general": "llama3.2",
}

SYSTEM_PROMPT = """Tu es LocalMind, une IA personnelle qui tourne en local sur le PC de l'utilisateur.
Tu réponds de façon directe, un peu familière, sans blabla inutile.
Ne mentionne jamais Ollama, Llama, Mistral, Qwen : tu es LocalMind, point final.

RÈGLE D'UTILISATION DU WEB :
Si un bloc "INFORMATIONS DU WEB" est présent dans le message de l'utilisateur, tu DOIS obligatoirement l'utiliser pour répondre de manière exacte et récente. Fais une synthèse rapide et cool des résultats trouvés.

RÈGLE EXEC (très stricte) :
Tu ne proposes une commande d'exécution QUE si l'utilisateur demande EXPLICITEMENT de lancer,
exécuter, ouvrir ou scanner quelque chose sur le PC.
[EXEC]la commande ici[/EXEC]
Jamais de [EXEC] spontané."""


def route_question(question: str) -> dict:
    """Demande au petit modèle de classer la question et choisir un outil web."""
    router_prompt = f"""Analyse cette question et choisis les meilleures options.
Question : "{question}"

1. Catégorie :
- "code" : dev, debug, script, shell, sys, pentest, repos
- "creative" : histoire, écriture, brainstorm
- "general" : faits, culture, météo, actu, recherche, discussion

2. Outil Web (tool) :
- "none" : pas besoin d'internet (ex: écrire du code basique, blague, maths)
- "ddg" : info rapide, simple, météo, recherche basique
- "tavily" : actualité récente, recherches complexes, meilleurs repos/outils, synthèse d'articles

Réponds UNIQUEMENT sous forme d'un objet JSON strict :
{{"category": "general", "tool": "none"}}"""

    try:
        import json
        res = ollama.chat(
            model=ROUTER_MODEL,
            messages=[{"role": "user", "content": router_prompt}],
            format="json"
        )
        data = json.loads(res["message"]["content"])
        category = data.get("category", "general")
        tool = data.get("tool", "none")
        if category not in MODELS:
            category = "general"
        if tool not in ["none", "ddg", "tavily"]:
            tool = "none"

        keywords_web = ["cherche", "recherche", "actualité", "actu", "du moment", "actuel", "récent", "meilleur", "top", "news", "repo", "github"]
        if any(kw in question.lower() for kw in keywords_web) and tool == "none":
            tool = "ddg"

        return {"category": category, "tool": tool}
    except Exception:
        return {"category": "general", "tool": "none"}


def ask(question: str, web_context: str = "") -> str:
    """Route la question, appelle le bon modèle, renvoie la réponse."""
    decision = route_question(question)
    chosen_model = MODELS[decision["category"]]

    prompt = question
    if web_context:
        prompt = f"INFORMATIONS DU WEB :\n{web_context}\n\nQUESTION UTILISATEUR : {question}"

    response = ollama.chat(
        model=chosen_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"]


def main():
    print("=== LocalMind — Ton IA locale multi-modèles ===")
    print("Tape 'exit' pour quitter.\n")

    while True:
        question = input("Toi > ").strip()
        if question.lower() in ("exit", "quit", "q"):
            print("À la prochaine !")
            break
        if not question:
            continue

        reponse = ask(question)
        print(f"\nLocalMind > {reponse}\n")


if __name__ == "__main__":
    main()
