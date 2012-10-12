from distutils.core import setup

setup(name='utilities',
    version='2012.10.12',
    author='Jonathan Newbrough',
    author_email='jonathan.newbrough@gyregroup.com',
    url='https://github.com/newbrough/utilities',
    package_dir = {'': 'src'},
    packages=['ooi', 'ooi.logging'],
    install_requires = [ 'pyyaml==3.10', 'graypy' ]
)

