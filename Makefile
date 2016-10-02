.PHONY: all clean

all:
	armsglobe/cities_lat_lon.json

armsglobe/city_to_country.json:
	python preprocessing/cities_to_countries_from_airportdata.py

armsglobe/cities_lat_lon.json:
	./preprocessing/generate_country_lat_lon.sh | jq -c '.' > armsglobe/cities_lat_lon.json
