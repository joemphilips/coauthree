
armsglobe/cities_lat_lon.json:
	./preprocessing/generate_country_lat_lon.sh | jq -c '.' > armsglobe/cities_lat_lon.json
