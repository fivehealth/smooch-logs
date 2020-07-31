__all__ = ['SmoochLogsDownloader']

from argparse import ArgumentParser
from datetime import datetime
import json
import logging
import os

from pytz import UTC

from uriutils import URIFileType

from .session import SmoochWebSession
from .session import SMOOCH_BASE_URL

logger = logging.getLogger(__name__)


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
        least_recent_event, most_recent_event = None, None
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

                if least_recent_event is None or least_recent_event['timestamp'] < event['timestamp']:
                    least_recent_event = event
                if most_recent_event is None or most_recent_event['timestamp'] > event['timestamp']:
                    most_recent_event = event
                count += 1

                if count % 10000 == 0:
                    logger.debug(f'Downloaded {count} entries for <{app_id}> since {datetime.utcfromtimestamp(least_recent_event["timestamp"]).isoformat()}.')
                #end if
            #end for

            end_date_timestamp = response['events'][-1]['timestamp']
        #end while

        if count:
            logger.info(f'Downloaded {count} entries for <{app_id}> ({datetime.utcfromtimestamp(least_recent_event["timestamp"]).isoformat()} to {datetime.utcfromtimestamp(most_recent_event["timestamp"]).isoformat()}).')
        else:
            logger.info(f'There are no log entries available to download for <{app_id}>.')
        #end if
    #end def
#end class


def main():
    parser = ArgumentParser(description='Download Smooch logs for given application ID.')
    parser.add_argument('-A', '--apps', type=str, nargs='+', required=False, metavar='app_id', help='Smooch App IDs to download logs for. Defaults to all apps.')
    parser.add_argument('--start', type=datetime.fromisoformat, default=None, metavar='date', help='Dump logs after this date (ISO date time format; default = all logs available which is ~30 days)')
    parser.add_argument('--end', type=datetime.fromisoformat, default=None, metavar='date', help='Dump logs before this date (ISO date time format; default = now).')
    parser.add_argument('-o', '--output', type=URIFileType('w'), metavar='uri', required=True, help='Dump logs to this URI.')
    A = parser.parse_args()

    logging.basicConfig(format='%(asctime)-15s [%(name)s-%(process)d] %(levelname)s: %(message)s', level=os.environ.get('LOG_LEVEL', 'INFO'))

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
