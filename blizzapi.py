import os
import json
from blizzardapi import BlizzardApi


current_folder = '\\'.join(os.path.abspath(__file__).split('\\')[:-1])
print(current_folder)

with open(current_folder + '\\realms.json') as realms_file:
    realms = json.load(realms_file)

with open(current_folder + '\\secrets.json', 'rb') as json_file:
    creds = json.load(json_file)


class RealmNotFoundError(Exception):
    pass


class CharNotFoundError(Exception):
    pass


class BlizzAPI:
    def __init__(self):
        # Make the client
        self.client = BlizzardApi(
            creds['blizz_client_id'], creds['blizz_client_secret']
        )
        self.realms = realms
