install:
	pip install -r requirements.txt

.PHONY: test
test: install
	PYTHONPATH=. py.test -s

.PHONY: run
run: install
	cd tagcompare && python main.py
