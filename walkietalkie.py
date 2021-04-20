from stmpy import Machine, Driver

class GUI:
    def __init__(self):
        pass
    
    def send_signal(self):
        self.stm.send('msg_received')

    def print_to_receiving(self): 
        print("transition: idle to receiving, trigger: msg_received")

    def print_to_sending(self): 
        print("transition: idle to sending, trigger: record_button")

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

gui = GUI()

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
    'trigger': 'done; t',
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
gui.send_signal()