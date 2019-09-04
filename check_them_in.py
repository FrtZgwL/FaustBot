
import json

with open("Daten/users.json", "r") as f:
    users = json.load(f)

for user in users:
    users[user]["is_checked_in"] = False

with open("Daten/users.json", "w") as f:
    json.dump(users, f, indent=4)
