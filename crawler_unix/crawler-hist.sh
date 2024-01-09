#!/bin/sh -eu
#set -x
jq <list.json -r '.data.[] | "url = https://s.cafef.vn/Ajax/PageNew/DataHistory/PriceHistory.ashx?Symbol=\(.d[0])&StartDate=&EndDate=&PageIndex=&PageSize=10000\noutput = hist/'"$(date +%Y-%m-%d)"'/\(.d[0]).json"' | tee crawl-hist.list | curl --verbose --rate 60/m --create-dirs --config -

