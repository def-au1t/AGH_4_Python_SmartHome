import threading
import paho.mqtt.client as mqtt


class MqttManager:

    def __init__(self):
        self.mqtt_client = mqtt.Client()

        self.mqtt_client.on_connect = self.mqtt_on_connect
        self.mqtt_client.on_message = self.mqtt_on_message
        try:
            self.mqtt_client.connect("localhost", 1883, 60)
        except:
            print("Cannot connect to MQTT Broker")
            exit()

    def mqtt_on_message(self, userdata, msg):
        print(msg.payload.decode())
        print(userdata)

    def mqtt_on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("cmd/")
        thread = threading.Thread(target=self.mqtt_client.loop_forever, args=())
        thread.daemon = True
        thread.start()

    def mqtt_send_message(self, topic="cmd/kitchen/light1", message="on"):
        if self.mqtt_client is None:
            print("MQTT client not connected!")
            return
        self.mqtt_client.publish(topic, message)
