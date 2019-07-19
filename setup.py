from setuptools import setup
setup(
    name = 'pymex',
    version = '1.0.1',
    packages = ['pymex'],
    entry_points = {
        'console_scripts': [
            'pymex = pymex.__main__:main'
        ]
    })