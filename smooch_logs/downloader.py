__all__ = ['SmoochLogsDownloader']

from argparse import ArgumentParser
from datetime import datetime
import json
import logging

from dateutil.parser import isoparse

from pytz import UTC

from uriutils import URIFileType

from .session import SmoochWebSession

logger = logging.getLogger(__name__)

SMOOCH_BASE_URL = 'https://app.smooch.io'


class SmoochLogsDownloader():
    def __init__(self, session):
        self._session = session
    #end def

    def download(self, app_id, start=None, end=None):
        session = self._session

        end_datetime = end if end else datetime.utcnow()
        start_datetime = start if start else datetime(1970, 1, 1)
        start_datetime = UTC.localize(start_datetime) if start_datetime.tzinfo is None else start_datetime.astimezone(UTC)
        end_datetime = UTC.localize(end_datetime) if end_datetime.tzinfo is None else end_datetime.astimezone(UTC)
        logger.info(f'Start downloading Smooch logs for appId <{app_id}> from {start_datetime.isoformat()} to {end_datetime.isoformat()}...')

        start_date_timestamp, end_date_timestamp = datetime.timestamp(start_datetime), datetime.timestamp(end_datetime)

        done, count = False, 0
        while not done:
            r = session.get(f'{SMOOCH_BASE_URL}/webapi/apps/{app_id}/logs', params=dict(before=end_date_timestamp))
            r.raise_for_status()

            response = r.json()

            if not response['hasMore']:
                break

            for event in response['events']:
                if event['timestamp'] < start_date_timestamp:
                    done = True
                    break
                #end if

                yield event
                count += 1

                if count % 10000 == 0:
                    logger.debug(f'Downloaded {count} entries for <{app_id}> since {datetime.fromtimestamp(event["timestamp"]).isoformat()}.')
            #end for

            end_date_timestamp = response['events'][-1]['timestamp']
        #end while

        if count:
            logger.info(f'Downloaded {count} entries for <{app_id}> since {datetime.fromtimestamp(event["timestamp"]).isoformat()}.')
        else:
            logger.info(f'There are no log entries available to download for <{app_id}>.')
        #end if
    #end def
#end class


def main():
    parser = ArgumentParser(description='Download Smooch logs for given application ID.')
    parser.add_argument('-A', '--apps', type=str, nargs='+', required=False, help='Smooch App IDs to download logs for. Defaults to all apps.')
    parser.add_argument('--start', type=isoparse, default=None, help='Dump logs after this date (ISO date time format; default = all logs available which is ~30 days)')
    parser.add_argument('--end', type=isoparse, default=None, help='Dump logs before this date (ISO date time format; default = now).')
    parser.add_argument('-o', '--output', type=URIFileType('w'), required=True, help='Dump logs to this URI.')
    A = parser.parse_args()

    logging.basicConfig(format='%(asctime)-15s [%(name)s-%(process)d] %(levelname)s: %(message)s', level=logging.DEBUG)

    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.INFO)
    logging.getLogger('WDM').setLevel(logging.WARNING)

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
#end def


if __name__ == '__main__':
    main()
