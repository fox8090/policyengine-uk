all: microdata

install:
	pip install -e .

microdata:
	python openfisca_uk/initial_setup.py

format:
	black . -l 79

test: 
	openfisca test -c openfisca_uk openfisca_uk/tests/policy/baseline
	openfisca test -c openfisca_uk openfisca_uk/tests/policy/reforms/with_postcode_features -r openfisca_uk.config.postcode_lookup.with_postcode_features
	pytest openfisca_uk/tests/code_health
	pytest openfisca_uk/tests/microsimulation
	black . -l 79 --check

serve:
	openfisca serve --country-package openfisca_uk

stats:
	python docs/summary/generate_descriptions.py