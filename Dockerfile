FROM joyzoursky/python-chromedriver:3.8-alpine3.10-selenium
MAINTAINER Yanchuan Sim <yc@botmd.io>

ENV CHROME_BINARY_LOCATION=/usr/local/bin/chrome

COPY smooch_logs /code/smooch_logs
COPY setup.py /code/setup.py
COPY README.md /code/README.md

RUN apk add --update coreutils && \
    rm -rf /var/cache/apk/* && \
    pip install boto3 && \
    pip install /code

# location to save downloaded file
ENV OUTPUT_URI=/code/downloaded.json

COPY download_last_3_days.sh /code/download_last_3_days.sh

ENV PATH="/code:${PATH}"

CMD ["download_last_3_days.sh"]
