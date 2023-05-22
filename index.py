import websocket
import requests
import json
import keys
from perspective import perspective_ban

openai_token = keys.OPENAI_TOKEN
api_token = keys.OWNCAST_TOKEN
mod_token = keys.MODERATOR_TOKEN
owncast_url = keys.OWNCAST_URL
websocket_url = keys.OWNCAST_WEBSOCKET

log = open("deleted.txt", "a")

chat_name = {"displayName": "Vigilante"}
chat_response = requests.post(owncast_url + "/api/chat/register", json=chat_name)
chat_user = chat_response.json()
chat_token = chat_user["accessToken"]
print("access token acquired")


def delete_message(id, text):
    msg_data = {"visible": False, "idArray": [id]}

    delete_response = requests.post(
        owncast_url + "/api/chat/messagevisibility?accessToken=" + mod_token,
        json=msg_data,
    )
    if delete_response.json()["success"] == True:
        log.write("\n" + text)
        return True
    else:
        return False


removed = 0


def on_message(ws_app, message):
    msg = json.loads(message)
    if msg["type"] == "CHAT":
        chat_text = msg["body"]
        chat_id = msg["id"]

        print(" - " + chat_text)
        if len(chat_text > 30):
            if perspective_ban(chat_text):
                if delete_message(chat_id, chat_text):
                    print("Deleted message: " + chat_text)
                    removed += 1
    print("TOTAL REMOVED: " + removed)


ws_URL = websocket_url + chat_token
ws_app = websocket.WebSocketApp(ws_URL, on_message=on_message)
ws_app.run_forever()
