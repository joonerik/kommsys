import wave
import speech_recognition as sr
import logging
from threading import Thread
import paho.mqtt.client as mqtt

broker = "mqtt.item.ntnu.no"
port = 1883
topic = '#'

logging.basicConfig(format='%(asctime)s %(message)s',
                    filename='/home/petter/Dropbox/fag/programmering/log.txt',
                    filemode='w',
                    level=logging.DEBUG)

r = sr.Recognizer()

def on_message(client, userdata, msg):
    # TODO Check if a .wav file was received

    message = sr.AudioFile(msg)

    with message as source:
        audio = r.record(source)

    interpretation = r.recognize_google(audio)
    logging.info('{}: {}'.format(client, interpretation))

client = mqtt.Client()
client.on_message = on_message
client.connect(broker, port)
client.subscribe(topic)
thread = Thread(target=client.loop_forever)
thread.start()
