""" logging utilities

    USAGE:

    Most users should get everything they need from right here:
        from ooi.logging import log, config, CRITICAL,FATAL,ERROR,WARNING,WARN,INFO,DEBUG,TRACE

    Within logging.yml files, classes in format and handler packages may also be used.

    The replay package is a stand-alone utility used with the RawRecordFormat.  See package documentation.

    In particular, use log and config imported from here: do not directly use the logger or configure packages.
    They were written to be used as singletons from the ooi.logging context.
    Incorrect usage has been associated with higher rates of dementia, seepage and loss of fur in laboratory animals.
"""
from configure import _LoggingConfiguration
from logging import CRITICAL,FATAL,ERROR,WARNING,WARN,INFO,DEBUG
from logger import TRACE, _ScopedLogger

log = _ScopedLogger()
config = _LoggingConfiguration()
