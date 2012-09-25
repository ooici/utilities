"""
record time taken for code to peform several steps
"""

import time
import logging

class Timer(object):
    def __init__(self, name, milliseconds=True):
        self.log = logging.getLogger('timing.'+name)
        self.times = []
        self.next_step("")
        self.multiplier = 1000 if milliseconds else 1

    def next_step(self, *lbl):
        label = lbl[1] if lbl else None
        self.times.append((label, time.time()))

    def last_step(self, *lbl):
        self.next_step(*lbl)
        self._log()

    def _log(self):
        if self.log.isEnabledFor(logging.DEBUG):
            previous_step = self.times[0][1]
            message = 'elapsed %f:' % self.multiplier*(self.times[:-1][1]-previous_step)
            for tuple in self.times[1:]:
                message += ' '
                if tuple[0]:
                    message += tuple[0]+'='
                this_step = tuple[1]
                delta = self.multiplier*(this_step-previous_step)
                message += '%f' % delta
                previous_step = this_step
            self.log.debug(message)