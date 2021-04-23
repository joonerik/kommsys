import stmpy
from appJar import gui
import time
import fileinput
from state_machines.record_logic import Recorder
from state_machines.playback_logic import Player

class GUI:

    def create_driver(self):
        recorder = Recorder()
        playback = Player()

        self.driver = stmpy.Driver()
        self.driver.add_machine(recorder.create_machine('recorder_stm'))
        self.driver.add_machine(playback.create_machine('playback_stm'))
        self.driver.start()

    def print_to_receiving(self):
        print("transition: idle to receiving, trigger: msg_received")

    def print_to_sending(self): 
        print("transition: idle to sending, trigger: start in recorder_stm")

    def recording(self):
        self.print_to_sending()
        self.driver.send('start', 'recorder_stm')

    def stop_recording(self):
        self.driver.send('stop', 'recorder_stm')

    def play_msg_signal(self):
        self.driver.send('start', 'playback_stm')

    def change_channel(self, channel):

        newChannel = open("audio_files/channel.txt", "w")
        newChannel.write(channel)

        self.driver.send('change_channel_signal', 'playback_stm')
    
    def A(self):
        print("internal transition")

    def receive_emg_msg(self):
        print("'A emg msg was received!'")
        self.driver.send('emg_msg', 'recorder_stm')
        self.app.setImage("show", "img/rsos.png")
        self.app.setImageMap("show", self.click, self.coords)
        # self.stm.driver.send('emg_msg', 'playback_stm')

    def finish_emg_msg(self):
        print("'The emg msg is done playing!'")
        self.driver.send('emg_msg', 'recorder_stm')
        self.app.setImage('show', "img/idle2.png")
        self.app.setImageMap("show", self.click, self.coords)
        # self.stm.driver.send('emg_msg', 'playback_stm')
    
    def print_back_to_idle(self):
        print("back to idle state")

    def print_to_receiving_emg_msg(self):
        print("going to receiving_emg_msg state")
        
    def print_to_sending_emg_msg(self):
        print("going to sending_emg_msg state")
    
    def print_start_machine(self):
        print("start machine")

    def print_do(self):
        print("this is a do")

    def print_timer(self):
        print("timer expired, going to idle state")

    def __init__(self):
        self.app = gui()
        self.a = ""
        self.channelEdit = False
        self.coords = {
            "Record": [76, 404, 188, 483],
            "SOS": [79, 496, 178, 533],
            "channel": [54, 155, 104, 191],
            "volume": [126, 170, 226, 292],
            "1": [83,565,138,594],
            "2": [158, 565, 224, 594],
            "3": [241, 565, 301, 594],
            "4": [83, 609, 138, 637],
            "5": [158, 609, 224, 637],
            "6": [241, 609, 301, 637],
            "7": [83, 652, 138, 684],
            "8": [158, 652, 224, 684],
            "9": [241, 652, 301, 684],
            "0": [158, 702, 224, 726],
            "+": [83, 702, 138, 726],
            "done": [241, 702, 301, 726]
        }
        self.app.addImage("show", "img/idle.png", 0, 0)
        self.app.setImageMap("show", self.click, self.coords)

        self.app.addLabel("l1", "<click on the device>")
        self.app.addLabel("channel", "" + str(50) + "")

        self.driver = stmpy.Driver()
        self.driver.start(keep_active=True)
        self.create_driver()

    def click(self,area):
        self.app.setLabel("l1", area)
        if area == "SOS":
            self.driver.send('emg_msg', 'recorder_stm')
            self.app.setImage("show", "img/ssos.png")
            self.app.setImageMap("show", self.click, self.coords)
            print("sending emergency message")
        if area == "Record":
            self.recording()
            #self.stm.driver.send('start', 'recorder_stm')
            self.app.setImage("show", "img/recording.png")
            self.app.setImageMap("show", self.click, self.coords)
            print("sending message")
        if area == "channel":
            # self.app.setImage("show", "/Users/cecilie/Desktop/ntnu/Frame 2.png")
            self.app.setImageMap("show", self.click, self.coords)
            print("channel changed")
        if area == None:
            self.app.setImage('show', "img/idle2.png")
            self.app.setImageMap("show", self.click, self.coords)
        """for k in ["0","1","2","3","4","5","6","7","8","9"]:
            if area == k:
                self.a = area
                self.app.setLabel("channelnow", "Channel: " + self.a)
                self.change_channel()
                break"""
        if area == "+":
            self.channelEdit = True
        k = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        if self.channelEdit:
            if area in k:
                self.a += area
            if area == "done":
                self.channelEdit = False
                self.app.setLabel("channelnow", "Current channel: " + self.a)
                self.change_channel(self.a)
                # self.change_channel()
                self.a = ""



    def create_gui(self):

        self.app.setFont(14)


        #self.app.startLabelFrame('Starting walkie talkie/ Home screen:')
        #self.app.addButton('Record message', self.recording)
        #self.app.addButton('Emergency', None)
        # self.app.stopLabelFrame()

        self.app.startLabelFrame('Releasing buttons:', 0,1)
        self.app.addButton('Play message', self.play_msg_signal)
        self.app.addLabelEntry("Channel", None)
        self.app.addButton('Change channel', self.change_channel)
        self.app.addButton('Release record', self.stop_recording)
        self.app.addButton('Release emergency', None)
        self.app.addButton('Emergency msg received', self.receive_emg_msg)
        self.app.addButton('Emergency msg finished', self.finish_emg_msg)
        self.app.stopLabelFrame()

        self.app.startLabelFrame('Display:',0,2)
        self.app.addLabel("channelnow", "Current channel: " + "1")
        #self.app.addLabel('Current Status: Listening', None)
        #self.app.addLabel('Current Volume: 15', None)
        self.app.stopLabelFrame()

        self.app.go()

gui_wt = GUI()
gui_wt.create_gui()
