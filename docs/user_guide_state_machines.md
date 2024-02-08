# PyIACStateMachine

You can create your own State Machine Classes by inherit from PyIACStateMachine.

In addition, you must decorate your class with the *define_machine* decorator in your PyIAC app. This decorator need the following
parameters:

- name (str): State Machine name.
- interval (float or int): State machine interval for the thread loop.
- mode (str): Concurrent mode (sync or async)

```python
from PyIAC import PyIAC, PyIACStateMachine, State

app = PyIAC()

@app.define_machine(name='State Machine Name', interval=1.0, mode="async")
class StateMachineClass(PyIACStateMachine):
    ...
```

Then, you must define the states of your state machine in the class context using the State class from PyIAC.

```python
@app.define_machine(name='State Machine Name', interval=1.0, mode="async")
class StateMachineClass(PyIACStateMachine):
    # states
    state_1 = State('State1', initial=True)
    state_2 = State('State2')
    ...
```

The *State* class need the state name as a string as a first argument, and the initial argument as optional if the state is the initial state.

Another topic that you make sure is to define the transitions.

For that, you use the *.to* method that has the state object

```python
@app.define_machine(name='State Machine Name', interval=1.0, mode="async")
class StateMachineClass(PyIACStateMachine):
    ...
    # transition
    transition_1 = state_1.to(state_2)
    transition_2 = state_2.to(state_1)
    ...
```

You must define your class __init__ method with the following minimum content:

```python
@app.define_machine(name='State Machine Name', interval=1.0, mode="async")
class StateMachineClass(PyIACStateMachine):
    ...
    def __init__(self, name):

        super().__init__(name)

    ...
```

The next step is to define the methods for states and transitions. 

The action that you want to be executed when the state machine is in some specific state must be defined in a method that begins with the word *while_* followed by the previously defined state object.

```python
@app.define_machine(name='State Machine Name', interval=1.0, mode="async")
class StateMachineClass(PyIACStateMachine):
    ...
    def while_state_1(self):

        ...

    ...
```

Whereas whatever you want to be executed when the state machine is at the time of the transition, you must define the method by prepending the word *on_* followed by the previously defined transition object.

```python
@app.define_machine(name='State Machine Name', interval=1.0, mode="async")
class StateMachineClass(PyIACStateMachine):
    ...
    def on_transition_1(self):

        ...

    ...
```

Below is a more concrete example applied to the scenario of a traffic light.

## Traffic Lights

```python
from PyIAC import PyIAC, PyIACStateMachine, State

app = PyIAC()

@app.define_machine(name='TrafficLight', interval=1.0, mode="async")
class TrafficLightMachine(PyIACStateMachine):

    # states
    green  = State('Green', initial=True)
    yellow  = State('Yellow')
    red  = State('Red')

    # transitions
    slowdown = green.to(yellow)
    stop = yellow.to(red)
    go = red.to(green)

    # parameters
    time_left = 30

    def __init__(self, name):

        super().__init__(name)

    def on_slowdown(self):

        self.time_left = 3

    def on_stop(self):

        self.time_left = 20

    def on_go(self):

        self.time_left = 30

    def while_green(self):

        print(self)
        if self.time_left == 0:

            self.slowdown()

        self.time_left -= 1

    def while_yellow(self):

        print(self)
        if self.time_left == 0:

            self.stop()

        self.time_left -= 1

    def while_red(self):

        print(self)
        if self.time_left == 0:

            self.go()
        
        self.time_left -= 1

    def __str__(self):

        return f"{self.name}: {self.get_state()} - {self.time_left} second left."

if __name__=='__main__':

    app.run()
```