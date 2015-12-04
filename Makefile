install:
	pip install -r requirements.txt -q

.PHONY: flake
flake: install
	flake8

.PHONY: test
test: install flake
	PYTHONPATH=. py.test -s -m "not integration" --cov-config .coveragerc --cov-report=term-missing --cov=tagcompare tagcompare/test/

.PHONY: test-all
test-all: install flake
	PYTHONPATH=. py.test -s --cov-config .coveragerc --cov-report=term-missing --cov=tagcompare tagcompare/test/

# Do a funn run including gather image and compare them
.PHONY: run
run: install
	cd tagcompare && python main.py

# Do a compare only run from previously gathered images
.PHONY: compare
compare: install
	cd tagcompare && python compare.py

# Aggregates the output
.PHONY: output
output: install
	cd tagcompare && python output.py

# Captures screenshots for tags
.PHONY: capture
capture: install
	cd tagcompare && python capture.py
