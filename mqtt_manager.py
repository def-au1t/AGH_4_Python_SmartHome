import os
import threading
import paho.mqtt.client as mqtt


class MqttManager:
    """
    Class responsible for MQTT broker management.
    """
    def __init__(self, rc):
        """
        Initializes MQTT Broker connection with provided connection parameters.
        Makes all subscriptions based on config, and starts new thread waiting for messages.
        """
        self.mqtt_client = mqtt.Client()
        self.main = rc
        self.last_sent_command = None

        self.mqtt_client.on_connect = self.mqtt_on_connect
        self.mqtt_client.on_message = self.mqtt_on_message
        try:
            self.mqtt_client.connect(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT")), 60)
        except:
            print("Nie można połączyć się z brokerem MQTT")
            exit()
        self.subscribe_all_devices(self.main.dm.smart_objects)
        thread = threading.Thread(target=self.mqtt_client.loop_forever, args=())
        thread.daemon = True
        thread.start()

    def mqtt_on_message(self, client, userdata, message):
        """
        Runs checking if view modification is required after receiving the message
        """
        print("Odebrano: ", message.topic, " - ", str(message.payload.decode("utf-8")))
        self.main.dm.check_view_update_on_msg(message.topic, str(message.payload.decode("utf-8")))

    def mqtt_on_connect(self, client, userdata, flags, rc):
        print("Połączono z brokerem MQTT - kod: " + str(rc))

    def mqtt_send_message(self, topic, message):
        """
        Sends message to MQTT broker
        """
        message = format(message)
        if self.mqtt_client is None:
            print("Klient MQTT nie jest podłączony!")
            return
        print("Wysyłam: " + topic + " |-> " + message)
        self.last_sent_command = topic + "|" + message
        self.mqtt_client.publish(topic, message)

    def subscribe_all_devices(self, objects):
        """
        Subscribes to all devices managed by application from configuration file.
        Requires config parser to be run before. Objects parameter provides all rooms with devices.
        """
        for room_id in range(len(objects)):
            for device_num in range(len(objects[room_id]['devices'])):
                topic = 'cmd/' + objects[room_id]['id'] + '/' + \
                        objects[room_id]['devices'][device_num]['id']
                print("Subskrybuję: ", topic)
                self.mqtt_client.subscribe(topic)
