#!/bin/sh

python -m smooch_logs.downloader --start `date --utc --iso-8601 --date="3 days ago"` --end `date --utc --iso-8601 --date="1 day"` -o $OUTPUT_URI
