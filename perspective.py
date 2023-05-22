from googleapiclient import discovery
import json
import keys

API_KEY = keys.GOOGLE_KEY


def perspective_ban(comment):
    client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )
    print("persepective check on " + comment)
    analyze_request = {
        "comment": {"text": comment},
        "requestedAttributes": {
            "SEVERE_TOXICITY": {},
            "IDENTITY_ATTACK": {},
            "INSULT": {},
        },
    }
    response = client.comments().analyze(body=analyze_request).execute()
    toxicity = response["attributeScores"]["SEVERE_TOXICITY"]["summaryScore"]["value"]
    attack = response["attributeScores"]["IDENTITY_ATTACK"]["summaryScore"]["value"]
    insult = response["attributeScores"]["INSULT"]["summaryScore"]["value"]

    if toxicity > 0.75 or attack > 0.75 or insult > 0.75:
        return True
    else:
        print(toxicity)
        return False
