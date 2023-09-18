all: pdm.prod.lock pdm.harmony.lock pdm.standalone.lock requirements.txt

pdm.prod.lock: pyproject.toml pdm.lock
	@echo ""
	@echo ">>>>>> Generating Production Lockfile"
	@pdm lock --prod -L pdm.prod.lock

pdm.harmony.lock: pyproject.toml pdm.lock
	@echo ""
	@echo ">>>>>> Generating Harmony Tests Lockfile"
	@pdm lock -G dev,local -L pdm.harmony.lock

pdm.standalone.lock: pyproject.toml pdm.lock
	@echo ""
	@echo ">>>>>> Generating Harmony Tests Lockfile"
	@pdm lock -G dev -L pdm.standalone.lock

requirements.txt: pdm.prod.lock
	@echo ""
	@echo ">>>>>> Generating Production requirements.txt file"
	@pdm export -L pdm.prod.lock -o requirements.txt --without-hashes