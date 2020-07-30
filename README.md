# Smooch Logs Downloader

This is a simple module for downloading Smooch logs from their website.
We obtain login credentials for Smooch using a Selenium with a Chromium headless browser.

## Example

```python
with SmoochWebSession() as session:
    if A.apps:
        app_ids = A.apps
    else:
        r = session.get(f'{SMOOCH_BASE_URL}/webapi/apps?limit=999')
        r.raise_for_status()

        app_ids = [d['_id'] for d in r.json()['apps']]
    #end if

    logger.info(f'Found {len(app_ids)} Smooch applications.')

    downloader = SmoochLogsDownloader(session)
    for app_id in app_ids:
        r = session.get(f'{SMOOCH_BASE_URL}/webapi/apps/{app_id}')
        r.raise_for_status()
        logger.info(f'Downloading logs for "{r.json()["name"]}" <{app_id}> from Smooch.')

        for event in downloader.download(app_id, start=A.start, end=A.end):
            A.output.write(json.dumps(event))
            A.output.write('\n')
        #end for
    #end for

    A.output.close()
#end with
```

The [`SmoochWebSession`](smooch_logs/session.py) sets up the Selenium webdriver and required web-based operation to obtain `sessionId` from Smooch.
During development, it can be convenient to specify an existing session ID for the Smooch session by
```python
SmoochWebSession(session_id='xxx', logout=False)
```
The `SmoochWebSession` object automatically checks for session validity and re-logins if necessary.

The [`SmoochLogsDownloader`](smooch_logs/downloader.py) is a convenience class for downloading Smooch logs for a particular application.
