
import datetime

LINE_LENGTH = 34

def fill(line):
    return line + (" " * (LINE_LENGTH - len(line) - 1)) + "*\n"

class Bank:
    def __init__(self):
        # Dict von id(string) zu Account
        self.accounts = {}

    def balance(self, id):
        return self.accounts[id][-1].balance

    # Für id Schulden hinzufügen
    # RETURN: None, wenns die id nicht gibt
    # RETURN: Sonst der Kontobetrag des Nutzers
    def buy(self, id, amount):
        if id in self.accounts:
            new_balance = self.accounts[id][-1].balance + amount
            self.accounts[id].append(Transaction(new_balance))
        else:
            self.accounts[id] = [Transaction(amount)]

    def clearall(self):
        for id in self.accounts:
            self.accounts[id].append(Transaction(0))

    def clear(self, id):
        self.accounts[id].append(Transaction(0))

    # Gibt die Schulden als stringing aus, None, wenns id nicht gibt
    def get_debts(self, id=None):
        # Schulden für bestimmten Nutzer
        if id:
            string = "="*LINE_LENGTH + "\n"

            user_line = "* USER ID: {}".format(id)
            user_line = fill(user_line)
            string += user_line

            account = self.accounts[id]

            for transaction in account:
                string += "="*LINE_LENGTH + "\n"

                string += "* DATE: {}\n".format(transaction.date)

                balance_line = "* BALANCE: {}".format(transaction.balance)
                balance_line = fill(balance_line)
                string += balance_line


            string += "="*LINE_LENGTH + "\n"

            return string

        # Schulden für alle Nutzer
        else:
            string = ""

            for id in self.accounts:
                string += "\n" + self.get_debts(id)

            return string


class Account (list):
    @property
    def current_transaction(self):
        try:
            return self[-1]
        except IndexError:
            return None

    @property
    def balance(self):
        return current_transaction.balance


class Transaction:
    def __init__(self, balance):
        self.date = datetime.datetime.now()
        self.balance = balance
