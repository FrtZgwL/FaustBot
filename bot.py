
#########################
# ---   Imports     --- #
#########################

import telepot
import time
import json
from telepot.loop import MessageLoop

# Temporär?
import pprint


###############################################
# ---   Globale Variablen & Konstanten    --- #
###############################################

# --- Konstanten --- #

M_NORMAL = 0
M_PASSWORT = 1
M_SCHLÜSSEL = 2
M_GRUPPEN = 3

SUPPORTTEAM = "Cedric und Maurice"
PASSWORT = ""
TOKEN = ""

# --- Variablen --- #

menüs = {}
users = {}
data = {}

# --- Globale Variablen --- #

display_message = {}
pp = pprint.PrettyPrinter(indent=2)


###########################################
# ---   json Datein barbeiten/laden   --- #
###########################################

with open("Daten/menüs.json", "r") as f:
    menüs = json.load(f)

with open("Daten/users.json", "r") as f:
    users = json.load(f)

with open("Daten/data.json", "r") as f:
    data = json.load(f)

with open("Daten/config.json", "r") as f:
    config = json.load(f)
    if config["token"] == "":
        sys.exit("No token defined. Define it in a file called token.txt.")
    if config["passwort"] == "":
        print("WARNING: Empty Password for registering to use the bot." +
              " It could be dangerous, because anybody could use this bot" +
              " and forward messages to the channels associated to it")
    SUPPORTTEAM = config["supportteam"]
    PASSWORT = config["passwort"]
    TOKEN = config["token"]

def save(pfad, obj):
    with open(pfad, "w") as f:
        f.write(json.dumps(obj, indent=2, sort_keys=True))


# users aus datei laden

# SUPPORTTEAM aus config laden
# TOKEN aus config laden
# PASSWORT und weitere Passwörter

#########################
# ---   Funktionen  --- #
#########################


def build_name(msg):
    return msg["from"]["first_name"] + (" " + msg["chat"]["last_name"] if "last_name" in msg["chat"] else "")


def handle(msg):
    global display_message
    global users
    global data

    flavor = telepot.flavor(msg)

    if flavor == "chat":
        chat_id = msg["chat"]["id"]
        txt = msg["text"]


        ##################################
        # ---   Telegram Befehle    ---- #
        ##################################

        if "/start" == txt[:6]:
            if msg["chat"]["type"] != "private":
                bot.sendMessage(chat_id, "Dieser Befehl kann nur in privaten Chats verwendet werden.")
            else:
                # Wenn noch nicht Nutzer, dann (hinzufügen, in Passwort-Modus und) checken ob Passwort korrekt. Wenn schon Nutzer, Hauptmenü anzeigen
                if str(chat_id) not in users:
                    users[str(chat_id)] = {
                    "name":build_name(msg),
                    "modus":M_PASSWORT,
                    "current_group":"",
                    "schulden":0.0,
                    "is_allowed":False,
                    "is_finanzen":False,
                    "is_einkauf":False,
                    "is_admin":False
                    }
                    save("Daten/users.json", users)

                    bot.sendMessage(chat_id, "Hi, " + build_name(msg) + "!\nGibt bitte das Passwort ein, um den Zugriff zu erhalten. Falls du das Passwort nicht weiß, schreib eine Nachricht an " + SUPPORTTEAM + ".")

                elif users[str(chat_id)]["is_allowed"]:
                    display_message = bot.sendMessage(chat_id, "Hauptmenü", reply_markup=json.dumps(menüs["haupt"]))

                else:
                    display_message = bot.sendMessage(chat_id, "Hey, du bist leider noch nicht als Nutzer hinzugefügt. Gib bitte erst das richtige Passwort ein. Bei Problemen kanns du dich immer an " + SUPPORTTEAM + " wenden")

        elif "/help" == txt[:5] or "/?" == txt[:2]:
            pp.pprint(users)

            if str(chat_id) in users:
                if users[str(chat_id)]["is_allowed"]:
                    bot.sendMessage(chat_id, "HIER IST HILFE")
                else:
                    bot.sendMessage(chat_id, "Nur registrierte Nutzer können diese Funktion nutzen.")
            else:
                bot.sendMessage(chat_id, "Nur registrierte Nutzer können diese Funktion nutzen.")


        #####################
        # ---   Modi    --- #
        #####################
        else:
            modus = users[str(chat_id)]["modus"]

            if modus == M_PASSWORT:
                if txt == PASSWORT:
                    users[str(chat_id)]["is_allowed"] = True
                    users[str(chat_id)]["modus"] = M_NORMAL
                    save("Daten/users.json", users)

                    bot.sendMessage(chat_id, "Du wurdest erfolgreich als Nutzer hinzugefügt! Viel Spaß!")
                    display_message = bot.sendMessage(chat_id, "Hauptmenü", reply_markup=json.dumps(menüs["haupt"]))
                else:
                    display_message = bot.sendMessage(chat_id, "Bitte gibt das korrekte Passwort ein. Wenn du nicht weiter weißt, wende dich an " + SUPPORTTEAM + ".")

            elif modus == M_NORMAL:
                # Hier nach tags für Gruppennachrichten suchen
                print("Los gehts!")

            else:
                print("MODUS-FAIL!")
                print(modus)

        # debugging
        pp.pprint(users)


    elif flavor == "callback_query":
        button = msg["data"]
        msg_id = msg["message"]["message_id"]
        chat_id = msg["message"]["chat"]["id"]
        callback_id = msg["id"]

        if button == "haupt":
            bot.answerCallbackQuery(callback_id)

            display_message = bot.editMessageText((chat_id, msg_id), "Hauptmenü", reply_markup=json.dumps(menüs["haupt"]))

        elif button == "tür":
            if data["tür"]:
                open_text = "Die Tür ist offen. Hier kannst du sie schließen." # Das später zufällig

                bot.answerCallbackQuery(callback_id)
                display_message = bot.editMessageText((chat_id,msg_id), open_text, reply_markup=json.dumps(menüs["türzu"]))
            else:
                closed_text = "Die Tür ist zu. Hier kannst du sie öffnen."

                bot.answerCallbackQuery(callback_id)
                display_message = bot.editMessageText((chat_id, msg_id), closed_text, reply_markup=json.dumps(menüs["türoffen"]))

        elif button == "türzu":
            closing_text = "Die Tür ist jetzt zu"

            data["tür"] = False
            save("Daten/data.json", data)

            bot.answerCallbackQuery(callback_id, text=closing_text, show_alert=True)
            display_message = bot.sendMessage(chat_id, "Hauptmenü", reply_markup=json.dumps(menüs["haupt"]))

        elif button == "türoffen":
            opening_text = "Die Tür ist jetzt offen"

            data["tür"] = True
            save("Daten/data.json", data)

            bot.answerCallbackQuery(callback_id, text=opening_text, show_alert=True)
            display_message = bot.sendMessage(chat_id, "Hauptmenü", reply_markup=json.dumps(menüs["haupt"]))

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

bot = telepot.Bot(TOKEN)

MessageLoop(bot, handle).run_as_thread()
print("Ich lese mit ...")
while 1:
    time.sleep(10)
