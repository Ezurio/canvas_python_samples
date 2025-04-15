# Base class for a simple state machine where each state is a method
# and each event is a method that calls the state method.
# The state machine is initialized with a start state and a list of events.
class StateMachine:
    def _call(self, event):
        return lambda *a: getattr(self, self.state)(event, *a)
    def __init__(self):
        self._states = [ i for i in dir(self) if not i.startswith('_') ]
        self.state = self._start
        for ev in self._events:
            setattr(self, ev, self._call(ev))
    def _set(self, state):
        if state in self._states:
            self.state = state
        else:
            raise ValueError("Invalid state")
