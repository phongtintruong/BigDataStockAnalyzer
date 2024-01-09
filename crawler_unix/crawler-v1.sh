#!/bin/sh -eu
#set -x
cd "$(cd "$(dirname "$0")"; pwd)"
mkdir -p v1/
jq <list.json -r '.data.[] | "url = https://apipubaws.tcbs.com.vn/stock-insight/v1/intraday/\(.d[0])/pv-ins\noutput = v1/'"$(date +%Y-%m-%d-%H-%M-%S)"'/\(.d[0]).json"' | tee crawl-v1.list | curl --verbose --rate 100/m --create-dirs --config -
