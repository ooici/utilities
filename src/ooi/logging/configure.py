""" manage logging configuration

    USAGE:

    ### perform once as the application begins to initialize logging system-wide
    from ooi.logging import config
    config.add_configuration("some/path/logging.yml")           # could be normal file
    config.add_configuration("or/resource/logging.local.yml")   # or resource within egg
    # define special fields for GELF records
    config.set_logging_fields( {"username":"user", "conversation-id":"session"}, {"system":"alpha"} )

    ### now throughout codebase, can write log records
    from ooi.logging import log
    log.info("up and running now")

    ### but can also go back and change configuration later
    def oh_please_make_it_stop():
        config.set_level("pyon.net.endpoint", logging.ERROR)
        config.set_level("pyon.ion.endpoint", logging.ERROR)
"""

import logging.config
import errno
import yaml
import collections
from pkg_resources import resource_string
import ooi.logging
import logger
import time

class _LoggingConfiguration(object):

    debug = False
    current_config = {}

    def set_debug(self, value=True):
        """print all calls to public methods"""
        self.debug = value

    def add_configuration(self, configuration):
        if self.debug:
            print 'DEBUG LOGGING: add_configuration: %r\nStack trace:' % configuration
            self._print_caller()

        if not configuration:
            return # no config = no-op
        if isinstance(configuration, dict):
            self.current_config['disable_existing_loggers'] = False
            self._add_dictionary(self.current_config, configuration)
            logging.config.dictConfig(self.current_config)
            if self.debug:
                print 'DEBUG LOGGING: configuration: %r' % self.current_config
        elif isinstance(configuration, str):
            # is a configuration file or resource -- try both
            contents = self._read_file(configuration) or self._read_resource(configuration)
            if not contents:
                raise IOError('failed to locate logging configuration file: ' + configuration)
            parsed = yaml.load(contents)
            self.add_configuration(parsed)
        elif isinstance(configuration, list) or isinstance(configuration, tuple):
            for item in configuration:
                self.add_configuration(item)
        else:
            raise Exception("ERROR: unable to configure logging from a %s: %s" % (configuration.__class__.__name__, repr(configuration)))

    def replace_configuration(self, configuration):
        self.current_config.clear()
        self.add_configuration(configuration)

    def set_level(self, scope, level):
        if self.debug:
            print 'DEBUG LOGGING: set_level: %s: %s\nStack trace:' % (scope,level)
            self._print_caller()
        config = { 'loggers': { scope: {'level':level }}}
        self.add_configuration(config)

    def set_all_levels(self, level):
        if self.debug:
            print 'DEBUG LOGGING: set_all_levels: %s\nStack trace:' % level
            self._print_caller()
        changes = {}
        for scope in self.current_config['loggers'].keys():
            changes[changes] = {'level':level}
        self.add_configuration(changes)

    def get_configuration(self):
        return self.current_config

    def _read_file(self, filename):
        try:
            with open(filename, 'r') as infile:
                return infile.read()
        except IOError, e:
            if e.errno != errno.ENOENT:
                print 'ERROR: error reading logging configuration file ' + repr(filename) + ': ' + str(e)
        return None

    def _read_resource(self, resource_name):
        try:
            return resource_string('', resource_name)
        except IOError, e:
            if e.errno != errno.ENOENT:
                print 'ERROR: error reading logging configuration resource ' + repr(resource_name) + ': ' + str(e)
        return None

    def _add_dictionary(self, current, added):
        """ from pyon.core.common, except allow recursion (logging config isn't too deep) """
        for key in added:
            if key in current and isinstance(current[key], collections.Mapping):
                self._add_dictionary(current[key], added[key])
            else:
                current[key] = added[key]

    def add_filter(self, filter):
        """ add a filter to all new loggers created """
        ooi.logging.log._add_filter(filter)

    def set_logging_fields(self, thread_local_fields, constant_fields):
        """WARNING: calling multiple times is currently additive -- will not replace fields"""
        filter = logger.AddFields(thread_local_fields, constant_fields)
        self.add_filter(filter)

    def _print_caller(self):
        """ display stack when enabled """
        try:
            import traceback
            print '\n'.join(['%s:%d %s'%(f,l,c) for f,l,m,c in traceback.extract_stack()])
        except:
            print 'failed to get stack information'