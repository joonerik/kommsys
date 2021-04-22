import logging
from threading import Thread
import json
from appJar import gui
from stmpy import Machine, Driver
from walkietalkie import start


class TimerCommandSenderComponent:
    """
    The component to send voice commands.
    """

    def on_message(self, client, userdata, msg):
        pass

    def __init__(self):
        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        self.create_gui()
        start()

    def create_gui(self):
        self.app = gui()

        self.app.setBg('light blue', override=False, tint=False)
        self.app.setFg('#121212', override=False)

        def extract_timer_name(label):
            label = label.lower()
            if 'record' in label: return 'record'
            if 'emergency' in label: return 'emergency'
            if 'change channel' in label: return 'change channel'
            return None

        def extract_duration_seconds(label):
            label = label.lower()
            if 'record' in label: return 60
            if 'emergency' in label: return 60
            if 'change channel' in label: return 15
            return None

        def publish_command(command):
            payload = json.dumps(command)
            self._logger.info(command)
            #self.mqtt_client.publish(MQTT_TOPIC_INPUT, payload=payload, qos=1)

        self.app.startLabelFrame('Starting walkie talkie/ Home screen:')
        def on_button_pressed_start(title):
            self.stm.send('msg_received')
            name = extract_timer_name(title)
            duration = extract_duration_seconds(title)
            command = {"command": "new_command", "name": name, "duration": duration}
            publish_command(command)
        self.app.addButton('Record message', on_button_pressed_start)
        self.app.addButton('Emergency', on_button_pressed_start)
        self.app.addLabelEntry("Type Channel")
        self.app.addButton('Change channel', on_button_pressed_start)
        self.app.stopLabelFrame()



        self.app.startLabelFrame('Releasing buttons:')
        def on_button_pressed_stop(title):
            name = extract_timer_name(title)
            command = {"command": "release_button", "name": name}
            publish_command(command)
        self.app.addButton('Release record', on_button_pressed_stop)
        self.app.addButton('Release emergency', on_button_pressed_stop)
        self.app.stopLabelFrame()

        #TODO: lag et felt med status osv? 
        self.app.startLabelFrame('Text Display:')
        self.app.addLabel('Current Channel: 1', None)
        self.app.addLabel('Current Status: Listening', None)
        self.app.addLabel('Current Volume:', None)
        self.app.addSpinBoxRange("Volume", 1, 100)
        self.app.stopLabelFrame()

        self.app.go()

#ikke endret noe på dette nedenfor, kopiert 
debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = TimerCommandSenderComponent()