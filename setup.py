import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='smooch_logs',
    version='0.1.2',
    packages=['smooch_logs'],
    description='Simple module for downloading Smooch logs from their website.',
    long_description=README,
    long_description_content_type='text/markdown',
    author='5 Health Inc',
    author_email='hello@botmd.io',
    url='https://github.com/fivehealth/smooch-logs',
    license='MIT License',
    install_requires=[
        'selenium',
        'python-dateutil',
        'pytz',
        'webdriver-manager',
        'requests',
        'uriutils',
    ],
    python_requires='>=3.6',
    keywords='selenium smooch',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'Framework :: Flask',
        'License :: OSI Approved :: MIT License',
    ],
)