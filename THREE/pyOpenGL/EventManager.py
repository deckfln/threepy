"""

"""
import time


class Event:
    def __init__(self, parameters):
        for key in parameters.keys():
            value = parameters[key]
            self.__setattr__(key, value)

    def preventDefault(self):
        return True

    def stopPropagation(self):
        return True


class EventManager:
    def __init__(self, events=None):
        self.callbacks = {}

        if events:
            for event in events:
                self.callbacks[event] = []

    def addEventListener(self, event, funct, compatibility=False):
        if event not in self.callbacks:
            self.callbacks[event] = []

        self.callbacks[event].append(funct)

    def removeEventListener(self, event, funct, compatibility=False):
        callbacks = self.callbacks[event]

        found = -1
        for i in range(len(callbacks)):
            if callbacks[i] == funct:
                found = i
                break

        if found >= 0:
            del self.callbacks[event][found]

    def removeAllEventListeners(self):
        self.callbacks.clear()

    def dispatchEvent(self, event=None, params=None):
        type = event['type']

        if type == 'animationRequest':
            callbacks = self.callbacks[type]
            for callback in callbacks:
                callback(params)

        elif type in self.callbacks:
            callbacks = self.callbacks[type]

            if len(callbacks) > 0:
                eventObject = Event(event)
                for callback in callbacks:
                    callback(eventObject, params)

        # print("event %s in %f s" % (event, t1 - t0))
