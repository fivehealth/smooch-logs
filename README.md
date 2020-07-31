# Smooch Logs Downloader

[![PyPI version](https://img.shields.io/pypi/v/smooch_logs.svg)](https://pypi.python.org/pypi/smooch_logs/)
[![PyPI license](https://img.shields.io/pypi/l/smooch_logs.svg)](https://pypi.python.org/pypi/smooch_logs/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/smooch_logs.svg)](https://pypi.python.org/pypi/smooch_logs/)
[![PyPI status](https://img.shields.io/pypi/status/smooch_logs.svg)](https://pypi.python.org/pypi/smooch_logs/)
[![PyPI download total](https://img.shields.io/pypi/dm/smooch_logs.svg)](https://pypi.python.org/pypi/smooch_logs/)

This is a simple module for downloading Smooch logs from their website.
We obtain login credentials for Smooch using a Selenium with a Chromium headless browser.

## Installation

```bash
pipenv install smooch_logs
```

## Usage

### CLI

You use the `smooch_logs.downloader` script to directly download Smooch logs from thr CLI.

```bash
$ python -m smooch_logs.downloader --help                                                                                                <aws:botmd>

usage: downloader.py [-h] [-A app_id [app_id ...]] [--start date] [--end date] -o uri

Download Smooch logs for given application ID.

optional arguments:
  -h, --help            show this help message and exit
  -A app_id [app_id ...], --apps app_id [app_id ...]
                        Smooch App IDs to download logs for. Defaults to all apps.
  --start date          Dump logs after this date/time (ISO date time format; default = all logs available which is ~30 days)
  --end date            Dump logs before this date/time (ISO date time format; default = now).
  -o uri, --output uri  Dump logs to this URI.
```

For example, to download logs for all apps in the last 3 days,

```bash
python -m smooch_logs.downloader --start `date --utc --iso-8601 --date="3 days ago"` -o last_3_days.json
```

### Module

```python
import logging

from smooch_logs import SmoochWebSession
from smooch_logs import SmoochLogsDownloader
from smooch_logs import SMOOCH_BASE_URL

logger = logging.getLogger(__name__)

with SmoochWebSession() as session:
    r = session.get(f'{SMOOCH_BASE_URL}/webapi/apps?limit=999')
    r.raise_for_status()

    app_ids = [d['_id'] for d in r.json()['apps']]

    logger.info(f'Found {len(app_ids)} Smooch applications.')

    downloader = SmoochLogsDownloader(session)
    for app_id in app_ids:
        r = session.get(f'{SMOOCH_BASE_URL}/webapi/apps/{app_id}')
        r.raise_for_status()
        logger.info(f'Downloading logs for "{r.json()["name"]}" <{app_id}> from Smooch.')

        for event in downloader.download(app_id, start=A.start, end=A.end):
            print(json.dumps(event))
        #end for
    #end for
#end with
```

The [`SmoochWebSession`](smooch_logs/session.py) sets up the Selenium webdriver and required web-based operation to obtain `sessionId` from Smooch.
During development, it can be convenient to specify an existing session ID for the Smooch session by
```python
SmoochWebSession(session_id='xxx', logout=False)
```
The [`SmoochWebSession`](smooch_logs/session.py) object automatically checks for session validity and re-logins if necessary.

The [`SmoochLogsDownloader`](smooch_logs/downloader.py) is a convenience class for downloading Smooch logs for a particular application.


## Docker

The [Dockerfile](Dockerfile) included in this repository contains the necessary to run the Python download script.
It currently comes with a [shell script to download the last 3 days of logs](download_last_3_days.sh) for all Smooch applications and save them to the URI specified in environment variable `OUTPUT_URI`.
This is currently used by the authors in a daily job to download logs.
Feel free to modify as necessary for your use case.
