import io
import json


class DevicesManager:
    """
    Class used to manage devices and rooms collection
    """
    def __init__(self, rc_main):
        self.main = rc_main
        self.smart_objects = None
        self.parse_smart_objects_config()

    def parse_smart_objects_config(self):
        """
        Reads configuration from file config.json
        In case of failure, stops the program
        """
        with io.open("config.json", encoding="utf-8") as config_data:
            try:
                config_text = config_data.read()
                self.smart_objects = json.loads(config_text)
            except:
                print("Parsowanie konfiguracji z pliku JSON nie powiodło się.")
                exit()

    def switch_device(self, device_id, room_id, button=None):
        """
        Switches device (on/off) status. Require number of room and number of device.
        Button parameter allows to quickly change label.
        """
        if not self.smart_objects[room_id] or not self.smart_objects[room_id]['devices'][device_id]:
            print("Niepoprawny identyfikator urządzenia do przełączenia!")
            return

        topic = 'cmd/' + self.smart_objects[room_id]['id'] + '/' + self.smart_objects[room_id]['devices'][device_id][
            'id']
        current_status = self.smart_objects[room_id]['devices'][device_id]['settings']['status']
        if current_status == 'OFF':
            self.smart_objects[room_id]['devices'][device_id]['settings']['status'] = 'ON'
            message = 'on'
        else:
            self.smart_objects[room_id]['devices'][device_id]['settings']['status'] = 'OFF'
            message = 'off'
        self.main.mqttm.mqtt_send_message(topic, message)
        if button:
            button.config(text=self.smart_objects[room_id]['devices'][device_id]['settings']['status'])

    def device_change_power(self, device_id, room_id, new_power):
        """
        Changes device power (from a slider). Require number of room and number of device.
        """
        if not self.smart_objects[room_id] or not self.smart_objects[room_id]['devices'][device_id]:
            print("Niepoprawny identyfikator urządzenia do zmiany mocy!")
            return

        new_power = int(new_power)
        if not 'power' in self.smart_objects[room_id]['devices'][device_id]['settings']:
            self.smart_objects[room_id]['devices'][device_id]['settings']['power'] = 0
        current_power = self.smart_objects[room_id]['devices'][device_id]['settings']['power']
        if new_power == current_power:
            return
        else:
            self.smart_objects[room_id]['devices'][device_id]['settings']['power'] = new_power
            topic = 'cmd/' + self.smart_objects[room_id]['id'] + '/' + \
                    self.smart_objects[room_id]['devices'][device_id]['id']
            message = new_power
            self.main.mqttm.mqtt_send_message(topic, message)

    def device_change_prop(self, device_id, room_id, new_prop):
        """
        Changes device property. Require number of room and number of device.
        """
        if not self.smart_objects[room_id] or not self.smart_objects[room_id]['devices'][device_id] \
                or not self.smart_objects[room_id]['devices'][device_id]['settings']:
            print("Niepoprawny identyfikator urządzenia do zmiany właściwości!")
            return

        device_props = self.smart_objects[room_id]['devices'][device_id]['settings']['props']
        if device_props is None:
            return
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
        message = 'p' + format(prop_id)
        self.main.mqttm.mqtt_send_message(topic, message)

    def check_view_update_on_msg(self, topic, message):
        """
        Checks if current view require update after receiving message from other source e.g. another remote control.
        If change could be visible for user it refreshes view. Slider adjustable device power is not refreshed due
        to large number of messages while change - to see power change (on a slider) it is required to manually
        refresh view.
        """
        if topic + "|" + message == self.main.mqttm.last_sent_command:
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
        if received_room_id is None or received_room_id != self.main.wm.current_room:
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

        if update:
            self.main.wm.tk_room_view(self.main.wm.current_room)
