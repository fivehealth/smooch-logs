FROM joyzoursky/python-chromedriver:3.8-alpine3.10-selenium
MAINTAINER Yanchuan Sim <yc@botmd.io>

ENV CHROME_BINARY_LOCATION=/usr/local/bin/chrome

RUN apk add --update coreutils && \
    rm -rf /var/cache/apk/* && \
    pip install smooch_logs

# location to save downloaded file
ENV OUTPUT_URI=/code/downloaded.json

COPY download_last_3_days.sh /code/download_last_3_days.sh

CMD ["/code/download_last_3_days.sh"]
