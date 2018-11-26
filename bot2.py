
#########################
# ---   Imports     --- #
#########################

import telepot
import time
import json
import pickle
import hashlib
from cProfile import runctx
from telepot.loop import MessageLoop
from constants import Constants as const

# Eigene
import debts

# Temporär?
import pprint



###############################################
# ---   Globale Variablen & Konstanten    --- #
###############################################

# --- Konstanten --- #

MO_NULL = "kein Modus"
MO_NORMAL = "normal"
MO_PASSWORT = "passwort"
MO_SCHLÜSSEL = "schlüssel"
MO_EINKÄUFE = "einkauf"
MO_GRUPPEN = "gruppen"
MO_ADD_INFO_LINK = "link hinzufügen"
MO_ADD_INFO_TEXT = "info hinzufügen"
MO_SCHULDENZAHLEN = "schulden zahlen"
MO_SCHULDENMACHEN = "schulden machen"
MO_SPRINGER ="springer"
MO_ALL = "all"

SUPPORTTEAM = "@FrtZgwL und @MauriceHaug"
PASSWORT = ""
ADMIN_PASSWORT = ""
TOKEN = ""

#--- Menues ---#

ME_HAUPT = "haupt"

ME_SCHLÜSSEL = "schlüssel"

ME_SCHULDEN = "schulden"
ME_SCHULDENBEGLEICHEN = "schulden/begleichen"

ME_EINKAUFSLISTE = "einkaufsliste"
ME_ARTIKELENTFERNEN = "einkaufsliste/entfernen"

ME_GRUPPEN= "gruppen"

ME_INFO = "info"
ME_INFOLÖSCHEN = "info/löschen"

ME_TÜR = "tür"




# --- Variablen --- #

menüs = {}
pp = pprint.PrettyPrinter(indent=2)

display_message = {}
users = {}
data = {}
infotext = ""
bank = debts.Bank()



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
    ADMIN_PASSWORT = config["adminpasswort"]
    TOKEN = config["token"]

with open("Daten/schulden.bin", "rb") as f:
    bank = pickle.load(f)

#########################
# ---   Funktionen  --- #
#########################

def error(chat_id):

    users[str(chat_id)]["modus"] = MO_NORMAL
    users[str(chat_id)]["menue"] = ME_HAUPT
    save("Daten/users.json", users)

    display_message = bot.sendMessage(chat_id, "Ups! Irgendwas ist schiefgelaufen! Tippe auf \"Hilfe\" oder \"Hauptmenü\", um Hilfe zu erhalten oder zum Hauptmenü zurück zu gehen.", reply_markup=json.dumps(menüs["error"]))

def save(pfad, obj):
    with open(pfad, "w") as f:
        f.write(json.dumps(obj, indent=2, sort_keys=True))

def pickle_save(pfad, obj):
    with open(pfad, "wb") as f:
        pickle.dump(obj, f)

def build_name(msg):
    if msg["chat"]["type"] == "private":
        return msg["from"]["first_name"] + (" " + msg["chat"]["last_name"] if "last_name" in msg["chat"] else "")
    else:
        return msg["chat"]["title"]

def build_menu(items, footer, identifier = ""): # TODO
    menu = "{\"inline_keyboard\":["

    for item in items:
        menu = menu + "[{\"text\":\"" + item + "\",\"callback_data\":\"" + identifier + hashlib.md5(item.encode()).hexdigest() + "\"}],"

    for row in footer:
        menu += "["
        for button in row:
            if len(button[0]) == 1:
                menu += "{\"text\":\"" + button + "\","
                menu += "\"callback_data\":\"" + button + "\"},"
                break

            menu += "{\"text\":\"" + button[0] + "\","
            menu += "\"callback_data\":\"" + button[1] + "\"},"
        menu = menu[:-1]
        menu += "],"
    menu = menu[:-1]
    menu += "]}"

    return menu

#################################################
# ---   FUNKTIONEN FÜR BUTTON INTERAKTION   --- #
#################################################

def adddebts(betrag, chat_id, callback_id, msg_id):
    global users
    betrag = round(betrag, 2)
    users[str(chat_id)]["schulden"] = round(users[str(chat_id)]["schulden"] + betrag, 2)
    users[str(chat_id)]["schulden"]
    save("Daten/users.json", users)

    betraghinzu = str(betrag).replace(".", ",") + "€ wurden zu deinen Schulden hinzugefügt."

    bank.buy(chat_id, betrag)
    pickle_save("Daten/schulden.bin", bank)

    bot.answerCallbackQuery(callback_id, text=betraghinzu)
    display_message = bot.editMessageText((chat_id, msg_id), "Du schuldest dem Faust jetzt " + str(users[str(chat_id)]["schulden"]).replace(".", ",") + "€. Tipp auf Buttons, um mehr Schulden zu machen, oder schick mir den Betrag als Kommazahl.", reply_markup=json.dumps(menüs["schulden"]))

def mainmenu(chat_id, msg_id, callback_id):
    bot.answerCallbackQuery(callback_id)

    users[str(chat_id)]["modus"] = MO_NORMAL
    users[str(chat_id)]["menue"] = ME_HAUPT
    save("Daten/users.json", users)

    display_message = bot.editMessageText((chat_id, msg_id), "Hauptmenü", reply_markup=json.dumps(menüs["haupt"]))

def group(chat_id, msg_id, callback_id):
    bot.answerCallbackQuery(callback_id)

    users[str(chat_id)]["menue"] = ME_GRUPPEN
    save("Daten/users.json", users)
    menü = "{\"inline_keyboard\":["

    # Alle Gruppen ausgeben
    for tag in data["chats"]:
        menü += "[{\"text\":\"" + tag + "\", \"callback_data\":\"chat" + hashlib.md5(tag.encode()).hexdigest() + "\"}],"

    menü += "[{\"text\":\"#all\", \"callback_data\":\"all\"}],"

    # Springer Zeile
    menü += "[{\"text\":\"#springer\", \"callback_data\":\"springer\"}],"


    # Steuerfunktionen
    menü += "[{\"text\":\"Hauptmenü\", \"callback_data\":\"haupt\"}]]}"

    display_message = bot.editMessageText((chat_id, msg_id), "Tippe auf die Gruppe um ihnen eine Nachricht zu senden", reply_markup=build_menu(data["chats"], const.footer_group_main, "chat"))

def info(chat_id, msg_id, callback_id):
    """Shows info-menu."""

    bot.answerCallbackQuery(callback_id)

    users[str(chat_id)]["menue"] = ME_INFO
    save("Daten/users.json", users)

    display_message = bot.editMessageText((chat_id, msg_id), "Tippe auf Zeilen, um Informationen zu erhalten.", reply_markup=build_menu(data["infos"], const.footer_info_main, "info"))

def door(chat_id, msg_id, callback_id):
    bot.answerCallbackQuery(callback_id)
    if data["tür"]:
        open_text = "Die Tür ist offen. Hier kannst du sie schließen." # Das später zufällig

        display_message = bot.editMessageText((chat_id, msg_id), open_text, reply_markup=json.dumps(menüs["türzu"]))
    else:
        closed_text = "Die Tür ist zu. Hier kannst du sie öffnen."

        display_message = bot.editMessageText((chat_id, msg_id), closed_text, reply_markup=json.dumps(menüs["türoffen"]))

    users[str(chat_id)]["menue"] = ME_TÜR
    save("Daten/users.json", users)

def help_button(chat_id, msg_id, callback_id):
    bot.answerCallbackQuery(callback_id)

    help_str = "Ich bin der Faustbot 2.0! Ich Bot ermögliche dir die Kommunikation zwischen den Gruppen im Café Faust und biete dazu viele weitere Funktionen.\n\nAm einfachsten bentzt du mich, indem du dich durch das Hauptmenü klickst, du kannst aber auch immer Nachrichten an die Gruppen senden, indem du mir eine Nachricht sendest, die mit dem Tag der Gruppe beginnt. Es gibt diese Gruppen: "

    for tag in data["chats"]:
        help_str += tag + ", "
    help_str = help_str[:-2]

    help_str += "\n\nBei Fragen kannst du dich immer gerne an " + SUPPORTTEAM + " wenden."

    display_message = bot.editMessageText((chat_id, msg_id), help_str, reply_markup=json.dumps(menüs["nachrichten"]))

def help_chat(chat_id):
    help_str = "Ich bin der Faustbot 2.0! Ich Bot ermögliche dir die Kommunikation zwischen den Gruppen im Café Faust und biete dazu viele weitere Funktionen.\n\nAm einfachsten bentzt du mich, indem du dich durch das Hauptmenü klickst, du kannst aber auch immer Nachrichten an die Gruppen senden, indem du mir eine Nachricht sendest, die mit dem Tag der Gruppe beginnt. Es gibt diese Gruppen: "

    for tag in data["chats"]:
        help_str += tag + ", "
    help_str = help_str[:-2]

    help_str += "\n\nBei Fragen kannst du dich immer gerne an " + SUPPORTTEAM + " wenden."

    display_message = bot.sendMessage(chat_id, help_str, reply_markup=json.dumps(menüs["nachrichten"]))

def jumper(chat_id, msg_id, callback_id):
    global users

    bot.answerCallbackQuery(callback_id)

    users[str(chat_id)]["modus"] = MO_SPRINGER
    save("Daten/users.json", users)

    aktuelle_springer = ""
    for id in users:
        if users[id]["is_springer"]:
            aktuelle_springer += users[id]["name"] + ", "
    aktuelle_springer = aktuelle_springer[:-2]

    display_message = bot.editMessageText((chat_id, msg_id), "Schick mir bitte deine Nachricht, dann leite ich sie weiter an " + aktuelle_springer, reply_markup=json.dumps(menüs["nachrichten"]))

def key(chat_id, msg_id, callback_id):
    global users
    bot.answerCallbackQuery(callback_id)

    users[str(chat_id)]["menue"] = ME_SCHLÜSSEL
    save("Daten/users.json", users)

    schlüssel_text = "Die aktuellen Schlüsselträger sind: Das Faust"

    for user in users:
        if users[user]["is_schlüsselträger"]:
            schlüssel_text = schlüssel_text + ", " + users[user]["name"]

    if users[str(chat_id)]["is_schlüsselträger"]:
        display_message = bot.editMessageText((chat_id, msg_id), schlüssel_text, reply_markup=json.dumps(menüs["habschlüssel"]))
    else:
        display_message = bot.editMessageText((chat_id, msg_id), schlüssel_text, reply_markup=json.dumps(menüs["habkeinenschlüssel"]))

def debt(chat_id, msg_id, callback_id):
    bot.answerCallbackQuery(callback_id)

    users[str(chat_id)]["modus"] = MO_SCHULDENMACHEN
    users[str(chat_id)]["menue"] = ME_SCHULDEN
    save("Daten/users.json", users)

    display_message = bot.editMessageText((chat_id, msg_id), "Du schuldest dem Faust jetzt " + str(users[str(chat_id)]["schulden"]).replace(".", ",") + "€. Tipp auf Buttons, um mehr Schulden zu machen, oder schick mir den Betrag als Kommazahl.", reply_markup=json.dumps(menüs["schulden"]))

def shoplist(chat_id, msg_id, callback_id):
    bot.answerCallbackQuery(callback_id)

    users[str(chat_id)]["menue"] = ME_EINKAUFSLISTE
    save("Daten/users.json", users)

    liste_text = "Auf der Einkaufsliste stehen:"

    for item in data["einkaufsliste"]:
        liste_text = liste_text + "\n - " + item

    display_message = bot.editMessageText((chat_id, msg_id), liste_text, reply_markup=json.dumps(menüs["einkaufliste"]), parse_mode="Markdown")

def addkey(chat_id, msg_id, callback_id):
    global users
    warning = ""

    anzahl_schlüsselträger = 0
    for user in users:
        if users[user]["is_schlüsselträger"]:
            anzahl_schlüsselträger += 1

    if anzahl_schlüsselträger >= 4:
        warning = "\nSo viele Schlüssel gibt es nicht! Erinnere den letzten Schlüsselträger daran, sich zu entfernen."

    users[str(chat_id)]["is_schlüsselträger"] = True
    save("Daten/users.json", users)

    bot.answerCallbackQuery(callback_id, text="Du wurdest als Schlüsselträger hinzugefügt" + warning, show_alert=True)


    mainmenu(chat_id, msg_id, callback_id)


def addinfo(chat_id, msg_id, callback_id, msg):
    global users
    bot.answerCallbackQuery(callback_id)

    users[str(msg["from"]["id"])]["modus"] = MO_ADD_INFO_TEXT
    save("Daten/users.json", users)

    display_message = bot.editMessageText((chat_id, msg_id), "Schick mir bitte den Namen unter dem du deine Infos speichern willst.", reply_markup=json.dumps(menüs["nachrichten"]))

def closedoor(chat_id, msg_id, callback_id):
    global data
    closing_text = "Die Tür ist jetzt zu"

    data["tür"] = False
    save("Daten/data.json", data)

    bot.answerCallbackQuery(callback_id, text=closing_text, show_alert=True)

    mainmenu(chat_id, msg_id, callback_id)

def opendoor(chat_id, msg_id, callback_id):
    global data
    opening_text = "Die Tür ist jetzt offen"

    data["tür"] = True
    save("Daten/data.json", data)

    bot.answerCallbackQuery(callback_id, text=opening_text, show_alert=True)

    mainmenu(chat_id, msg_id, callback_id)

def rmkey(chat_id, msg_id, callback_id):
    global users

    users[str(chat_id)]["is_schlüsselträger"] = False
    users[str(chat_id)]["modus"] = MO_NORMAL
    users[str(chat_id)]["menue"] = ME_SCHLÜSSEL
    save("Daten/users.json", users)

    bot.answerCallbackQuery(callback_id, text="Du wurdest als Schlüsselträger entfernt", show_alert=True)

    mainmenu(chat_id, msg_id, callback_id)

def msgkey(chat_id, msg_id, callback_id):
    global users
    bot.answerCallbackQuery(callback_id)

    users[str(chat_id)]["modus"] = MO_SCHLÜSSEL
    save("Daten/users.json", users)

    display_message = bot.editMessageText((chat_id, msg_id), "Schick mir bitte deine Nachricht, dann leite ich sie weiter...", reply_markup=json.dumps(menüs["nachrichten"]))

def cleardebt(chat_id, msg_id, callback_id):
    global users
    bot.answerCallbackQuery(callback_id)

    users[str(chat_id)]["modus"] = MO_SCHULDENZAHLEN
    users[str(chat_id)]["menue"] = ME_SCHULDENBEGLEICHEN
    save("Daten/users.json", users)

    bank.clear(chat_id)
    pickle_save("Daten/schulden.bin", bank)

    display_message = bot.editMessageText((chat_id, msg_id), "Du schuldest dem Faust. " + str(users[str(chat_id)]["schulden"]) + "€. Schick mir den Betrag, den du in die Kasse gezahlt hast, oder tipp auf \"Alles zahlen\"", reply_markup=json.dumps(menüs["schuldenbegleichen"]))

def delldebt(chat_id, msg_id, callback_id):
    global users

    users[str(chat_id)]["schulden"] = 0.0
    save("Daten/users.json", users)

    bot.answerCallbackQuery(callback_id, text="Alle deine Schulden wurden gelöscht.", show_alert=True)

    mainmenu(chat_id, msg_id, callback_id)

def addshoplist(chat_id, msg_id, callback_id):
    bot.answerCallbackQuery(callback_id)

    users[str(chat_id)]["modus"] = MO_EINKÄUFE
    save("Daten/users.json", users)

    display_message = bot.editMessageText((chat_id, msg_id), "Schick mir bitte deine Einkaufswünsche, ich schreibe sie auf die Liste...", reply_markup=json.dumps(menüs["nachrichten"]))

def clearshoplist(chat_id, msg_id, callback_id):
    bot.answerCallbackQuery(callback_id)

    users[str(chat_id)]["menue"] = ME_ARTIKELENTFERNEN

    display_message = bot.editMessageText((chat_id, msg_id), "Tippe Artikel an, um sie zu entfernen.", reply_markup=build_menu(data["einkaufsliste"], [[["!!! Alles löschen !!!", "alleslöschen"]], [["Zurück", "zurück"], ["Hauptmenü", "haupt"]]]))

def dellshoplist(chat_id, msg_id, callback_id):
    data["einkaufsliste"] = []
    save("Daten/data.json", data)

    bot.answerCallbackQuery(callback_id, text="Die Einkaufsliste ist jetzt leer.", show_alert=True)

    mainmenu(chat_id, msg_id, callback_id)

def dellitem(chat_id, msg_id, callback_id, button):
    for item in data["einkaufsliste"]:
        if button == hashlib.md5(item.encode()).hexdigest():
            data["einkaufsliste"].remove(item)
            save("Daten/data.json", data)
            bot.answerCallbackQuery(callback_id, text = item + " wurde von der Einkaufsliste gelöscht. Tippe weitere Artikel an, um sie zu löschen.")

            display_message = bot.editMessageText((chat_id, msg_id), "Tippe Artikel an, um sie zu entfernen.", reply_markup=build_menu(data["einkaufsliste"], const.footer_shoplist_delete))

            return True

def msggroup(chat_id, msg_id, callback_id, button):
    for tag in data["chats"]:
        if button == "chat" + hashlib.md5(tag.encode()).hexdigest():
            bot.answerCallbackQuery(callback_id)

            users[str(chat_id)]["modus"] = MO_GRUPPEN
            users[str(chat_id)]["forward_to"] = data["chats"][tag][0]
            save("Daten/users.json", users)
            display_message = bot.editMessageText((chat_id, msg_id), "Bitte sende mir deine Nachricht, dann leite ich sie an " + data["chats"][tag][1] + " weiter...", reply_markup=json.dumps(menüs["nachrichten"]))

            return True

def showinfo(chat_id, msg_id, callback_id, button):
    for info in data["infos"]:
        if button == "info" + hashlib.md5(info.encode()).hexdigest():
            bot.answerCallbackQuery(callback_id)
            display_message= bot.editMessageText((chat_id, msg_id), data["infos"][info][1], reply_markup=json.dumps(menüs["nachrichten"]))

            return True

def dellinfo(chat_id, msg_id, callback_id):
    """Shows Menu that allows user to delete infos."""

    bot.answerCallbackQuery(callback_id)

    users[str(chat_id)]["menue"] = ME_INFOLÖSCHEN
    save("Daten/users.json", users)

    display_message = bot.editMessageText((chat_id, msg_id), "Tippe auf die Zeile, um sie zu löschen.", reply_markup=build_menu(data["infos"], const.footer_back_main, "deleteinfo"))

def deleteinfo(chat_id, msg_id, callback_id, button):
    """Deletes one info named button and shows info menu. Returns true if info was deleted."""

    global data

    # Search if button is an info to delete
    for item in data["infos"].copy():
        if button == "deleteinfo" + hashlib.md5(item.encode()).hexdigest():
            # Delete Info
            del data["infos"][item]
            save("Daten/data.json", data)

            # Show notification
            bot.answerCallbackQuery(callback_id, text = item + " wurde gelöscht. Tippe weitere Infos an, um sie zu löschen.")

            # Show new menu
            display_message = bot.editMessageText((chat_id, msg_id), "Tippe auf weitere Infos, um sie zu löschen.", reply_markup=build_menu(data["infos"], const.footer_back_main, "deleteinfo"))

            return True

def all(chat_id, msg_id, from_id):
    global users

    if users[str(from_id)]["is_admin"]:

        users[str(chat_id)]["modus"] = MO_ALL
        save("Daten/users.json", users)

        display_message = bot.editMessageText((chat_id, msg_id), "Bitte sende mir die Nachricht zu, die ich weitergeleitet soll.", reply_markup=json.dumps(menüs["nachrichten"]))
    else:
        bot.sendMessage(chat_id, "Nur admins können an alle eine Nachricht schreiben.", reply_markup=json.dumps(menüs["nachrichten"]))




#############################################
# ---   FUNKTIONEN FÜR CHAT-INTERAKTION --- #
#############################################

def chat_passwort(chat_id, txt):
    global data
    global display_message

    if hashlib.sha256(txt.encode()).hexdigest() == PASSWORT:
        users[str(chat_id)]["is_allowed"] = True
        users[str(chat_id)]["modus"] = MO_NORMAL
        save("Daten/users.json", users)

        bot.sendMessage(chat_id, "Du wurdest erfolgreich als Nutzer hinzugefügt! Viel Spaß!")
        display_message = bot.sendMessage(chat_id, "Hauptmenü", reply_markup=json.dumps(menüs["haupt"]))
    else:
        display_message = bot.sendMessage(chat_id, "Bitte gibt das korrekte Passwort ein. Wenn du nicht weiter weißt, wende dich an " + SUPPORTTEAM + ".")


#def chat_extern(list_chat_id, txt, msg_id):

    #try:
        #bot.forwardMessage(list_chat_id, from_chat_id, message_id, disable_notification=None)


def chat_gruppen(chat_id, txt, msg_id):
    global display_message
    global data

    try:
        bot.forwardMessage(users[str(chat_id)]["forward_to"], chat_id, msg_id)
        if users[str(chat_id)]["forward_to"] > 0: # only for private chats
            bot.sendMessage(users[str(chat_id)]["forward_to"], "Hauptmenü", reply_markup=json.dumps(menüs["nachrichten"]))

        display_message = bot.sendMessage(chat_id, "Deine Nachricht wurde erfolgreich versendet.", reply_markup=json.dumps(menüs["nachrichten"]))
    except telepot.exception.BotWasKickedError:
        display_message = bot.sendMessage(chat_id, "Sorry, aber die Gruppe gibt es nicht mehr. Bitte melde dich bei " + SUPPORTTEAM + ".", reply_markup=json.dumps(menüs["nachrichten"]))

def chat_springer(chat_id, txt, msg_id):
    global display_message

    there_are_jumpers = False

    for id in users:
        if users[id]["is_springer"]:
            there_are_jumpers = True

            bot.forwardMessage(int(id), chat_id, msg_id)
            bot.sendMessage(int(id), "Hauptmenü", reply_markup=json.dumps(menüs["nachrichten"]))

    if there_are_jumpers:
        display_message = bot.sendMessage(chat_id, "Deine Nachricht wurde erfolgreich versendet.", reply_markup=json.dumps(menüs["nachrichten"]))

    else:
        display_message = bot.sendMessage(chat_id, "Es gibt im Moment kein Springer", reply_markup=json.dumps(menüs["nachrichten"]))

def chat_schuldenzahlen(chat_id, txt):
    global users
    global display_message
    aktuelle_schulden = users[str(chat_id)]["schulden"]
    #aktuelle_schulden = round(aktuelle_schulden, 2)

    try:
        betrag = abs(float(txt.replace(",", ".").replace("€", "")))
        #betrag = round(betrag, 2)

        if aktuelle_schulden - betrag < 0:
            display_message = bot.sendMessage(chat_id, "Du schuldest dem Faust " + str(aktuelle_schulden).replace(".", ",") + "€. Du kannst nicht mehr zurückzahlen, als du dem Faust schuldest. Bitte sende mir den zurückgezahlten Betrag als Kommazahl", parse_mode="Markdown", reply_markup=json.dumps(menüs["nachrichten"]))
        else:
            users[str(chat_id)]["schulden"] = round(aktuelle_schulden - betrag, 2)
            users[str(chat_id)]["modus"] = MO_SCHULDENZAHLEN
            save("Daten/users.json", users)

            display_message = bot.sendMessage(chat_id, "Von deiner Schuldenliste wurden " + str(betrag).replace(".", ",") + "€ gestrichen. Du schuldest dem Faust noch " + str(round(aktuelle_schulden-betrag,2)).replace(".", ",") + "€", parse_mode="Markdown", reply_markup=json.dumps(menüs["schuldenbegleichen"]))

    except ValueError as e:
        display_message = bot.sendMessage(chat_id, "Bitte sende mir deine Schulden entweder als ganze Zahl _10_, bzw. Kommazahl im Format:  _1,2_ oder _1.2_. Deine aktuellen Schulden sind: _" + str(aktuelle_schulden).replace(".", ",") + "€_", parse_mode="Markdown", reply_markup=json.dumps(menüs["nachrichten"]))

def chat_schuldenmachen(chat_id, txt):
    global users
    global display_message
    aktuelle_schulden = users[str(chat_id)]["schulden"]

    try:
        betrag = abs(float(txt.replace(",", ".").replace("€", "")))

        users[str(chat_id)]["schulden"] = round(aktuelle_schulden + betrag, 2)
        users[str(chat_id)]["modus"] = MO_SCHULDENMACHEN
        save("Daten/users.json", users)

        display_message = bot.sendMessage(chat_id, "Zu deinen Schulden wurden " + str(betrag).replace(".", ",") + "€ addiert. Du schuldest dem Faust noch " + str(aktuelle_schulden+betrag).replace(".", ",") + "€", parse_mode="Markdown", reply_markup=json.dumps(menüs["schulden"]))

    except ValueError as e:
        display_message = bot.sendMessage(chat_id, "Bitte sende mir deine Schulden entweder als ganze Zahl _10_, bzw. Kommazahl im Format:  _1,2_ oder _1.2_. Deine aktuellen Schulden sind: _" + str(aktuelle_schulden).replace(".", ",") + "€_", parse_mode="Markdown", reply_markup=json.dumps(menüs["nachrichten"]))

def chat_schluessel(chat_id, msg_id):
    # Nachricht an alle Schlüsselträger senden
    for user in users:
        if users[user]["is_schlüsselträger"]:
            bot.forwardMessage(int(user), chat_id, msg_id)
            display_message = bot.sendMessage(int(user), "Klick auf _Hauptmenü_, um zurück zum Hauptmenü zu kommen", parse_mode="Markdown", reply_markup=json.dumps(menüs["nachrichten"]))
        bot.sendMessage(chat_id, "Deine Nachricht wurde erfolgreich weitergeleitet.", reply_markup=json.dumps(menüs["nachrichten"]))

def chat_einkaeufe(chat_id, txt):
    global data
    global display_message

    # Einzelne Artikel zu Einkaufsliste hinzufügen
    if "#" == txt[0]:
        txt_split =txt.strip().split(" ")
        display_Message = bot.sendMessage(chat_id, "Die <i>#-Funktion</i> ist in diesem Untermenü nicht verwendbar, bitte klicke auf Hauptmenü oder gibt einen Artikel einn, den du zur Einkaufliste hinzufügen willst.", parse_mode="HTML",reply_markup=json.dumps(menüs["nachrichten"]))
    else:
        if txt in data["einkaufsliste"]:
            display_message = bot.sendMessage(chat_id, "_" + txt + "_ ist schon auf der Einkaufsliste. Aber schick mir gerne weitere Artikel...", parse_mode="Markdown", reply_markup=json.dumps(menüs["nachrichten"]))
        else:
            artikel = txt + " (von " + users[str(chat_id)]["name"] + ")"

            data["einkaufsliste"].append(artikel)
            save("Daten/data.json", data)
            display_message = bot.sendMessage(chat_id, "_" + txt + "_ wurde zur Einkaufsliste hinzugefügt. Schick mir gerne weitere Artikel...", parse_mode="Markdown", reply_markup=json.dumps(menüs["nachrichten"]))

def chat_add_info(chat_id, txt):
    global data
    global users
    global infotext
    global display_message

    if infotext in data["infos"]:
        # Zweiter Durchlauf: Text eingeben
        data["infos"][infotext][1] = txt
        save("Daten/data.json", data)

        display_message = bot.sendMessage(chat_id, "Die neuen Informationen wurden unter dem Namen _" + infotext + "_ gespeichert.", parse_mode="Markdown", reply_markup=json.dumps(menüs["haupt"]))

        infotext = ""
        users[str(chat_id)]["modus"] = MO_NORMAL
        users[str(chat_id)]["menue"] = ME_HAUPT
        save("Daten/users.json", users)

    elif infotext == "":
        # Erster Durchlauf: Name und Typ eingeben
        data["infos"][txt] = ["TEXT", "...Leere Information..."]
        save("Daten/data.json", data)

        infotext = txt

        # Text eingabe auffordern
        display_message = bot.sendMessage(chat_id, "Schick mir jetzt bitte die Informationen, die du speichern willst")

    else:
        error(chat_id)

def chat_normal(chat_id, txt, msg):
    global display_message

    if txt[0] == "#":
        txt_split =txt.strip().split(" ")
        i= 0
        tags = []
        while i < len(txt_split) and txt_split[i][0] == "#":
            tags.append(txt_split[i].lower())
            i+=1
        if i != len(txt_split) or "reply_to_message" in msg:
            approved = []
            rejected = []
            for tag in tags:
                if tag in data["chats"]:
                    if data["chats"][tag][0] !=str(chat_id):
                        group_id = data["chats"][tag][0]
                        group_name = data["chats"][tag][1]

                        try:
                            bot.forwardMessage(group_id, chat_id, msg["message_id"])
                            bot.sendMessage(chat_id, "Deine Nachricht wurde erfolgreich weitergeleitet an <i>" + group_name + "</i>", parse_mode="HTML", reply_markup=json.dumps(menüs["nachrichten"]))
                            if "reply_to_message" in msg:
                                bot.forwardMessage(group_id, chat_id, msg["reply_to_message"]["message_id"])
                                bot.sendMessage(chat_id, "Deine Nachricht wurde erfolgreich weitergeleitet an <i>" + group_name + "</i>", parse_mode="HTML", reply_markup=json.dumps(menüs["nachrichten"]))
                            approved.append(group_name)
                        except telepot.exception.BotWasKickedError:
                            rejected.append(tag)
                else:
                    rejected.append(tag)
            if len(rejected) > 0:
                bot.sendMessage(chat_id,"Ich konnte leider an folgende Tags keine Nachricht senden: <i>" + ", ".join(rejected) + "</i>\nFalls der Tag trotzdem in Gruppen angezeigt wird, wurde die Gruppe gelöscht bitte melde dich in diesem Fall bei " + SUPPORTTEAM + "." , parse_mode="HTML", reply_markup=json.dumps(menüs["error"]))
        else:
            # Fehler, weil leere Nachricht mit Tags
            bot.sendMessage(chat_id, "Du kannst keine leeren Nachrichten senden. Bitte sende mir eine Nachricht mit den Tags", reply_markup=json.dumps(menüs["error"]))
    else:
        # Fehler, weil irgend ne Nachricht
        error(chat_id)

def chat_send_all(chat_id, msg_id, msg):
    global display_message

    benutzer = []
    abgelehnte_benutzer = []

    for user in users:
        name = users[user]["name"]
        try:
            bot.forwardMessage(int(user), chat_id, msg["message_id"])
            display_message = bot.sendMessage(int(user), "Klick auf _Hauptmenü_, um zurück zum Hauptmenü zu kommen", parse_mode="Markdown", reply_markup=json.dumps(menüs["nachrichten"]))

            benutzer.append(name)
        except telepot.exception.TelegramError:
            abgelehnte_benutzer.append(name)

    display_message = bot.sendMessage(chat_id, "Deine Nachricht wurde erfolgreich an <i>" + ", ".join(benutzer) + " </i> weitergeleitet. Jetzt  kommen alle Namen an die es nicht geklappt hat:" + ", ".join(abgelehnte_benutzer), parse_mode="HTML", reply_markup=json.dumps(menüs["nachrichten"]))



def handle(msg):
    global display_message
    global users
    global data

    flavor = telepot.flavor(msg)


##################################
# ---   TELEGRAM BEFEHLE    ---- #
##################################

    if flavor == "chat":
        chat_id = msg["chat"]["id"]
        from_id = msg["from"]["id"] # Das muss noch konsequenter umgesetzt werden
        txt = msg["text"]

        if "/start" == txt[:6]:
            if msg["chat"]["type"] != "private":
                bot.sendMessage(chat_id, "/start geht nur in Privatchats.")

            else:
                if str(chat_id) not in users:
                    users[str(chat_id)] = {
                    "name":build_name(msg),
                    "modus":MO_PASSWORT,
                    "menue":ME_HAUPT,
                    "current_group":"",
                    "schulden":0.0,
                    "is_allowed":False,
                    "is_finanzen":False,
                    "is_einkauf":False,
                    "is_admin":False,
                    "is_schlüsselträger":False,
                    "is_springer":False
                    }
                    save("Daten/users.json", users)

                    bot.sendMessage(chat_id, "Hi, " + build_name(msg) + "!\nGib bitte das Passwort ein, um Zugriff zu erhalten. Falls du das Passwort nicht weiß, schreib eine Nachricht an " + SUPPORTTEAM + ".")

                elif users[str(chat_id)]["is_allowed"]:
                    users[str(chat_id)]["modus"] = MO_NORMAL
                    users[str(chat_id)]["menue"] = ME_HAUPT
                    save("Daten/users.json", users)

                    display_message = bot.sendMessage(chat_id, "Hauptmenü", reply_markup=json.dumps(menüs["haupt"]))

                else:
                    display_message = bot.sendMessage(chat_id, "Hey, du bist leider noch nicht als Nutzer hinzugefügt. Gib bitte erst das richtige Passwort ein. Bei Problemen kanns du dich immer an " + SUPPORTTEAM + " wenden")

        # elif "/cheat" == txt[:len("/cheat")]:
        #
        #     chats = {}
        #     global data
        #
        #     with open("Daten/chats.json", "r") as f:
        #         chats = json.load(f)
        #
        #     for tag in chats:
        #         id = chats[tag]["id"]
        #         name = chats[tag]["name"]
        #
        #         data["chats"][tag] = [int(id), name] #TODO NOW
        #
        #     save("Daten/data.json", data)

        elif "/help" == txt[:5] or "/?" == txt[:2]:
            if str(chat_id) in users:
                if users[str(chat_id)]["is_allowed"]:
                    help_chat(chat_id)
                else:
                    bot.sendMessage(chat_id, "Nur registrierte Nutzer können diese Funktion nutzen. Du musst zuerst das korrekte Passwort eingeben.")
            else:
                bot.sendMessage(chat_id, "Nur registrierte Nutzer können diese Funktion nutzen. Du musst zuerst das korrekte Passwort eingeben.")

        elif "/admin" == txt[:6]:
            if msg["chat"]["type"] != "private":
                bot.sendMessage(chat_id, "/admin geht nur in Privatchats.")

            else:
                if ADMIN_PASSWORT == hashlib.sha256(txt[7:].encode()).hexdigest():
                    users[str(msg["from"]["id"])]["is_admin"] = True
                    save("Daten/users.json", users)

                    display_message = bot.sendMessage(chat_id, "Du wurdest als Admin hinzugefügt!")
                else:
                    display_message = bot.sendMessage(chat_id,
                    "Falsches Passwort!")

        elif "/add" == txt[:4]:
            if not users[str(from_id)]["is_admin"]:
                bot.sendMessage(chat_id, "Nur admins können neue Gruppen hinzufügen.")

            elif msg["chat"]["type"] != "group":
                bot.sendMessage(chat_id, "\"/add\" ist nur dazu da, um _normale Gruppen_ hinzuzufügen.", parse_mode="Markdown")

            else:
                # Befehl formal überprüfen
                if len(txt) < 5:
                    bot.sendMessage(chat_id, "Du musst einen Tag für deine Gruppe angeben. Zum Beispiel so: _#meinegruppe_", parse_mode="Markdown",)
                elif txt[5] != "#":
                    bot.sendMessage(chat_id, "Jeder Tag muss mit einem \"#\" beginnen. Zum Beispiel so: _#meinegruppe_", parse_mode="Markdown")
                elif " " in txt[5:]:
                    bot.sendMessage(chat_id, "Tags dürfen nur aus einem Wort bestehen. Zum Beispiel so: _#meinegruppe_", parse_mode="Markdown")
                # Neue Gruppe hinzufügen
                else:
                    data["chats"][txt.lower()[5:]] = [chat_id, build_name(msg)]
                    save("Daten/data.json", data)

                    bot.sendMessage(chat_id, "_" + txt.lower()[5:] + "_ wurde als neue Gruppe hinzugefügt.", parse_mode="Markdown")

        elif "/debts" == txt[:6]:
            if (users[str(chat_id)]["is_admin"] | users[str(chat_id)]["is_finanzen"]):
                for id in users:
                    try:
                        bot.sendMessage(chat_id, users[id]["name"] + "\n" + bank.get_debts(int(id)))
                    except IndexError:
                        bot.sendMessage(chat_id, users[id]["name"] + "\n" "Keine Einträge+\n\n")
            else:
                bot.sendMessage(chat_id, "Sorry, aber du hast nicht das Recht, diese Funktion zu benutzen...\nDrück auf /start um den Bot zu starten.")

#######################################################
#           ---   CHAT INTERAKTION    --- #
#######################################################

        elif msg["chat"]["type"] == "private":

            modus = 0

            # Wenn noch kein Nutzer, Fehlermeldung und rausschmeißen
            if str(msg["from"]["id"]) not in users:
                bot.sendMessage(msg["chat"]["id"], "Du bist noch nicht als Nutzer eingetragen. Starte den chat mit dem Bot durch \"/start\" und gib das Passwort ein.")
            else:
                modus = users[str(chat_id)]["modus"]

            # --- TASTATURBUTTON INTERAKTION --- #

            if txt == "hauptmenü":




            # --- ANTWORTEN IN PRIVATCHATS ---- #

            if modus == MO_PASSWORT:
                chat_passwort(chat_id, txt)

            elif modus == MO_NORMAL:
                chat_normal(chat_id, txt, msg)

            elif modus == MO_GRUPPEN:
                chat_gruppen(chat_id, txt, msg["message_id"])

            elif modus == MO_SPRINGER:
                chat_springer(chat_id, txt, msg["message_id"])

            elif modus == MO_SCHULDENZAHLEN: # TODO zu viel weg + negativ
                chat_schuldenzahlen(chat_id, txt)

            elif modus == MO_SCHULDENMACHEN:
                chat_schuldenmachen(chat_id, txt)

            elif modus == MO_SCHLÜSSEL:
                chat_schluessel(chat_id, msg["message_id"])

            elif modus == MO_EINKÄUFE:
                chat_einkaeufe(chat_id, txt)

            elif modus == MO_ADD_INFO_TEXT:
                chat_add_info(chat_id, txt)

            elif modus == MO_ALL:
                chat_send_all(chat_id, msg["message_id"], msg)





########################################################
            # ---   BUTTON INTERAKTION  --- #
########################################################

    elif flavor == "callback_query":
        button = msg["data"]
        msg_id = msg["message"]["message_id"]
        chat_id = msg["message"]["chat"]["id"]
        callback_id = msg["id"]
        menue = users[str(chat_id)]["menue"]

        if button == "haupt":
            mainmenu(chat_id, msg_id, callback_id)

        elif button == "hilfe":
            help_button(chat_id, msg_id, callback_id)

        elif button == "zurück":

            if menue == "info/löschen":
                info(chat_id, msg_id, callback_id)

            elif menue == "einkaufsliste/entfernen":
                shoplist(chat_id, msg_id, callback_id)

            elif menue == "schulden/begleichen":
                debt(chat_id, msg_id, callback_id)

            elif menue == "info/löschen":
                info(chat_id, msg_id, callback_id)

        elif menue == "haupt":

            if button == "gruppen":
                group(chat_id, msg_id, callback_id)

            elif button == "info":
                info(chat_id, msg_id, callback_id)

            elif button == "schlüssel":
                key(chat_id, msg_id, callback_id)

            elif button == "schulden":
                debt(chat_id, msg_id, callback_id)

            elif button == "einkaufsliste":
                shoplist(chat_id, msg_id, callback_id)

            elif button == "tür":
                door(chat_id, msg_id, callback_id)

            else:
                error(chat_id)

        elif menue == "schlüssel":

            if button =="schlüsselhinzufügen":
                addkey(chat_id, msg_id, callback_id)

            elif button == "schlüsselentfernen":
                rmkey(chat_id, msg_id, callback_id)

            elif button == "schlüsselnachricht":
                msgkey(chat_id, msg_id, callback_id)

            else:
                error(chat_id)

        elif menue[:8] == "schulden":
            if menue[:19] == "schulden/begleichen":
                if button == "alleszahlen":
                    delldebt(chat_id, msg_id, callback_id)

                elif button == "schulden":
                    debt(chat_id, msg_id, callback_id)

                else:
                    error(chat_id)

            elif button == "schuldenbegleichen":
                cleardebt(chat_id, msg_id, callback_id)

            elif button == "0,50€":
                adddebts(0.5, chat_id, callback_id, msg_id)

            elif button == "0,70€":
                adddebts(0.7, chat_id, callback_id, msg_id)

            elif button == "1,00€":
                adddebts(1.0, chat_id, callback_id, msg_id)

            elif button == "1,25€":
                adddebts(1.25, chat_id, callback_id, msg_id)

            elif button == "1,50€":
                adddebts(1.5, chat_id, callback_id, msg_id)

            elif button == "1,75€":
                adddebts(1.75, chat_id, callback_id, msg_id)

            else:
                error(chat_id)

        elif menue[:13] == "einkaufsliste":

            if menue[:23] == "einkaufsliste/entfernen":
                if dellitem(chat_id, msg_id, callback_id, button):
                    pass

                elif button == "alleslöschen":
                    dellshoplist(chat_id, msg_id, callback_id)

                else:
                    error(chat_id)

            elif button == "hinzufügen":
                addshoplist(chat_id, msg_id, callback_id)

            elif button == "entfernen":
                clearshoplist(chat_id, msg_id, callback_id)

            else:
                error(chat_id)

        elif menue == "gruppen":
            if msggroup(chat_id, msg_id, callback_id, button):
                pass

            elif button == "springer":
                jumper(chat_id, msg_id, callback_id)

            elif button == "all":
                all(chat_id, msg_id, msg["from"]["id"])

            else:
                error(chat_id)

        elif menue[:4] == "info":
            if showinfo(chat_id, msg_id, callback_id, button):
                pass

            elif menue[:12] == "info/löschen":
                if deleteinfo(chat_id, msg_id, callback_id, button):
                    pass
                else:
                    error(chat_id)

            elif button == "infolöschen":
                dellinfo(chat_id, msg_id, callback_id)

            elif button == "infotexthinzufügen":
                addinfo(chat_id, msg_id, callback_id, msg)

            else:
                error(chat_id)

        elif menue == "tür":

            if button == "türzu":
                closedoor(chat_id, msg_id, callback_id)

            elif button == "türoffen":
                opendoor(chat_id, msg_id, callback_id)

            else:
                error(chat_id)

    else:
        error(chat_id)


    # debugging
    #pp.pprint(msg)
    #pp.pprint(users)


#################################
# ---   TELEPOT STARTEN     --- #
#################################

bot = telepot.Bot(TOKEN)

MessageLoop(bot, handle).run_as_thread()
print("Ich lese mit ...")
while 1:
    time.sleep(10)
