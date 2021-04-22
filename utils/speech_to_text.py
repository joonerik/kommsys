import wave
import speech_recognition as sr
import logging
from threading import Thread
import paho.mqtt.client as mqtt

# MQTT settings
broker = "mqtt.item.ntnu.no"
port = 1883
topic = 'awesometest'

# Log config
logging.basicConfig(format='%(asctime)s %(message)s',
                    filename='speech_to_text_log.txt',
                    filemode='w',
                    level=logging.DEBUG)

# Message handler
r = sr.Recognizer()
def on_message(client, userdata, msg):
    print

    # message = sr.AudioFile(msg)

    # with message as source:
    #     audio = r.record(source)

    # interpretation = r.recognize_google(audio)
    # logging.info('{}: {}'.format(client, interpretation))

# MQTT setup
client = mqtt.Client()
client.on_message = on_message
client.connect(broker, port)
client.subscribe(topic)
thread = Thread(target=client.loop_forever)
thread.start()
