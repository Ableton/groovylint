all: update sync

sync:
	pip-sync requirements.txt

update:
	pip-compile --quiet requirements.in --output-file requirements.txt
