from setuptools import setup, find_packages

setup(
    name='assistant',
    version='0.0.1',
    description='Assist with running jobs and send messages.',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['assistant=assistant.assistant:main']
    }
)