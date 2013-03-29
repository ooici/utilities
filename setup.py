from distutils.core import setup

setup(name='utilities',
    version='2013.03.28',
    author='Jonathan Newbrough',
    author_email='jonathan.newbrough@gyregroup.com',
    url='https://github.com/newbrough/utilities',
    package_dir = {'': 'src'},
    packages=['ooi', 'ooi.logging'],
    install_requires = [ 'pyyaml==3.10', 'graypy' ]
)

