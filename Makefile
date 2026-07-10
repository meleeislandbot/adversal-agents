.PHONY: validate doctor

validate:
	python3 scripts/validate_repo.py
	python3 -m unittest discover -s tests -p 'test_*.py'

doctor:
	python3 templates/project/scripts/adversal_doctor.py
