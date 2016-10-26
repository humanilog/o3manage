from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='o3manage',
    version='0.1dev1',
    description='Manage Library and Tools for Odoo in Shared Environments',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Systems Administration',
        'Operating System :: POSIX'
    ],
    keywords='odoo management tool shared instances'
    url='https://github.com/humanilog/o3manage',
    author='Stefan Becker',
    author_email='ich@funbaker.de',
    license='GPLv3',
    entry_points={
        'console_scripts': ['o3crinstance=o3manage.cmd:o3crinstance']
    },
    packages=['o3manage']
    install_requires=[
        'docopt',
        'plumbum'
    ],
    include_package_data=True,
    zip_safe=False,)