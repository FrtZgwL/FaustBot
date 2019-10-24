import xlwt
import json
import telepot
import schedule
import time

# An diese Nutzer werden die Schulden jede Woche gesendet
finance_staff = [795683755, 324700660, 287077960]


def send_debts():
    # Herausfinden, wie viele Schulden gemacht wurden
    with open("Daten/users.json") as f:
        users = json.load(f)

    debts_total = 0
    debts_per_user_name = {}
    for user in users:
        current_user_debts = users[user]["schulden"]
        user_name = users[user]["name"]

        debts_per_user_name[user_name] = current_user_debts
        debts_total += current_user_debts

    # Tabelle konstruieren
    wb = xlwt.Workbook()
    ws = wb.add_sheet("Schulden")

    header = xlwt.easyxf('font: bold on')

    ws.write(0, 0, "Name", header)
    ws.write(0, 1, "Schulden", header)

    i = 1
    for name in debts_per_user_name:
        ws.write(i, 0, name)
        ws.write(i, 1, debts_per_user_name[name])

        i += 1

    wb.save('Schulden.xls')

    # Nachrichten an Bot schicken
    bot = telepot.Bot("555473503:AAFpH1ogPqFnoiOiVVCQJUDjj8JNIMa9WeI")
    for staff_member in finance_staff:
        bot.sendMessage(staff_member, "Hier die aktuellen Schulden der Mitglieder im Faust.")
        bot.sendDocument(staff_member, open("Schulden.xls", "rb"))

    print("Nachrichten gesendet! Schuldenstand: {}".format(debts_total))

# Nachricht regelmäßig senden
schedule.every().monday.at("8:00").do(send_debts)

print("Sende regelmäßig Nachrichten...")
while True:
    schedule.run_pending()
    time.sleep(100)
