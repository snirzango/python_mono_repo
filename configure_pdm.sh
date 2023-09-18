# Will make it so that virtual environments made with `pdm` are made with `pip`, to
# allow `pip install` packages and experimentation. This should not be abused too much, of course.
pdm config venv.with_pip True

# Will make is so that adding dependencies (with `pdm add`) will add to
# the `pyproject.toml` the dependency with a compatability specifier.
pdm config strategy.save compatible
