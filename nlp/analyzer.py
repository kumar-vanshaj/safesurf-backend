import pickle

# Load models ONCE (server startup)
tox_model = pickle.load(open("nlp/models/toxicity_model.pkl", "rb"))
tox_vectorizer = pickle.load(open("nlp/models/toxicity_vectorizer.pkl", "rb"))

nsfw_model = pickle.load(open("nlp/models/nsfw_model.pkl", "rb"))
nsfw_vectorizer = pickle.load(open("nlp/models/nsfw_vectorizer.pkl", "rb"))


def toxicity_score(text: str) -> float:
    vec = tox_vectorizer.transform([text])
    return float(tox_model.predict_proba(vec)[0][1])


def nsfw_score(text: str) -> float:
    vec = nsfw_vectorizer.transform([text])
    return float(nsfw_model.predict_proba(vec)[0][1])


def analyze_text(text: str) -> dict:
    toxic = round(toxicity_score(text), 2)
    nsfw = round(nsfw_score(text), 2)

    final = round(max(toxic, nsfw), 2)

    if final >= 0.7:
        level = "FLAGGED"
    elif final >= 0.4:
        level = "WARNING"
    else:
        level = "SAFE"

    return {
        "toxicity_score": toxic,
        "nsfw_score": nsfw,
        "final_score": final,
        "risk_level": level
    }
