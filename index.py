import websocket
import requests
import json
import keys
import asyncio
from concurrent.futures import ProcessPoolExecutor

from perspective import perspective_ban

openai_token = keys.OPENAI_TOKEN
api_token = keys.OWNCAST_TOKEN
mod_token = keys.MODERATOR_TOKEN
owncast_url = keys.OWNCAST_URL
websocket_url = keys.OWNCAST_WEBSOCKET

log = open("deleted.txt", "a")

words = ['nigger', 'faggot', 'fag', 'http', 'cum', '123test', 'kaylor']
banned_names = ["卐", "ᛋ", "nigg", "í", 'é', "gas", "jew", "test", "ttt"]

chat_name = {"displayName": "Vigilante"}
chat_response = requests.post(owncast_url + "/api/chat/register", json=chat_name)
chat_user = chat_response.json()
chat_token = chat_user["accessToken"]
print("access token acquired, async version")


def delete_message(id, text):
    msg_data = {"visible": False, "idArray": [id]}

    delete_response = requests.post(
        owncast_url + "/api/chat/messagevisibility?accessToken=" + mod_token,
        json=msg_data,
    )
    if delete_response.json()["success"] == True:
        log.write("\n" + text)
        print("DELETED: " + text)
        removed += 1
        return True
    else:
        return False
    

# main moderation logic
# makes calls to delete_message and perspective.py
async def automod(message):
    msg = json.loads(message)
    if msg["type"] == "NAME_CHANGE":
        print("NAME CHANGE DETECTED")
        ban = False
        name = msg["user"]["displayName"].lower()
        user_id = msg["user"]["id"]
        ban_request = {"userId": user_id, "enabled": False}
        for word in banned_names:
            if word in name:
                ban = True
            
        if ban == True:
            banned = requests.post(owncast_url + "/api/chat/users/setenabled?accessToken=" + mod_token, json = ban_request)
            if banned.json()["success"] == True:
                print("____________BANNED USER + " + name + "!____________")
            else:
                print("_________BAN FAILED")
                print(banned.json())

    
    if msg["type"] == "CHAT":
        chat_text = msg["body"]
        chat_id = msg["id"]
        name = msg["user"]["displayName"]
        lower_name = name.lower()
        lower_chat = chat_text.lower()
        print(name + ": " + chat_text)

        if len(chat_text) > 100:
            if perspective_ban(chat_text):
                delete_message(chat_id, chat_text)

        for word in words:
            if word in chat_text:
                delete_message(chat_id, chat_text)

        if "卐" in name or "ᛋ" in name or "nigg" in lower_name or "NÍG"in name or "NIGGéR" in name or "gas" in lower_name or "jew" in lower_name:
            delete_message(chat_id, chat_text)

removed = 0


# websocket app on_message function
def on_message(ws_app, message):
    asyncio.run(automod(message))
   


ws_URL = websocket_url + chat_token
ws_app = websocket.WebSocketApp(ws_URL, on_message=on_message)
ws_app.run_forever()
