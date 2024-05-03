black:
	@black --check --diff ./

flake8:
	@flake8 ./

isort:
	@isort --diff  -c ./

fix-black:
	black .

fix-isort:
	isort  .

publish:
	cloudsmith push python carta/pip dist/*.whl

publish-dev:
	cloudsmith push python carta/pip-test dist/*.whl

build-sdist:
	@python setup.py sdist --formats=gztar

build-wheel:
	@python setup.py bdist_wheel

