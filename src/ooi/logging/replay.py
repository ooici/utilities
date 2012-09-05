""" read logfiles written by RawRecordFormatter,
    send these to a remote GELF server,
    then (optionally) delete the logfile.

    USAGE:

    One python application will write raw logfiles, then this application will read and forward them to graylog.
    (IE- gumstix can log from container while network is not connected, then forward log records when network is connected.)

    Main application would use logging.yml entries like this:

        formatters:
          raw:
            (): 'ooi.logging.format.RawRecordFormatter'
        handlers:
          file:
            class: logging.handlers.RotatingFileHandler
            formatter: raw
            level: DEBUG
            filename: /path/to/some-file.log
            maxBytes: 1048576
            backupCount: 9

    Now application will write logs.  Backups will be called /path/to/some-file.log.1, .2, etc.

    Later the backups can be sent with this command:

        python ooi/logging/replay.py graylog.oceanobservatories.org /path/to/some-file.log.*

    This is probably not appropriate for sending the non-backup /path/to/some-file.log because it is still being written
    to by the running application.
"""

import graypy
import os
import sys
import logging

class GELFReplayer(object):
    def __init__(self, server, port=12201, delete=True, level=logging.DEBUG):
        self._sender = graypy.GELFHander(server, port)
        self._sender.setLevel(level)
        self._delete_file = delete

    def relay(self, *filenames):
        """ process each of the filenames given by forwarding log record contents to the GELF server.
            handles files in reverse order so rotated logs can be specified by wildcard (file.log.*) 
            but sent oldest first.
        """
        # function needed by the exec below
        handle_record_dict = self._handle

        filenames.reverse() # work oldest to newest
        for filename in filenames:
            with open(filename, 'r') as f:
                contents = f.read()
            exec contents ## DANGER, DANGER!
            if self._delete_file:
                os.remove(filename)

    def _handle(self, dict):
        """ delegate sending record to GELFHandler """
        record = logging.makeLogRecord(dict)
        self._sender.emit(record)
        
if __name__ == '__main__':
    if len(sys.argv)<3:
        print 'USAGE: python ' + __file__ + " server logfile..."
        exit(1)
    server = sys.argv[1]
    filenames = sys.argv[2:]
    obj = GELFReplayer(server)
    obj.relay(*filenames)
