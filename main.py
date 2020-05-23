import json

cfg = json.load(open("config.json"))

if (cfg["debug"]):
    print("Debug mode is on")