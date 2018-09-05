
#########################
# ---   Imports     --- #
#########################

import telepot
import time
import json
from telepot.loop import MessageLoop


###############################################
# ---   Globale Variablen & Konstanten    --- #
###############################################

# --- Konstanten --- #

NORMAL = 0
PASSWORT = 1
SCHLÜSSEL = 2
GRUPPEN = 3

# --- Variablen --- #

display_message = {}
menüs = {}


#################################
# ---   json Datein laden   --- #
#################################

with open("Daten/menüs.json", "r") as f:
    menüs = json.load(f)


#########################
# ---   Funktionen  --- #
#########################

def handle(msg):
    global display_message

    flavor = telepot.flavor(msg)

    if flavor == "chat":
        # Variablen setzen
        chat_id = msg["chat"]["id"]
        txt = msg["text"]

        if "/start" == txt[:6]:
            # Wenn noch nicht Nutzer, dann (hinzufügen, in Passwort-Modus und) checken ob Passwort korrekt. Wenn schon Nutzer, Hauptmenü anzeigen
            display_message = bot.sendMessage(chat_id, "PLATZHALTER START", reply_markup=json.dumps(menüs["haupt"]))
        elif "/help" == txt[:5]:
            # Hilfe-Text anzeigen
            bot.sendMessage(chat_id, "HIER IST HILFE")

    elif flavor == "callback_query":
        button = msg["data"]
        msg_id = msg["message"]["message_id"]
        chat_id = msg["message"]["chat"]["id"]

        print("Nächstes Menü: " + button)

        if button == "haupt":
            display_message = bot.editMessageText((chat_id, msg_id), "Hauptmenü", reply_markup=json.dumps(menüs["haupt"]))

        elif button == "türzu":
            display_message = bot.editMessageText((chat_id,msg_id), "Türzumenü", reply_markup=json.dumps(menüs["türzu"]))

        elif button == "türoffen":
            display_message = bot.editMessageText((chat_id, msg_id), "Türoffenmenü", reply_markup=json.dumps(menüs["türoffen"]))

        elif button == "funktionen":
            display_message = bot.editMessageText((chat_id, msg_id), "Funktionsmenü", reply_markup=json.dumps(menüs["funktionen"]))

        elif button == "habschlüssel":
            display_message = bot.editMessageText((chat_id, msg_id), "Habschlüsselmenü", reply_markup=json.dumps(menüs["habschlüssel"]))

        elif button == "habkeinenschlüssel":
            display_message = bot.editMessageText((chat_id, msg_id), "Habkeinschlüsselmenü", reply_markup=json.dumps(menüs["habkeinschlüssel"]))

        elif button == "schulden":
            display_message = bot.editMessageText((chat_id, msg_id), "Schuldenmenü", reply_markup=json.dumps(menüs["schulden"]))

        elif button == "einkaufliste":
            display_message = bot.editMessageText((chat_id, msg_id), "Einkauflistemenü", reply_markup=json.dumps(menüs["einkaufliste"]))

        elif button == "einstellungen":
            display_message = bot.editMessageText((chat_id, msg_id), "EInstellungsmenü", reply_markup=json.dumps(menüs["einstellungen"]))
        # checken, ob einer der Tags ausgewählt wurde


#############################################
# ---   Telepot Message Loop starten    --- #
#############################################

bot = telepot.Bot("698839060:AAEPazfjo1gvbO-DFxi6cbpq-rAOIVJPJ2g")

MessageLoop(bot, handle).run_as_thread()
print("Ich lese mit ...")
while 1:
    time.sleep(10)
