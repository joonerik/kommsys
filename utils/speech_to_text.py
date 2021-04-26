
#UFERDIG









import wave
import speech_recognition as sr
import logging
from threading import Thread
import paho.mqtt.client as mqtt
from playsound import playsound
import pyaudio
import numpy as np
import json

# MQTT settings
broker = "mqtt.item.ntnu.no"
port = 1883
topic = 'team13'

# Audio settings
channels = 1
sample_format = pyaudio.paInt16
fs = 44100
p = pyaudio.PyAudio()
chunk = 248

# Audio messages
message_dict = {}

# MQTT setup
def setup_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker, port)
    client.subscribe(topic)
    thread = Thread(target=client.loop_forever)
    thread.start()

# Log config
logging.basicConfig(format='%(asctime)s %(message)s',
                    filename='speech_to_text_log.txt',
                    filemode='w',
                    level=logging.DEBUG)

# Message handler
r = sr.Recognizer()
def on_message(client, userdata, msg):
    try:
        data_in = json.loads(msg.payload)

        audiochunks = data_in["audio"]

        for i in range(10):
            
    except ValueError:
        pass  

def log_audio_as_text(audiochunks):
    # wf = wave.open("audio_block", 'wb')
    # wf.setnchannels(channels)
    # wf.setsampwidth(pyaudio.get_sample_size(sample_format))
    # wf.setframerate(fs)
    # wf.writeframes(msg.payload)
    # wf.close()
    # playsound("audio_block")


    # message = sr.AudioFile(msg)

    # with message as source:
    #     audio = r.record(source)

    # interpretation = r.recognize_google(audio)
    # logging.info('{}: {}'.format(client, interpretation))


setup_mqtt()
