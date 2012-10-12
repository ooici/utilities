"""
record time taken for code to peform several steps
"""

import time
import logging

class Timer(object):
    def __init__(self, name, milliseconds=True):
        self.log = logging.getLogger('timing.'+name)
        self.times = [] # list of tuples (msg, time)
        self.next_step("")
        self.multiplier = 1000 if milliseconds else 1

    def next_step(self, label=None):
        self.times.append((label, time.time()))

    def last_step(self, label=None):
        self.next_step(label)
        self._log()

    def _log(self):
        if self.log.isEnabledFor(logging.DEBUG):
            first_step = self.times[0]
            last_step = self.times[-1]
            elapsed = last_step[1]-first_step[1]
            message = 'elapsed %f:' % (self.multiplier*elapsed)

            previous_step = first_step
            for this_step in self.times[1:]:
                message += ' '
                if this_step[0]:
                    message += this_step[0]+'='
                delta = self.multiplier*(this_step[1]-previous_step[1])
                message += '%f' % delta
                previous_step = this_step
            self.log.debug(message)