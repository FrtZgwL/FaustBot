

import telepot
import json
from constants import Constants as const

def build_keyboard_menu(menu, resize_keyboard=True):
    """Takes a 2D Array with menu buttons
    Returns a json serialized string of a ReplyKeyboardMarkup object"""

    if resize_keyboard:
        string = "{\"keyboard\":" + json.dumps(menu) + ","
        string += "\"resize_keyboard\":true}"
    else:
        string = "{\"keyboard\":" + json.dumps(menu) + "}"
    return string

bot = telepot.Bot("698839060:AAEPazfjo1gvbO-DFxi6cbpq-rAOIVJPJ2g")

with open("Daten/users.json", "r") as f:
    users = json.load(f)

for user in users:
    try:
        bot.sendMessage(int(user), "Der neue Faustbot ist da! Schneller! Schöner! Besser! Und jetzt mich Check-Funktion!!!\n\nWir haben vor allem unseren Code aufgeräumt und können hoffentlich in Zukunft neue Funktionen einfacher hinzufügen.\n\nWenn was nicht funktioniert, versuch zuerst, den Chatverlauf zu leeren und den Bot neu zu starten. Wenn das nicht hilft, schreib uns @MauriceHaug oder @FrtZgwL und wir helfen dir :)", reply_markup=build_keyboard_menu(const.menu_main))
    except:
        print("Failed Attempt")
