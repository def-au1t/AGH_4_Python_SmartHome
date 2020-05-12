import threading
import paho.mqtt.client as mqtt


class MqttManager(object):

    def __init__(self, rc):
        self.mqtt_client = mqtt.Client()
        self.main = rc
        self.last_sent_command = None

        self.mqtt_client.on_connect = self.mqtt_on_connect
        self.mqtt_client.on_message = self.mqtt_on_message
        try:
            self.mqtt_client.connect("localhost", 1883, 60)
        except:
            print("Cannot connect to MQTT Broker")
            exit()
        self.subscribe_all_devices()
        thread = threading.Thread(target=self.mqtt_client.loop_forever, args=())
        thread.daemon = True
        thread.start()

    def mqtt_on_message(self, client, userdata, message):
        print("Odebrano: ", message.topic, " - ", str(message.payload.decode("utf-8")))
        self.main.check_view_update_on_msg(message.topic, str(message.payload.decode("utf-8")))

    def mqtt_on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))


    def mqtt_send_message(self, topic="cmd/kitchen/light1", message="on"):
        message = format(message)
        if self.mqtt_client is None:
            print("MQTT client not connected!")
            return
        print("Sending: "+ topic + "|->" + message)
        self.last_sent_command = topic + "|" + message
        self.mqtt_client.publish(topic, message)

    def subscribe_all_devices(self):
        for room_id in range(len(self.main.smart_objects)):
            tmp = self.main.smart_objects[room_id]['devices']
            for device_num in range(len(self.main.smart_objects[room_id]['devices'])):
                topic = 'cmd/' + self.main.smart_objects[room_id]['id'] + '/' + \
                        self.main.smart_objects[room_id]['devices'][device_num]['id']
                print("Subscribing: ",topic)
                self.mqtt_client.subscribe(topic)