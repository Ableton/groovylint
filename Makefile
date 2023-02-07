all: update sync

sync:
	pip-sync requirements-dev.txt

update:
	pip-compile --resolver=backtracking --strip-extras --allow-unsafe --upgrade requirements-dev.in --output-file requirements-dev.txt
