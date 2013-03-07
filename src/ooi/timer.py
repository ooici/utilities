"""
record time taken for code to peform several steps
"""

import time
import logging
from threading import Lock
import math

from logging import log as _log

class Timer(object):
    def __init__(self, name=None, logger=None, milliseconds=True, number_format='%f'):
        if not name and not logger:
            logging.getLogger(__file__).warn('timer created without a name or logger')
            name = 'unspecified'
        self.tlog = logger or logging.getLogger('timing.'+name)
        self.times = [] # list of tuples (msg, time)
        self.complete_step("start")
        self.multiplier = 1000 if milliseconds else 1
        self.lone_number_format = ' '+number_format
        self.label_number_format = ' %s='+number_format

    def complete_step(self, label=None):
        self.times.append((label, time.time()))

    def __str__(self):
        # special case if only have start time (complete_step never called)
        if len(self.times)==1:
            return 'start time: ' + self.times[0][1]

        # otherwise message has format: elapsed TOTAL unit
        message = 'elapsed' + self.lone_number_format%self.multiplier*self._elapsed() + ' s' if self.multiplier==1 else ' ms'
        if len(self.times)==2:
            return message

        # or: elapsed TOTAL unit: num1 num2 ...
        # or: elapsed TOTAL unit: step1=num1 step2=num2 ...
        message += ':'
        for pair_o_tuples in zip(self.times[1:],self.times[:-1]):
            # looping through adjacent pairs: [(labelN,timeN), (labelN+1,timeN+1)]
            delta = self.multiplier*(pair_o_tuples[1][1]-pair_o_tuples[0][1])
            label = pair_o_tuples[1][0]
            if label:
                message += self.label_number_format%(label,delta)
            else:
                message += self.lone_number_format%delta
        return message

    def _elapsed(self):
        first_step = self.times[0]
        last_step = self.times[-1]
        return last_step[1]-first_step[1]

    def log(self, level=logging.DEBUG, min=-1):
        if self.tlog.isEnabledFor(level):
            if self._elapsed()>=min:
                self.tlog.debug(str(self))


class Accumulator(object):
    def __init__(self, format='%2f'):
        self.lock = Lock()
        self.count = { '__total__': 0 }
        self.min = {}
        self.sum = {}
        self.sumsquares = {}
        self.min = {}
        self.max = {}
        self.format = '%d values: ' + format + ' min, ' + format + ' avg, ' + format + ' max, ' + format + ' dev'
    def add(self, timer):
        with self.lock:
            for pair_o_tuples in zip(timer.times[:-1], timer.times[1:], xrange(len(timer.times)-1)):
                label = pair_o_tuples[1][0] or str(pair_o_tuples[2])
                delta = pair_o_tuples[1][1]-pair_o_tuples[0][1]
                self._add(label, delta)
            total = timer.times[-1][1]-timer.times[0][1]
            self._add('__total__', total)

    def _add(self, label, delta):
        if label in self.sum:
            self.count[label]+=1
            self.sum[label] += delta
            self.sumsquares[label] += delta*delta
            self.min[label] = min(delta, self.min[label])
            self.max[label] = max(delta, self.max[label])
        else:
            self.count[label]=1
            self.sumsquares[label] = delta*delta
            self.min[label] = self.max[label] = self.sum[label] = delta

    def get_count(self, step='__total__'): return self.count[step]
    def get_min(self, step='__total__'): return self.min[step]
    def get_max(self, step='__total__'): return self.max[step]

    def get_average(self, step='__total__'):
        return self.sum[step] / self.count[step]

    def get_standard_deviation(self, step='__total__'):
        if self.count[step]<3:
            return 0
        avg = self.get_average(step=step)
        return math.sqrt(self.sumsquares[step]/self.count[step]-avg*avg)

    def __str__(self):
        return self.to_string()

    def to_string(self, step='__total__'):
        count = self.get_count()
        if count==0:
            return 'no values reported'
        else:
            return self.format % ( self.get_count(step), self.get_min(step), self.get_average(step),
                                    self.get_max(step), self.get_standard_deviation(step))