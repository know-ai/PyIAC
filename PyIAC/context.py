from .core import PyIAC

class PyIACContext(object):
    r"""
    When you need run threads with PyIAC with a web framework, where these frameworks have a main thread, the PyIAC app
    must run with a context to avoid lock the main app with the main thread.
    
    Usage

    ```python
    >>> from flask import Flask
    >>> from PyIAC import PyIAC, PyIACContext, State, PyIACStateMachine

    >>> flask_app = Flask(__name__)
    >>> hades_app = PyIAC()
    >>> @hades_app.define_machine(name='TrafficLight', interval=1.0, mode="async")
        class TrafficLightMachine(PyIACStateMachine):

        # states
        ...

    
    >>> if __name__ == "__main__":

    >>> with PyIACContext(hades_app):
        
            flask_app.run()
    ```
    """

    def __init__(self, app:PyIAC, create_tables:bool=True, alarm_worker:bool=False):

        if isinstance(app, PyIAC):
            
            self.app = app
            self._create_tables = create_tables
            self._create_alarm_worker = alarm_worker

    def __enter__(self):
        self.app.safe_start(create_tables=self._create_tables, alarm_worker=self._create_alarm_worker)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.app.safe_stop()
