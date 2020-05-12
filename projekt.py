import io
import json
import os
import time

import bcrypt as bcrypt
import pymongo
import pyotp
import qrcode
from bson.binary import Binary
from dotenv import load_dotenv

from mqtt import *
from tk_views import *


class Main(object):
    def __init__(self):
        self.smart_objects = None
        self.db = None
        self.wm: WindowsManager = None
        self.logged = "test"

        load_dotenv()
        self.parse_smart_objects_config()
        self.mqtt_manager = MqttManager(self)

        self.connect_to_db()
        self.wm = WindowsManager(self)
        self.wm.loop()

    def try_login(self, username, password):
        username = username.get()
        password = password.get()
        if self.db is None:
            print("Nie udało się połączyć z bazą danych")
            return
        users = self.db.get_collection("users")
        user = users.find_one({"username": username})
        if not user:
            print("Nie znaleziono użytkownika w bazie!")
            self.wm.tk_login_view(info="Nieprawidłowa nazwa użytkownika")
        elif bcrypt.checkpw(password.encode('utf-8'), user['password']):
            self.wm.tk_login_code_view(username=username, key=user['otp_key'])
        else:
            self.wm.tk_login_view(info="Nieprawidłowe hasło")

    def try_login_code(self, username, key, input_code):
        input_code = input_code.get()
        if self.db is None:
            print("Nie udało się połączyć z bazą danych")
            return
        current_key = pyotp.TOTP(key).now()
        if input_code == current_key:
            self.logged = username
            self.wm.tk_logged()
        else:
            self.wm.tk_login_code_view(username=username, key=key, info="Niepoprawny kod")

    def logout(self):
        self.logged = None
        self.wm.window.destroy()
        self.wm = WindowsManager(self)

    def try_register(self, username, password, password2):
        username = username.get()
        password = password.get()
        password2 = password2.get()
        if self.db is None:
            print("Nie udało się połączyć z bazą danych")
            self.wm.tk_register_view(info="Nie udało się połączyć z bazą!")
            return
        if len(username) < 3:
            print("Nazwa użytkownika jest zbyt krótka!")
            self.wm.tk_register_view(info="Nazwa użytkownika jest zbyt krótka!")
            return
        if len(password) < 3:
            print("Hasło jest zbyt krótkie!")
            self.wm.tk_register_view(info="Hasło jest zbyt krótkie!")
            return
        if password != password2:
            print("Hasła nie pasują do siebie!")
            self.wm.tk_register_view(info="Hasła do siebie nie pasują!")
            return
        users = self.db.get_collection("users")
        user = users.find_one({"username": username})
        if user:
            print("użytkownik już istnieje w bazie!")
            self.wm.tk_register_view(info="Nazwa użytkownika już istnieje!")
            return;

        random_key = pyotp.random_base32()
        qr_string = pyotp.totp.TOTP(random_key).provisioning_uri(username, issuer_name="Smart Home Remote Control")
        qrcode.make(qr_string).save("static/qr/qr_code_" + username + ".png")

        self.wm.tk_register_code_view(username=username, password=password, key=random_key)

    def try_register_code(self, username, password, key, code):
        code = code.get()
        if self.db is None:
            print("Nie udało się połączyć z bazą danych")
            self.wm.tk_register_code_view(username=username, password=password, key=key)
            return
        users = self.db.get_collection("users")

        if pyotp.TOTP(key).now() != code:
            print("Błędny kod")
            self.wm.tk_register_code_view(username=username, password=password, key=key, info="Błędny kod!")
            return

        passwd_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        qr_img = open("static/qr/qr_code_" + username + ".png", 'rb').read()
        new_user = {"username": username,
                    "password": passwd_hash,
                    "otp_key": key,
                    "img": Binary(qr_img)}
        users.insert_one(new_user)

        self.wm.tk_login_view(info="Zarejestrowano pomyślnie! Zaloguj się!")

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

    def switch_device(self, device_id, room_id, button):
        topic = 'cmd/' + self.smart_objects[room_id]['id'] + '/' + self.smart_objects[room_id]['devices'][device_id][
            'id']
        current_status = self.smart_objects[room_id]['devices'][device_id]['settings']['status']
        if current_status == 'OFF':
            self.smart_objects[room_id]['devices'][device_id]['settings']['status'] = 'ON'
            message = 'on'
        else:
            self.smart_objects[room_id]['devices'][device_id]['settings']['status'] = 'OFF'
            message = 'off'
        self.mqtt_manager.mqtt_send_message(topic, message)
        self.update_button_from_current_state(button, self.smart_objects[room_id]['devices'][device_id]['settings']['status'])

    def device_change_power(self, device_id, room_id, new_power):
        new_power = int(new_power)
        current_power = self.smart_objects[room_id]['devices'][device_id]['settings']['power']
        if new_power == current_power:
            return
        else:
            self.smart_objects[room_id]['devices'][device_id]['settings']['power'] = new_power
            topic = 'cmd/' + self.smart_objects[room_id]['id'] + '/' + \
                    self.smart_objects[room_id]['devices'][device_id]['id']
            message = new_power
            self.mqtt_manager.mqtt_send_message(topic, message)

    def device_change_prop(self, device_id, room_id, new_prop):
        device_props = self.smart_objects[room_id]['devices'][device_id]['settings']['props']
        prop_id = None
        for i in range(len(device_props)):
            if device_props[i] == new_prop:
                prop_id = i
                break
        if prop_id is None:
            print("Błąd właściwości urządzenia")
            return

        self.smart_objects[room_id]['devices'][device_id]['settings']['prop'] = prop_id
        topic = 'cmd/' + self.smart_objects[room_id]['id'] + '/' + \
                self.smart_objects[room_id]['devices'][device_id]['id']
        message = 'p' + format(i)
        self.mqtt_manager.mqtt_send_message(topic, message)



    def update_button_from_current_state(self, button, new_label):
        button.config(text=new_label)

    def check_view_update_on_msg(self, topic, message):
        if topic+"|"+message == self.mqtt_manager.last_sent_command:
            return
        topic = str(topic)
        message = str(message)
        parts = topic.split("/")
        received_room_name = parts[1]
        received_device_name = parts[2]
        received_room_id = None
        received_device_id = None
        for room_id in range(len(self.smart_objects)):
            if self.smart_objects[room_id]['id'] == received_room_name:
                received_room_id = room_id
                break
        if received_room_id == None:
            return
        for device_num in range(len(self.smart_objects[received_room_id]['devices'])):
            if self.smart_objects[received_room_id]['devices'][device_num]['id'] == received_device_name:
                received_device_id = device_num
                break
        settings = self.smart_objects[received_room_id]['devices'][received_device_id]['settings']

        update = False
        if message == 'on':
            if settings['status'] != 'ON':
                settings['status'] = 'ON'
                update = True
        elif message == 'off':
            if settings['status'] != 'OFF':
                settings['status'] = 'OFF'
                update = True

        elif message.isnumeric():
            if settings['power'] != int(message):
                settings['power'] = int(message)
                update = False

        elif message[0] == 'p' and message[1:].isnumeric():
            settings['prop'] = int(message[1:])
            update = True

        if self.wm.current_room == received_room_id and update:
            self.wm.tk_room_view(self.wm.current_room)

if __name__ == '__main__':
    main = Main()
