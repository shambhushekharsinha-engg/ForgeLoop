.PHONY: help install test simulate dashboard verify package clean

help:
	@echo "ForgeLoop Commands:"
	@echo "  make install    - Install dependencies for analysis and development"
	@echo "  make test       - Run all unit tests"
	@echo "  make simulate   - Run the Phase 5 synthetic simulation demo"
	@echo "  make dashboard  - Export the static web dashboard to public/"
	@echo "  make verify     - Run the pre-flight checklist for Kaggle artifacts"
	@echo "  make package    - Package the submission artifacts into a zip file"
	@echo "  make clean      - Remove generated caches, plots, and output files"

install:
	pip install -e ".[analysis,dev]"

test:
	pytest -q

simulate:
	python simulate_phase5.py

dashboard:
	python -m forgeloop.cli.export_web

verify:
	python scripts/verify_submission.py

package:
	python scripts/create_submission.py

clean:
	rm -rf .pytest_cache
	rm -rf public/plots
	rm -f public/index.html
	rm -f ForgeLoop_Submission.zip
