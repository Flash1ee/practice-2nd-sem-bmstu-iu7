import json

config = json.load(open("./config.json"))

if (config["debug"]):
    print("Debug mode is on")