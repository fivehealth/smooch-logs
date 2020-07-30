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

```python
import logging

from smooch_logs import SmoochWebSession
from smooch_logs import SmoochLogsDownloader

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
