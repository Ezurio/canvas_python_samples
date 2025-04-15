from state_machine import StateMachine
from machine import Pin

class StateTransition(StateMachine):
    # List of events that the state machine can handle
    _events = ['init', 'button_pressed']
    # Initial state of the state machine
    _start = 'state0'
    # List of states that the state machine can be in
    _states = ['state0', 'state1', 'state2', 'state3']
    
    # State 0: Initial state
    def state0(self, event):
        print("State 0")
        led0.off()
        led1.off()
        # Transition to state 1 on button press
        if event == 'init' or event == 'button_pressed':
            self._set('state1')
    
    # State 1: Next state
    def state1(self, event):
        print("State 1")
        led0.off()
        led1.on()
        # Transition to state 2 on button press
        if event == 'button_pressed':
            self._set('state2')
    
    # State 2: Intermediate state
    def state2(self, event):
        print("State 2")
        led0.on()
        led1.off()
        # Transition to state 3 on button press
        if event == 'button_pressed':
            self._set('state3')
    
    # State 3: Final state
    def state3(self, event):
        print("State 3")
        led0.on()
        led1.on()
        # Transition to state 0 on button press
        if event == 'button_pressed':
            self._set('state0')

# Callback function for button press
def button0_pressed(val):
    state_machine.button_pressed()

# Configure LEDs
led0 = Pin("LED0", Pin.OUT, Pin.PULL_NONE)
led1 = Pin("LED1", Pin.OUT, Pin.PULL_NONE)
led0.off()
led1.off()

# Configure button 0 to transition states using a callback
btn0 = Pin('BUTTON0', Pin.IN, Pin.PULL_NONE)
btn0.configure_event(button0_pressed, Pin.EVENT_FALLING)

# Create an instance of the state machine
state_machine = StateTransition()
# Send the init event to the state machine
state_machine.init()
