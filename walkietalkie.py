import stmpy

class WalkieTalkie:
    def __init__(self):
        pass

    def print(self): 
        print("this is a function triggered from a transition effect")

    def print_state(self):
        print("this is a function triggered from the state")

    def create_machine(self):
        walkietalkie = WalkieTalkie()
        # start
        t0 = {'source': 'initial',
              'target': 'idle',
              'effect': ''}
        # idle to receiving by receiving message
        t1 = {
            'source': 'idle',
            'target': 'receiving',
            'trigger': 'msg_received',
            'effect': 'print'}
        # idle to sending by button
        t2 = {
            'source': 'idle',
            'trigger': 'record_button',
            'target': 'sending',
            'effect': 'print'}
        # idle to sending_emg_msg by button
        t3 = {
            'source': 'idle',
            # remember that this trigger represents a function which handles
            # the two buttons pressed simultanously
            'trigger': 'emg_mes_button',
            'target': 'sending_emg_msg',
            'effect': 'print'}
        # idle to receiving_emg_msg by trigger by trigger emg_msg_received
        t4 = {
            'source': 'idle',
            'trigger': 'emg_mes_received',
            'target': 'receiving_emg_msg',
            'effect': 'print'}
        # receiving_emg_msg to idle by trigger done
        t5 = {
            'source': 'receiving_emg_msg',
            'trigger': 'done',
            'target': 'idle',
            'effect': 'print'}
        # receiving to receiving_emg_msg by trigger emg_msg_received
        t6 = {
            'source': 'receiving',
            'trigger': 'emg_msg_received',
            'target': 'receiving_emg_msg',
            'effect': 'print'}
        # sending to receiving_emg_msg by trigger emg_msg_received
        t7 = {
            'source': 'sending',
            'trigger': 'emg_msg_received',
            'target': 'receiving_emg_msg',
            'effect': 'print'}
        # sending to idle by trigger done or timer
        t8 = {
            'source': 'sending',
            # possible two separate transitions as there are two triggers
            'trigger': 'done; t',
            'target': 'idle',
            'effect': 'print'}
        # receiving to idle by trigger done
        t9 = {
            'source': 'receiving',
            'trigger': 'done',
            'target': 'idle',
            'effect': 'print'}
        # receiving to sending_emg_msg by trigger emg_mes_button
        t10 = {
            'source': 'receiving',
            'trigger': 'emg_mes_button',
            'target': 'sending_emg_msg',
            'effect': 'print'}
        # sending_emg_msg to idle by trigger done or timer
        t11 = {
            'source': 'sending_emg_msg',
            'trigger': 'done; t',
            'target': 'idle',
            'effect': 'print'}


        idle = {'name': 'idle',
                # TODO: internal transition
                }

        sending = {'name': 'sending',
                  'entry': 'start_timer("t", 30000)',
                  # do: publish()
                  'do': 'print_state()'}

        receiving = {'name': 'receiving',
                    # do: play()
                    'do': 'print_state()'}

        receiving_emg_msg = {'name': 'receiving_emg_msg',
                            # do: play() - possible other function
                            'do': 'print_state()'}

        sending_emg_msg = {'name': 'sending_emg_msg',
                           'entry': 'start_timer("t", 30000)',
                           #'do': 'publish()'
                           'do': 'print_state()'}


        wt_stm = stmpy.Machine(name="wtMachine", 
                                  transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11],
                                  states=[idle, sending, receiving, receiving_emg_msg, sending_emg_msg],
                                  obj=walkietalkie)
        walkietalkie.stm = wt_stm
        return wt_stm