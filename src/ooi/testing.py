"""
testing utilities
"""

import unittest
import os
import os.path

class ImportTest(unittest.TestCase):
    """
    unit test that attempts to import every python file beneath the base directory given.
    fail if any can not be imported
    """
    def __init__(self, source_directory, base_package,*a,**b):
        """
        @param source_directory: should be something in the PYTHONPATH
        @param base_package: top-level package to start recursive search in (or list of them)
        @param a, b: pass-through from unittest.main() to TestCase.__init__()
        """
        super(ImportTest,self).__init__(*a,**b)
        self.source_directory = source_directory
        self.base_package = base_package

    def test_can_import(self):
        failures = []

        packages = self.base_package if isinstance(self.base_package,list) else [ self.base_package ]
        for pkg in packages:
            pkg_dir = pkg.replace('.','/')
            self._import_below(pkg_dir, pkg, failures)
        if failures:
            self.fail(msg='failed to import these modules:\n' + '\n'.join(failures))

    def _import_below(self, dir, mod, failures):
        subdir = os.path.join(self.source_directory, dir)
        for entry in os.listdir(subdir):
            path = os.path.join(subdir, entry)
            # each python script (except init), try to import
            if os.path.isfile(path) and entry.endswith('.py') and entry!='__init__.py':
                try:
                    submod = mod + '.' + entry[:-3]
                    __import__(submod)
                except Exception,e:
                    failures.append(submod + '\t' + str(e))
            # each new subpackage import and recurse
            elif os.path.isdir(path) and os.path.isfile(os.path.join(path,'__init__.py')) and entry!='test':
                submod = mod + '.' + entry
                try:
                    __import__(submod)
                except Exception,e:
                    failures.append(submod + '\t' + str(e))
                    continue
                self._import_below(os.path.join(dir,entry), submod, failures)
