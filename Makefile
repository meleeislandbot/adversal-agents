.PHONY: validate doctor

validate:
	python3 scripts/validate_repo.py

doctor:
	python3 templates/project/scripts/adversal_doctor.py
