import sqlite3
import datetime
import smtplib
from email.mime.text import MIMEText

class Datenkraken:

    def __init__(self):
        self.conn = sqlite3.connect("debts.db")

        try:
            c = self.conn.cursor()

            for obj in c.execute("""SELECT MAX(id) FROM debts"""):
                print("Max_id: " + str(obj))
        except sqlite3.OperationalError:
            print("DATENKRAKEN: Es wurde noch keine Datenbank erstellt. Führe bitte den \"setup\"-Befehl aus")

    def setup(self): # TODO: Das in init einbauen
        c = self.conn.cursor()

        c.execute("""CREATE TABLE debts
        (id INTEGER PRIMARY KEY, day INTEGER, month INTEGER, year INTEGER,
        hour INTEGER, minute INTEGER, second INTEGER,
        debts REAL)""") # TODO: Will ich die Total debts speichern?

    def store_debts(self, debts):
        c = self.conn.cursor()
        current = datetime.datetime.today()

        query = """INSERT INTO debts (year, month, day, hour, minute, second, debts)
        VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6})"""
        query = query.format(current.year, current.month, current.day, current.hour, current.minute, current.second, debts)

        c.execute(query)
        self.conn.commit()

    @property
    def total_balance(self):
        c = self.conn.cursor()

        total = 0
        for transaction in c.execute("SELECT debts FROM debts"):
            total += transaction[0]

        return total

    def print_all(self):
        c = self.conn.cursor()
        for entry in c.execute("SELECT * FROM debts"):
            print(entry)

    def mail_last_week(self):
        c = self.conn.cursor()

        week = datetime.timedelta(7)
        day = datetime.timedelta(1)
        a_week_ago = datetime.datetime.today() - week

        # Get id of first entry on the day a week ago
        for i in range(7):
            try:
                query = """SELECT MIN(id) FROM debts WHERE year={} AND month={}
                AND day={}"""
                query = query.format(a_week_ago.year, a_week_ago.month, a_week_ago.day - (day.days * i)))

                id = c.execute(.format().fetchone()[0]
                print("id a week ago: " + str(id))



        # calculate new debts
        new_debts = 0
        query = """SELECT (debts) FROM debts WHERE id >= {} AND debts > 0"""
        query = query.format(id)
        try:
            results = c.execute(query)
            for result in results:
                new_debts += result[0]
        except:
            print("Die letzte Woche wurden keine neuen Schulden gemacht.")

        # calculate payed debts
        payed_debts = 0
        query = """SELECT (debts) FROM debts WHERE id >= {} AND debts < 0"""
        query = query.format(id)
        try:
            results = c.execute(query)
            for result in results:
                payed_debts += result[0]
        except:
            print("Die letzte Woche wurden keine alten Schulden bezahlt")

        total_debts = self.total_balance

        smtp_ssl_host = "smtp.strato.de"
        smtp_ssl_port = 465
        username = "bot@cafefaust.de"
        password = "sk8enmachtspass"
        sender = username
        targets = ["cedrictd.ctd@gmail.com"]

        msg = MIMEText("Heyo! Diese Woche wurden beim Faust " + str(new_debts) + "€ neue Schulden gemacht. Es wurden " + str(payed_debts) + "€ alte Schulden bezahlt. Insgesamt schulden die Mitarbeiter dem Faust damit noch " + str(total_debts) + "€.")
        msg["Subject"] = "Faust Schulden diese Woche"
        msg["From"] = sender
        msg["To"] = ", ".join(targets)

        server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
        server.login(username, password)
        server.sendmail(sender, targets, msg.as_string())
        server.quit()

    def __del__(self):
        self.conn.close()

# Wenn als eigenes script aufgerufen, neuen Kraken und setup
if __name__ == "__main__":
    kraken = Datenkraken()

    kraken.mail_last_week()

    #kraken.store_debts(3)
