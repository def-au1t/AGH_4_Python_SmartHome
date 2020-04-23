import threading
import paho.mqtt.client as mqtt



def mqtt_on_message(mqtt_client, userdata, msg):
    print(msg.payload.decode())
    print(userdata)


def mqtt_on_connect(mqtt_client, client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("cmd/")
    thread = threading.Thread(target=mqtt_client.loop_forever, args=())
    thread.daemon = True
    thread.start()


def mqtt_send_message(mqtt_client, topic="cmd/kitchen/light1", message="on"):
    if mqtt_client is None:
        print("MQTT client not connected!")
        return
    mqtt_client.publish(topic, message)
