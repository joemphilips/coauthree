.PHONY: all clean categories

all:
	armsglobe/cities_lat_lon.json

categories:
	armsglobe/categories/All_SingleCell.json
	armsglobe/categories/All_iPS.json
	armsglobe/categories/All_Bioconductor.json
	armsglobe/categories/All_ES.json

armsglobe/city_to_country.json:
	python preprocessing/cities_to_countries_from_airportdata.py

armsglobe/categories/All_Bioconductor.json:
	python preprocessing/convert_to_timebins_format.py ./data/demo/demo_Bioconductor.csv

armsglobe/categories/All_iPS.json:
	python preprocessing/convert_to_timebins_format.py ./data/demo/demo_iPS.csv

armsglobe/categories/All_SingleCell.json:
	python preprocessing/convert_to_timebins_format.py ./data/demo/demo_SingleCell.csv

armsglobe/categories/All_ES.json:
	python preprocessing/convert_to_timebins_format.py ./data/demo/demo_ES.csv

armsglobe/cities_lat_lon.json:
	./preprocessing/generate_country_lat_lon.sh | jq -c '.' > armsglobe/cities_lat_lon.json
