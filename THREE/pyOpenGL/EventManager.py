"""

"""
import sys
import time
import traceback


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
        self.animationRequest = None

        if events:
            for event in events:
                self.callbacks[event] = []

    def addEventListener(self, event, funct, compatibility=False):
        if event not in self.callbacks:
            self.callbacks[event] = []

        self.callbacks[event].append(funct)

        if event == 'animationRequest':
            self.animationRequest = funct

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

    def animate(self, params):
        self.animationRequest(params)

    def dispatchEvent(self, event, params=None):
        try:
            if isinstance(event, Event):
                type = event.type
                eventObject = event
            else:
                type = event['type']
                eventObject = Event(event)

            if type in self.callbacks:
                callbacks = self.callbacks[type][:]  # get a copy of the list

                if len(callbacks) > 0:
                    for c in callbacks:
                        c(eventObject, params)
        except:
            traceback.print_exc(file=sys.stdout)
            raise RuntimeError("render")

        # print("event %s in %f s" % (event, t1 - t0))
