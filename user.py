
from json import JSONEncoder

class User:

    def __init__(self, **kwargs):
        self.id = None
        self.display_message = ""
        self.forward_to = None

        self.is_admin = False
        self.is_allowed = False
        self.is_keybearer = False
        self.is_springer = False

        self.is_checked_in = False

        self.menu = "Hauptmenü"
        self.name = ""
        self.debts = 0.0
        self.temp = ""

class UserEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, User):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

class UserDictEncoder(JSONEncoder):
    def default(self, obj):
        result_dict = {}
        for i in obj:
            result_dict[i] = obj[i].__dict__
