
from json import dumps

class Constants:

    # --- FOOTERS FOR MENUS --- #

    footer_back_main = [
        [
            ["Zurück", "zurück"],
            ["Hauptmenü", "haupt"]
        ]
    ]

    footer_group_main = [
        [
            ["#all", "all"]
        ],
        [
            ["#springer", "springer"]
        ]
    ]

    footer_info_main = [
        [
            ["Infos hinzufügen", "infotexthinzufügen"],
            ["Infos entfernen", "infolöschen"]
        ],
        [
            ["Hauptmenü", "haupt"]
        ]
    ]

    footer_shoplist_delete = [
        [
            ["!!! Alles löschen !!!", "alleslöschen"]
        ]
    ]

    # --- MENUS --- #

    menu_basic = [
        ["Hauptmenü"]
    ]

    menu_main = [
        ["Info", "Schlüssel", "Gruppen"],
        ["Schichten", "Einkaufsliste", "Schulden"],
        ["Hilfe", "Stammtisch", "Check"]
    ]


    menu_add_remove = [
        ["Hinzufügen", "Entfernen"],
        ["Hauptmenü"]
    ]

    # TODO: Vielleicht sollte man überdenken, ob wir anstatt dem Zurück/Hauptmenü-Chaos generell immer nur einen Zurück-Button in der untersten Zeile wollen.
    menu_back_main = [
        ["Zurück"],
        ["Hauptmenü"]
    ]

    menu_delete_all = [
        ["Alles löschen!"],
        ["Hauptmenü"]
    ]

    menu_checked_in = [
        ["Check-out", "Daten"],
        ["Hauptmenü"]
    ]

    menu_checked_out = [
        ["Check-in", "Daten"],
        ["Hauptmenü"]
    ]

    # TODO: Das mit add_remove zusammenfassen
    menu_info_main = [
        ["Hinzufügen", "Entfernen"],
        ["Hauptmenü"]
    ]

    menu_has_no_key = [
        ["Hinzufügen", "Nachricht"],
        ["Hauptmenü"]
    ]

    menu_has_key = [
        ["Entfernen", "Nachricht"],
        ["Hauptmenü"]
    ]

    menu_make_debts = [
        ["0,50€", "0,70€", "1,00€"],
        ["1,25€", "1,50€", "1,75€"],
        ["Schulden begleichen"],
        ["Hauptmenü"]
    ]

    menu_pay_debts = [
        ["-5€", "-10€"],
        ["-20€", "-50€"],
        ["Schulden machen", "Alles zahlen"],
        ["Hauptmenü"]
    ]


    # --- GENERAL --- #

    mitarbeiterpreise = ""

#    """Mitarbeiterpreise:
# Wasser/Tee/Heißgetränke: 0,50€
# Softdrinks: 0,70€
# Bier: 1,00€
# Longdrinks: 1,75€"""
