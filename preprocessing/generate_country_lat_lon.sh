#!/usr/bin/env bash
set -u

echo '{"cities":'
cat data/demo/demo* | cut -d"|" -f22,25,28 | sed -e "s/|/,/g" | jq -s -R 'split("\n") | map(split(",")) | map(select(length > 0))  | map({(.[0]): {"lat": .[1], "lon": .[2]}}) | .[]' | jq -s 'add'
echo "}"
