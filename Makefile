all: update sync

sync:
	pip-sync requirements.txt

update:
	pip-compile --quiet requirements.in --output-file requirements.txt
	pip-compile --quiet requirements-dev.in --output-file requirements-dev.txt
