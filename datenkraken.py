import sqlite3
import datetime
import smtplib
import csv
from email.mime.text import MIMEText

class Datenkraken:



    def setup(self): # TODO: Das in init einbauen
        conn = sqlite3.connect("debts.db")
        c = conn.cursor()

        c.execute("""CREATE TABLE debts
            (id INTEGER PRIMARY KEY, day INTEGER, month INTEGER, year INTEGER,
            hour INTEGER, minute INTEGER, second INTEGER,
            debts REAL);""") # TODO: Will ich die Total debts speichern?

        conn.close()

    def store_debts(self, debts):
        conn = sqlite3.connect("debts.db")
        c = conn.cursor()
        current = datetime.datetime.today()

        query = """INSERT INTO debts (year, month, day, hour, minute, second, debts)
            VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6});"""
        query = query.format(current.year, current.month, current.day, current.hour, current.minute, current.second, debts)

        c.execute(query)
        conn.commit()
        conn.close()

    @property
    def total_balance(self):
        conn = sqlite3.connect("debts.db")
        c = conn.cursor()

        total = 0
        for transaction in c.execute("SELECT debts FROM debts;"):
            total += transaction[0]

        conn.commit()
        conn.close()

        return total

    def print_all(self):
        conn = sqlite3.connect("debts.db")
        c = conn.cursor()

        for entry in c.execute("SELECT * FROM debts;"):
            print(entry)

        conn.commit()
        conn.close()

    def mail_last_week(self):
        conn = sqlite3.connect("debts.db")
        c = conn.cursor()

        week = datetime.timedelta(7)
        a_week_ago = datetime.datetime.today() - week

        # Get id of first entry on the day a week ago
        for i in range(8):
            try:
                query = """SELECT MIN(id) FROM debts WHERE year={} AND month={}
                AND day={};"""
                query = query.format(a_week_ago.year, a_week_ago.month, a_week_ago.day + i)

                id = c.execute(query).fetchone()[0]
                print("date a week ago:" + a_week_ago.day + i)
                print("id a week ago: " + str(id))
            except:
                continue


        # calculate new debts
        new_debts = 0
        query = """SELECT (debts) FROM debts WHERE id >= {} AND debts > 0;"""
        query = query.format(id)
        try:
            results = c.execute(query)
            for result in results:
                new_debts += result[0]
        except:
            print("Die letzte Woche wurden keine neuen Schulden gemacht.")

        # calculate payed debts
        payed_debts = 0
        query = """SELECT (debts) FROM debts WHERE id >= {} AND debts < 0;"""
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

        conn.commit()
        conn.close()

    def setup_checks(self):
        """Setup database for check-ins."""
        conn = sqlite3.connect("debts.db")
        c = conn.cursor()

        # c.execute("""CREATE TABLE checks
        # (id INTEGER PRIMARY KEY, day INTEGER, month INTEGER, year INTEGER,
        # hour INTEGER, minute INTEGER, second INTEGER,
        # check_in INTEGER, user TEXT);""") # TODO: Will ich die Total debts speichern?

        c.execute("""CREATE TABLE checks (id INTEGER PRIMARY KEY, check_in_date TEXT,
            check_in_time TEXT, check_out_date TEXT, check_out_time TEXT, user TEXT)""")

        conn.commit()
        conn.close()

    def build_check_text(self):
        """Returns user readable string with all people checked in right now."""


        return "Im Fauuuusteee bist immer nur du."

    def write_checks(self):
        """Writes all check-ins and outs to 'checks.csv'."""
        conn = sqlite3.connect("debts.db")
        c = conn.cursor()

        results = c.execute("""SELECT * FROM checks;""")

        with open("checks.csv", "w", newline="") as f:
            writer = csv.writer(f, dialect="excel")
            writer.writerows(results)

        conn.commit()
        conn.close()

    # TODO: Problem!! Man kann das System umgehen, indem man auf Telegram seinen Namen ändert!

    def check(self, user, check_in):
        """Saves check in for one user to the database."""
        conn = sqlite3.connect("debts.db")
        c = conn.cursor()

        # Get last activity
        try:
            results = c.execute("""SELECT MAX(id) FROM checks
                WHERE user = '{0}';""".format(user))
            id = next(results)[0]
        except StopIteration:
            c.execute("""INSERT INTO checks (check_in_date, check_in_time, user)
                VALUES (date('now'), time('now', 'localtime'), '{0}'');""".format(user))

        if check_in:
            c.execute("""INSERT INTO checks (check_in_date, check_in_time, user)
                VALUES (date('now'), time('now', 'localtime'), '{0}');""".format(user))
        else:
            c.execute("""UPDATE checks SET check_out_date = date('now'),
                check_out_time = time('now', 'localtime') WHERE id = {0};""".format(id))

        # query = """INSERT INTO checks (year, month, day, hour, minute, second, check_in, user)
        # VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})"""
        # query = query.format(current.year, current.month, current.day, current.hour, current.minute, current.second, check_in_int, "'" + user + "'")

        conn.commit()
        conn.close()

# Wenn als eigenes script aufgerufen, neuen Kraken und setup
if __name__ == "__main__":
    kraken = Datenkraken()

    kraken.write_checks()

    #kraken.store_debts(3)
