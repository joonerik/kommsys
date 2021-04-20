from stmpy import Machine, Driver
import logging
from threading import Thread
import json
from appJar import gui


class simple_gui:

    def __init__(self):
        self.create_gui()
        #self.print_start_machine()


    def create_gui(self):
        self.app = gui()


        self.app.setBg('light blue', override=False, tint=False)
        self.app.setFg('#121212', override=False)

        self.app.startLabelFrame('Home screen:')
        self.app.addButton('Press Record message', self.extract_button_name)
        self.app.addButton('Press Emergency', self.extract_button_name)
        self.app.addLabelEntry("Type Channel", None)
        self.app.addButton('Press Change channel', self.extract_button_name)
        self.app.stopLabelFrame()

        self.app.startLabelFrame('Releasing buttons:')
        self.app.addButton('Release record', self.extract_action)
        self.app.addButton('Release emergency', self.extract_action)
        self.app.stopLabelFrame()

        self.app.startLabelFrame('Display:')
        self.app.addLabel('Current Channel: 1', None)
        self.app.addLabel('Current Status: Listening', None)
        self.app.addLabel('Current Volume:', None)
        self.app.addSpinBoxRange("Volume", 1, 100)
        self.app.stopLabelFrame()

        self.app.go()


    #determine actions from which buttton is pressed in a tidy way.
    def extract_button_name(self,label):
        label = label.lower()
        if 'record' in label: return 'record'
        if 'emergency' in label: return 'emergency'
        if 'channel' in label: return 'channel'
        return None

    #check if button is pressed or released.
    def extract_action(self,label):
        label = label.lower()
        if 'Release' in label: return "button released"
        if 'Press' in label: return "button pressed"
        return None

    def connect_to_stm(self,title, action):
        name = extract_button_name(title)
        act = extract_action(action)
        #command = {"command": "new_event", "name": name, "duration": act}

    def print_start_machine(self):
        print('start machine')

    def print_to_recieving(self):
        print('to recieving')

    def print_to_sending(self):
        print('to sending')

    def print_to_sending_emg_msg(self):
        print("to sending SOS")

    def print_to_receiving_emg_msg(self):
        print("recieving SOS")

    def print_back_to_idle(self):
        print("back to idle state")

    def print_do(self):
        print("do")


gui = simple_gui()

# start
t0 = {'source': 'initial',
    'target': 'idle',
    'effect': 'print_start_machine'}

# idle to receiving by receiving message
t1 = {
    'source': 'idle',
    'target': 'receiving',
    'trigger': 'msg_received',
    'effect': 'print_to_receiving'}

# idle to sending by button
t2 = {
    'source': 'idle',
    'trigger': 'record_button',
    'target': 'sending',
    'effect': 'print_to_sending'}

# idle to sending_emg_msg by button
t3 = {
    'source': 'idle',
    # remember that this trigger represents a function which handles
    # the two buttons pressed simultanously
    'trigger': 'emg_mes_button',
    'target': 'sending_emg_msg',
    'effect': 'print_to_sending_emg_msg'}

# idle to receiving_emg_msg by trigger by trigger emg_msg_received
t4 = {
    'source': 'idle',
    'trigger': 'emg_mes_received',
    'target': 'receiving_emg_msg',
    'effect': 'print_to_receiving_emg_msg'}

# receiving_emg_msg to idle by trigger done
t5 = {
    'source': 'receiving_emg_msg',
    'trigger': 'done',
    'target': 'idle',
    'effect': 'print_back_to_idle'}

# receiving to receiving_emg_msg by trigger emg_msg_received
t6 = {
    'source': 'receiving',
    'trigger': 'emg_msg_received',
    'target': 'receiving_emg_msg',
    'effect': 'print_to_receiving_emg_msg'}

# sending to receiving_emg_msg by trigger emg_msg_received
t7 = {
    'source': 'sending',
    'trigger': 'emg_msg_received',
    'target': 'receiving_emg_msg',
    'effect': 'print_to_receiving_emg_msg'}

# sending to idle by trigger done or timer
t8 = {
    'source': 'sending',
    # possible two separate transitions as there are two triggers
    'trigger': 'done',
    'target': 'idle',
    'effect': 'print_back_to_idle'}

# receiving to idle by trigger done
t9 = {
    'source': 'receiving',
    'trigger': 'done',
    'target': 'idle',
    'effect': 'print_back_to_idle'}

# receiving to sending_emg_msg by trigger emg_mes_button
t10 = {
    'source': 'receiving',
    'trigger': 'emg_mes_button',
    'target': 'sending_emg_msg',
    'effect': 'print_to_sending_emg_msg'}

# sending_emg_msg to idle by trigger done or timer
t11 = {
    'source': 'sending_emg_msg',
    # possible two separate transitions as there are two triggers
    'trigger': 'done; t',
    'target': 'idle',
    'effect': 'print_back_to_idle'}


idle = {'name': 'idle',
        # TODO: internal transition
        }

sending = {'name': 'sending',
            'entry': 'start_timer("t", 30000)',
            # do: publish()
            'do': 'print_do'}

receiving = {'name': 'receiving',
            # do: play()
            'do': 'print_do'}

receiving_emg_msg = {'name': 'receiving_emg_msg',
                    # do: play() - possible other function
                    'do': 'print_do'}

sending_emg_msg = {'name': 'sending_emg_msg',
                    'entry': 'start_timer("t", 30000)',
                    #'do': 'publish()'
                    'do': 'print_do'}


machine = Machine(name='gui', 
                transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11], 
                states=[idle, sending, receiving, receiving_emg_msg, sending_emg_msg],
                obj=gui) 
gui.stm = machine

driver = Driver()
driver.add_machine(machine)
driver.start()

# gui (buttons or some sort) to send correct signals (triggers)
