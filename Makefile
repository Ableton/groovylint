all: update sync

sync:
	pip-sync requirements-dev.txt requirements.txt

update:
	pip-compile --allow-unsafe --upgrade --quiet requirements.in --output-file requirements.txt
	pip-compile --allow-unsafe --upgrade --quiet requirements-dev.in --output-file requirements-dev.txt
