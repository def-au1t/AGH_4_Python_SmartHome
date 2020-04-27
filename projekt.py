import json
import threading
import tkinter as tk
from tkinter import ttk

import pymongo
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

from mqtt import *
from tk_views import *
import io
import os
import sqlite3


class Main(object):
    # smart_objects = None
    # mqttm = None
    # wm = None
    # db = None

    def __init__(self):
        self.smart_objects = None
        self.db = None
        self.wm : WindowsManager = None

        load_dotenv()
        self.parse_smart_objects_config()
        self.mqtt_manager = MqttManager()
        self.connect_to_db()
        self.wm = WindowsManager(self)
        self.wm.loop()

    def try_login(self, username, password):
        if self.db is None:
            print("Nie udało się połączyć z bazą danych")
            return
        users = self.db.get_collection("users")
        user = users.find_one({"username": username})
        if not user:
            print("Nie znaleniono użytkownika w bazie!")
            self.wm.tk_login_view(info="nie udało się zalogować")

    def connect_to_db(self):
        try:
            c_string = os.getenv("CONNECTION_STRING")
            client = pymongo.MongoClient(c_string)
            self.db = client.get_database("smarthome")
        except:
            print("Cannot connect to MongoDB database!")
            exit()

    def parse_smart_objects_config(self):
        with io.open("config.json", encoding="utf-8") as config_data:
            try:
                config_text = config_data.read()
                self.smart_objects = json.loads(config_text)
            except:
                print("Cannot parse JSON config.")
                exit()


# def main():
#     main.mqtt_client.publish("test/topic", "Hello world2!");
#

if __name__ == '__main__':
    main = Main()
