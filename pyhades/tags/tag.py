from .tag_value import TagValue

DATETIME_FORMAT = "%m/%d/%Y, %H:%M:%S.%f"

class Tag:

    def __init__(self, name, unit, data_type, desc="", min_value=None, max_value=None):

        self.name = name
        self.value = TagValue(min_value=min_value, max_value=max_value)
        self.unit = unit
        self.data_type = data_type
        self.description = desc
        self._observers = set()

    def set_value(self, value):

        self.value.update(value)
        self.notify()

    def set_min_value(self, value):

        self.value.set_min_value(value)

    def set_max_value(self, value):

        self.value.set_max_value(value)
    
    def get_value(self):
        
        return self.value.get_value()

    def get_value_attributes(self):

        return {
            "status_code":{
                "name": self.value.get_status_code().name,
                "value": self.value.get_status_code().value[0],
                "description":  self.value.get_status_code().value[1]
            },
            "source_timestamp": self.value.get_source_timestamp().strftime(DATETIME_FORMAT),
            "value": self.value.get_value(),
        }

    def get_min_value(self):

        return self.value.get_min_value()

    def get_max_value(self):

        return self.value.get_max_value()

    def get_data_type(self):
        
        return self.data_type

    def get_unit(self):

        return self.unit

    def get_description(self):

        return self.description

    def get_attributes(self):

        return {
            "value": self.get_value_attributes(),
            "name": self.name,
            "unit": self.get_unit(),
            "data_type": self.get_data_type(),
            "description": self.get_description(),
            "min_value": self.get_min_value(),
            "max_value": self.get_max_value()
        }
    
    def attach(self, observer):

        observer._subject = self
        self._observers.add(observer)

    def detach(self, observer):

        observer._subject = None
        self._observers.discard(observer)

    def notify(self):

        for observer in self._observers:

            observer.update()