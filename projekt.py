import json
import threading
import tkinter as tk
from tkinter import ttk
from mqtt import *
from tk_views import *
import io
import sqlite3

smart_objects = None
mqtt_client = None
window = None
db = None

def connect_to_db(name):
    global db
    try:
        conn = sqlite3.connect(name)
    except:
        print("Cannot connect to SQLite database")
        # exit()



def connect_to_mqtt(host, port, keepalive):
    global mqtt_client
    mqtt_client = mqtt.Client()
    mqtt_client.mqtt_on_connect = mqtt_on_connect
    mqtt_client.mqtt_on_message = mqtt_on_message
    try:
        mqtt_client.connect(host, port, keepalive)
    except:
        print("Cannot connect to MQTT Broker")
        exit()

def parse_smart_objects_config():
    global smart_objects
    with io.open("config.json", encoding="utf-8") as config_data:
        try:
            config_text = config_data.read()
            smart_objects = json.loads(config_text)
        except:
            print("Cannot parse JSON config.")
            exit()




def show_rc_login():
    global window
    window = tk.Tk()
    window.title("Smart-home remote control")
    label = tk.Label(text="Hello")
    label.pack()
    button1 = tk.Button(text="Kitchen Light On", command=mqtt_send_message)
    button1.pack()



def create_tk_window():
    global window
    window = tk.Tk()
    window.title("Smart Home Remote Control")
    window.configure()
    window.geometry("1000x600")
    window.resizable(False, False)
    tk_start_view(window)


def init():
    parse_smart_objects_config()
    connect_to_mqtt("localhost", 1883, 60)
    connect_to_db("remote_control.db")
    create_tk_window()


def main():
    init();
    mqtt_client.publish("test/topic", "Hello world2!");
    window.mainloop()


if __name__ == '__main__':
    main()
