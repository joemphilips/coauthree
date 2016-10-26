#!/usr/bin/env bash
set -eu

readonly VERSION="1.0"
readonly SCRIPT_DIR_PATH=$(dirname $(readlink -f $0))
cd $SCRIPT_DIR_PATH
cd ..

(head -n 1 result.csv && tail -n +2 result.csv | sort -t, -u -k1,1) > result2.csv

csvjson -k university result2.csv > result2.json

cat result2.json | jq '.[]' | jq '{(.university): {lon: .long, lat}}' > result3.json
