r"""
pyhades/core.py

This module implements the core app class and methods for PyHades
"""
import time
import sys
import logging
import concurrent.futures
from datetime import datetime

from peewee import SqliteDatabase, MySQLDatabase, PostgresqlDatabase

from .utils import log_detailed

from ._singleton import Singleton

from .workers import _ContinuosWorker, StateMachineWorker, LoggerWorker

from .managers import StateMachineManager, DBManager

from .dbmodels import SQLITE, POSTGRESQL, MYSQL
# PyHades Status

STARTED = 'Started'
RUNNING = 'Running'
STOPPED = 'Stopped'

DEVELOPMENT_MODE = 'Development'
PRODUCTION_MODE = 'Production'

APP_MODES = [DEVELOPMENT_MODE, PRODUCTION_MODE]


class PyHades(Singleton):
    r"""
    PyHades is a [singleton](https://en.wikipedia.org/wiki/Singleton_pattern) class to develop multi threads web application 
    for general purposes .

    Usage:
    
    ```python
    >>> from pyhades import PyHades
    >>> app = PyHades()
    ```
    """

    def __init__(self):

        self._start_up_datetime = None
        self._status = STARTED
        self._logging_level = logging.INFO
        self._max_threads = 10
        self._log_file = "app.log"
        self._thread_functions = list()
        self._threads = list()
        self.workers = list()
        self._mode = DEVELOPMENT_MODE

        self._machine_manager = StateMachineManager()
        self._db_manager = DBManager()

        self.db = None

    def info(self):
        r"""
        Shows a summary threads on execution
        """
        return f'''
        \nPyHades {self._status}\n
        \n* Threads Running: {self.threads_running()}
        {self.threads_info()}
        \n* State Machines Running: {self.state_machines_running()}
        {self.state_machines_info()}
        '''

    def set_mode(self, mode:str):
        r"""
        Allows to you define "Development" or "Production" mode.

        For Development mode you use Sqlitedatabase by default when you define it.

        For Production mode you can use Sqlite - Postgres - MySQL

        **Parameters**

        * **mode** (str): App mode ('Development' or 'Production')

        **Return** `None`

        ```python
        >>> app = PyHades()
        >>> app.set_mode('Development')
        ```
        """
        if mode.capitalize() in APP_MODES:
            self._mode = mode

    def get_mode(self):
        r"""
        Gets app mode

        **Returns**
        
        * **mode** (str)

        ```python
        >>> app.get_mode()
        'Development'
        ```
        """
        return self._mode

    def threads_running(self):
        r"""
        Gets thread numbers defined in the app

        **Returns:** (int)

        Usage

        ```python
        >>> threads_running = app.threads_running()
        ```
        """
        return len(self._thread_functions)

    def state_machines_running(self):
        r"""
        Gets state machines numbers defined in the app

        **Returns:** (int)

        Usage

        ```python
        >>> state_machines_running = app.state_machines_running()
        ```
        """
        return len(self.workers)

    def threads_info(self):
        r"""
        Gets information of all defined threads

        **Returns:** (str)

        Usage

        ```python
        >>> app.threads_info()
        ```
        """
        result = ''

        for _thread in self._thread_functions:

            result += _thread.__str__()

        return result

    def state_machines_info(self):
        r"""
        Gets information of all defined state machines

        **Returns:** (str)

        Usage

        ```python
        >>> app.state_machines_info()
        ```
        """
        result = ''

        for _state_machine_worker in self.workers:

            result = _state_machine_worker.__str__()
            break

        return result

    def _set_start_up_datetime(self, date_time:datetime=datetime.now()):
        r"""
        Sets start up datetime of the application

        **Parameters**

        * **date_time** (datetime): date_time when the application is start up (default value is datetime.now())

        **Returns:** `None`

        Usage
        ```python
        >>> app._set_start_up_datetime()
        ```
        """
        self._start_up_datetime = date_time

    def get_start_up_datetime(self):
        r"""
        Gets the start up datetime of the application

        **Returns**

        * **date_time** (datetime): Start up datetime of the app

        Usage

        ```python
        >>> start_up = app.get_start_up_datetime()
        ```
        """

        return self._start_up_datetime

    def append_table(self, table):
        """
        Append a database model class definition.
        
        **Parameters:**

        * **table** (BaseModel): A Base Model Inheritance.
        """

        self._db_manager.register_table(table)

    def define_table(self, cls):
        """
        Append a database model class definition
        by a class decoration.
        """

        self.append_table(cls)

        return cls

    def set_log(self, level=logging.INFO, file:str="app.log"):
        r"""
        Sets the log file and level.
        
        **Parameters:**
        
        * **level** (str): `logging.LEVEL` (default: logging.INFO).
        * **file** (str): log filename (default: 'app.log').

        **Returns:** `None`

        Usage:

        ```python
        >>> app.set_log(file="app.log")
        ```
        """

        self._logging_level = level
        
        if file:

            self._log_file = file

    def set_db(self, dbtype=SQLITE, drop_table=True, cascade=False, **kwargs):
        """
        Sets the database, it supports SQLite and Postgres,
        in case of SQLite, the filename must be provided.

        if app mode is "Development" you must use SQLite Databse
        
        **Parameters:**

        * **dbfile** (str): a path to database file.
        * *drop_table** (bool): If you want to drop table.
        * **cascade** (bool): if there are some table dependency, drop it as well
        * **kwargs**: Same attributes to a postgres connection.

        **Returns:** `None`

        Usage:

        ```python
        >>> app.set_db(dbfile="app.db")
        ```
        """

        from .dbmodels import proxy

        if self.get_mode() == DEVELOPMENT_MODE:

            dbfile = kwargs.get("dbfile", ":memory:")

            self._db = SqliteDatabase(dbfile, pragmas={
                'journal_mode': 'wal',
                'journal_size_limit': 1024,
                'cache_size': -1024 * 64,  # 64MB
                'foreign_keys': 1,
                'ignore_check_constraints': 0,
                'synchronous': 0}
            )

        elif dbtype == SQLITE:

            dbfile = kwargs.get("dbfile", ":memory:")
            
            self._db = SqliteDatabase(dbfile, pragmas={
                'journal_mode': 'wal',
                'journal_size_limit': 1024,
                'cache_size': -1024 * 64,  # 64MB
                'foreign_keys': 1,
                'ignore_check_constraints': 0,
                'synchronous': 0}
            )

        elif dbtype == MYSQL:
            
            db_name = kwargs['name']
            del kwargs['name']
            self._db = MySQLDatabase(db_name, **kwargs)

        elif dbtype == POSTGRESQL:
            
            db_name = kwargs['name']
            del kwargs['name']
            self._db = PostgresqlDatabase(db_name, **kwargs)
        
        proxy.initialize(self._db)
        self._db_manager.set_db(self._db)
        self._db_manager.set_dropped(drop_table, cascade)

    def set_dbtags(self, tags, period=0.5, delay=1.0):
        """
        Sets the database tags for logging.

        If you want to log any tag defined in CVTengine, you must define it here
        
        **Parameters:**

        * **tags** (list): A list of the tags.

        **Returns:** `None`

        Usage:

        ```python
        >>> tags = ["P1", "P2", "T1"]
        >>> app.set_dbtags(tags, period=1.0)
        ```
        """

        self._db_manager.set_period(period)
        self._db_manager.set_delay(delay)

        for _tag in tags:
            self._db_manager.add_tag(_tag, period)

    def get_dbtags(self):
        """
        Returns the database tags for logging.
        """

        return self._db_manager.get_tags()

    def set_max_threads(self, max_threads:int):
        r"""
        Sets maximum numbers of threads

        **Parameters**

        * **max_threads** (int): Max numbers of threads

        **Returns** `None`

        Usage

        ```python
        >>> app.set_max_threads(20)
        ```
        """
        self._max_threads = max_threads

    def _append_machine(self, machine, interval=1, mode="sync"):
        """
        Append a state machine to the state machine manager.
        
        **Parameters:**

        * **machine** (`PyHadesStateMachine`): a state machine object.
        * **interval** (int): Interval execution time in seconds.
        """
        machine.set_interval(interval)
        self._machine_manager.append_machine(machine, interval=interval, mode=mode)

    def get_machine(self, name):
        """
        Returns a PyHades State Machine defined by its name.
        
        **Parameters:**
        
        * **name** (str): a pyhades state machine name.

        Usage

        ```python
        >>> state_machine = app.get_machine('state_machine_name')
        ```
        """

        return self._machine_manager.get_machine(name)

    def get_machines(self):
        """
        Returns all defined PyHades state machines.

        **Returns** (list)

        Usage

        ```python
        >>> state_machines = app.get_machines()
        ```
        """

        return self._machine_manager.get_machines()

    def get_state_machine_manager(self):
        r"""
        Gets state machine Manager

        **Returns:** StateMachineManager instance

        ```python
        >>> app.get_state_machine_manager()
        ```
        """
        return self._machine_manager

    def define_machine(self, name="", interval=1, mode="sync", **kwargs):
        """
        Append a state machine to the state machine manager
        by decoration.
        
        **Parameters:**
        
        * **name** (str): State machine name
        * **interval** (int): Interval execution time in seconds.
        * **mode** (str): Syncronic or Asyncronic thread mode - allowed values ['sync', 'async'] 

        **Returns** Class (cls)

        Usage

        ```python
        >>> from pyhades import PyHades, PyHadesStateMachine
        >>> app = PyHades()
        >>> @app.define_machine(name='state_machine_name', interval=1, mode='async')
            class StateMachine(PyHadesStateMachine):
                ...
        ```
        """
        def decorator(cls):

            machine = cls(name, **kwargs)
            
            self._append_machine(machine, interval=interval, mode=mode)

            return cls

        return decorator

    def thread(self, function=None, **kwargs):
        r"""
        Decorator method to register functions plugins.
        
        This method will register into the PyHades application
        a new function to be executed by the Thread Pool Executor

        **Parameters:**

        * **period** (float): Value of the default loop execution time.
        
        **Returns:** `None`

        Usage:
    
        ```python
        @app.thread(period=0.5)
        def hello():
            print("Hello!!!")

        @app.thread
        def hello_world():
            print("Hello World!!!")
        ```
        """
        if function:
            return _ContinuosWorker(function)
        else:

            def wrapper(function):
                return _ContinuosWorker(function, **kwargs)

            return wrapper

    def _start_logger(self):
        r"""
        Starts logger in log file
        """
        log_format = "%(asctime)s:%(levelname)s:%(message)s"

        level = self._logging_level
        log_file = self._log_file

        if not log_file:
            logging.basicConfig(level=level, format=log_format)
            return
        
        logging.basicConfig(filename=log_file, level=level, format=log_format)

    def _start_threads(self):
        r"""
        Starts execution of the threads define by the decorator @app.thread
        """

        _max = self._max_threads
        self._scheduler = concurrent.futures.ThreadPoolExecutor(max_workers=_max)

        for _f in self._thread_functions:

            try:
                logging.info(f"Thread {_f._name} started")
                self._threads.append(self._scheduler.submit(_f))
            except Exception as e:
                message = "Error on continous functions worker start-up"
                log_detailed(e, message)

    def _stop_threads(self):
        r"""
        Safe stop execution of the defined threads
        """

        for worker in self._thread_functions:
            try:
                worker.stop()
            except Exception as e:
                message = "Error on wokers stop"
                log_detailed(e, message)

    def _start_workers(self):
        r"""
        Starts defined workers like State Machines.
        """
        db_worker = LoggerWorker(self._db_manager)
        state_manager = self.get_state_machine_manager()

        db_worker.init_database()

        if state_manager.exist_machines():

            state_worker = StateMachineWorker(self._machine_manager)
            self.workers.append(state_worker)

        self.workers.append(db_worker)

        try:

            for worker in self.workers:
                worker.daemon = True
                worker.start()

        except Exception as e:
            message = "Error on wokers start-up"
            log_detailed(e, message)

    def _stop_workers(self):
        r"""
        Safe stop workers execution like State Machines
        """
        for worker in self.workers:
            try:
                worker.stop()
            except Exception as e:
                message = "Error on wokers stop"
                log_detailed(e, message)

    def safe_start(self):
        r"""
        Run the app without a main thread, only run the app with the threads and state machines define
        """
        _start_up_datetime = datetime.now()
        self._set_start_up_datetime(_start_up_datetime)

        self._start_logger()
        self._start_workers()
        self._start_threads()

        logging.info("Hades started")  
        self._status = RUNNING
        logging.info(self.info()) 

    def safe_stop(self):
        r"""
        Stops the app in safe way with the threads
        """
        self._stop_threads()
        self._stop_workers()
        logging.info("Manual Shutting down")
        self._status = STOPPED
        sys.exit()

    def run(self):
        r"""
        Runs main app thread and all defined threads by decorators and State Machines besides this method starts app logger

        **Returns:** `None`

        Usage

        ```python
        >>> app.run()
        ```
        """
        self.safe_start()
        
        try: 
            
            while True:

                time.sleep(1)

        except (KeyboardInterrupt, SystemExit):
            
            self.safe_stop()
            