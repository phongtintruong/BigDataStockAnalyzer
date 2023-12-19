#!/bin/sh -eu
#set -x
cd "$(cd "$(dirname "$0")"; pwd)"
mkdir -p v2/
jq <list.json -r '.data.[] | "url = https://apipubaws.tcbs.com.vn/stock-insight/v2/stock/bars?ticker=\(.d[0])&type=stock&resolution=1&countBack=3600&to='"$(date +%s)"'\noutput = v2/'"$(date +%Y-%m-%d-%H-%M-%S)"'/\(.d[0]).json"' | tee crawl-v2.list | curl --verbose --rate 100/m --create-dirs --config -
