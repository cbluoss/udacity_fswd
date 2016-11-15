Get started
===========

	pip install -r requirements.txt

either use the existing demo database
	python application.py

or create a new one
	rm test.db
	python application.py --setup
	python application.py

open https://localhost:8000/

REST API Endpoints are:
	/api/item
	/api/item/<itemid>
	/api/category
	/api/category/<categoryid>