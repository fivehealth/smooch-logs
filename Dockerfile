FROM joyzoursky/python-chromedriver:3.8-alpine3.10-selenium
MAINTAINER Yanchuan Sim <yc@botmd.io>

ENV CHROME_BINARY_LOCATION=/usr/local/bin/chrome

COPY smooch_logs /code/smooch_logs
COPY setup.py /code/setup.py
COPY README.md /code/README.md

RUN pip install boto3 && \
    pip install /code

CMD ["python", "-m", "smooch_logs.downloader"]
