.PHONY: run stage1 direct test help clean

PYTHON ?= python3
PACKAGE ?= A
REPO    ?= data/test_repo_simple.txt
DEPTH   ?= 5

help:
	@echo "Targets:"
	@echo "  make run          - run with default test data (Graphviz output)"
	@echo "  make stage1       - print configuration only"
	@echo "  make direct       - print direct dependencies"
	@echo "  make test         - run unit tests"
	@echo "  make clean        - remove temporary files"

run:
	./run.sh --package $(PACKAGE) --repo $(REPO) --test --depth $(DEPTH)

stage1:
	./run.sh --package $(PACKAGE) --repo $(REPO) --test --depth $(DEPTH) --stage1

direct:
	./run.sh --package $(PACKAGE) --repo $(REPO) --test --direct-only

test:
	$(PYTHON) -m unittest discover -s tests -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -f graph.dot *.png *.svg
