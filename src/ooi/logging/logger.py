"""
THIS CLASS IS NOT A LOGGER, but it plays one on TV.

    The purpose of this class is to make it easy for other code to get a scoped-logger with just an import statement.
    And while I was at it, I added a TRACE log level (below DEBUG).


USAGE:

    If you want to do some logging...

    put this at the top of your file:
        from ooi.logging import log

    then log out:
        log.info("PI is an irrational number")
        log.debug("after the 3 i found a point 14")
        log.trace("what the heck is trace for?")


WARNING: DO NOT stray from the path.  Some evil trickery is going on here and you could get hurt!

    DO NOT import as something else:
        from ooi.logging import log as foo_bar

    DO NOT use the fully qualified name:
        import ooi.logging

    DO NOT use the internal classes directly
        from ooi.logging.logger import _ScopedLogger
        cant_stop_me = _ScopedLogger()

    DO NOT pass "log" around for other things to use:
        from ooi.logging import log
        import other.module
        other.module.write_some_messages(log)

    Yes, this is hacky.  I would rather just stick with plain python logging.  But if this is the only way to quit the
    imported monkey patch habit, then give me hacky.


EVOLUTION / CREATION:

    In the early days of the project, it seems like this was just too much work:
        import logging
        log = logging.getLogger('python.module.name')

    To save those extra bytes, we monkey-patched import itself to save a few characters with this replacement:
        from pyon.util.log import log

    Unfortunately, this makes troubleshooting import problems much more difficult.  And solving a mundane problem by
    monkey-patching import kind of makes me taste my lunch a little bit, even well into the afternoon.

    If I've done this correctly, nobody should notice anything different.  But I'll sleep better with one less monkey
    running loose.
"""


import logging
import inspect
import threading

# invent a new log level called "trace".  hope that people will use it.
# lifted from http://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility
#
TRACE=5
logging.TRACE = TRACE
logging.addLevelName(TRACE, 'TRACE')
def trace(self, message, *args, **kws):
    self._log(TRACE, message, args, **kws) # resist the urge to stick your * in my args
logging.Logger.trace = trace


# here the magic happens
#
# the _ScopedLogger object has the same functions as a logger,
# but as soon as one of them is called:
#   - it figures out what module is the caller
#   - creates a logger for that module
#   - installs the logger as "module.log"
#   - invokes whatever the original function was on that new logger
#
# this should happen exactly once in each module.  after that, the installed logger would be called:
#     # say i'm inside x.y.py
#     from ooi.logging import log  # x.y.log is a _ScopedLogger()
#     log.info('first message')    # sets x.y.log = logging.getLogger('x.y') [and then runs .info() on it]
#     log.info('second message')   # this isn't a _ScopedLogger any more, its logging.getLogger('x.y'), remember?
#
class _ScopedLogger(object):

    _filters = []

    def _add_filter(self, filter):
        """ set this filter on each new logger created (does not affect loggers already created)
            not intended to be called directly by client code (interface is supposed to look like a Logger).
            instead, call ooi.logging.config.add_filter(filter)
        """
        self._filters.add(filter)

    def _install_logger(self):
        stack = inspect.stack()
        # stack[0]: call to inspect.stack() on the line above
        # stack[1]: call to _install_logger() by one of the delegate methods below
        frame=stack[2] # call to the delegate method from some outside calling module
        module = inspect.getmodule(frame[0])
        module.log = logging.getLogger(module.__name__)
        for filter in self._filters:
            module.log.addFilter(filter)
        #        setattr(module.log, 'trace', lambda *args: module.log.log(5, *args))
        return module.log

    # all Logger methods quietly install the true logger object and then delegate
    def setLevel(self,*a,**b):          return self._install_logger().setLevel(*a,**b)
    def isEnabledFor(self,*a,**b):      return self._install_logger().isEnabledFor(*a,**b)
    def getEffectiveLevel(self,*a,**b): return self._install_logger().getEffectiveLevel(*a,**b)
    def getChild(self,*a,**b):          return self._install_logger().getChild(*a,**b)
    def trace(self,*a,**b):             return self._install_logger().debug(*a,**b)
    def debug(self,*a,**b):             return self._install_logger().debug(*a,**b)
    def info(self,*a,**b):              return self._install_logger().info(*a,**b)
    def warning(self,*a,**b):           return self._install_logger().warning(*a,**b)
    def error(self,*a,**b):             return self._install_logger().error(*a,**b)
    def critical(self,*a,**b):          return self._install_logger().critical(*a,**b)
    def log(self,*a,**b):               return self._install_logger().log(*a,**b)
    def exception(self,*a,**b):         return self._install_logger().exception(*a,**b)
    def addFilter(self,*a,**b):         return self._install_logger().addFilter(*a,**b)
    def removeFilter(self,*a,**b):      return self._install_logger().removeFilter(*a,**b)
    def filter(self,*a,**b):            return self._install_logger().filter(*a,**b)
    def addHandler(self,*a,**b):        return self._install_logger().addHandler(*a,**b)
    def removeHandler(self,*a,**b):     return self._install_logger().removeHandler(*a,**b)
    def findCaller(self,*a,**b):        return self._install_logger().findCaller(*a,**b)
    def handle(self,*a,**b):            return self._install_logger().handle(*a,**b)
    def makeRecord(self,*a,**b):        return self._install_logger().makeRecord(*a,**b)


class AddFields(logging.Filter):
    """ add custom fields to messages for graypy to forward to graylog
        if the values are constant, can may be added as a dictionary when the filter is created.
        if they change, the values can be copied form thread-local fields with the given names.
        NOTE: graypy will automatically also add: function, pid, process_name, thread_name
    """
    def __init__(self, thread_local_field_names, constant_field_values):
        """
        @param thread_local_field_names is a dictionary mapping the name of the thread-local field
                                        to the name it should have in the logging record.  for example,
                                     if the dictionary has an entry 'a': 'b', then the logging record
                                        will be set:  record.b = threading.local().a

        @param constant_field_values is a dictionary mapping logging field names to string values.
                                     if this dictionary has an entry 'a': 'b', then: record.b = 'a'
        """
        self.thread_local_field_names = thread_local_field_names
        self.constant_field_values = constant_field_values

    def filter(self, record):
        # add values from thread local context
        values = threading.local()
        for local_field_name, logging_field_name in self.thread_local_field_names.iteritems():
            if hasattr(values,local_field_name):
                record.setattr(record,logging_field_name,getattr(values,local_field_name))

        # add values constant for the container
        for key,value in self.constant_field_values.iteritems():
            setattr(record,key,value)