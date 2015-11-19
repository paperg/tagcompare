.PHONY: test
test:
	PYTHONPATH=. py.test -s

.PHONY: run
run:
	cd tagcompare && python main.py
