# Development Guide

This document hopefully contains all of the necessary information for you to start developing in this repository right now, but that does not replace the communication expected with the rest of your team members.

## I don't care about anything - Tell me the essentials

The repository is a monorepo.
The repository is organized to projects by categories (services, libraries, tools, etc).
Therefore if you want to find the code of the `x` service - you can find it in the `services` directory, expectedly.

We use `pdm` for project & package management. You can read more about it below, as well in their documentation.

- Install it.
- Configure it to the Pagaya's PyPi (it's a process, unfortunately. Ask Shacham how, hopefully the process improved).
- Run `source configure_pdm.sh` in order to configure recommended configurations to the tools.

And that's it.

Now in order to start working on a project, just `cd` over to it, run `pdm sync` to install all of its dependencies (PDM will make the `virtualenv`s for you! Managing them on your own is not needed anymore!), and that's it - you're ready to work.

The only thing that's left to disclose is `pdm run checks` which is the command that the CI runs in order to runs the tests and stuff. So run them yourself in order test whether you pass the CI or not, locally.

Please note that we have a lot of format checks configured, and so a friendly suggestion is to use `pdm run format` as liberally as you can and not try to fix those formatting errors yourselves. Running `pdm run format` will automatically fix those formatting errors 99% of the time, save for things for documentation, etc.

## Repository Guide

This repository is constructed as a monorepo around the Datafy domain. All of the services, libraries and tools should relate to it in some ways. Projects should be located in an indicative location, with their definition being:

- `libs` - For libraries containing modules that are meant to be installed using a package manager (like `pip` or `pdm`), imported, and then reused.
- `services` - For serivces.
- `tools` - For first-party development tools.

## Python Projects Guide

All of the source-code present in the repository is expected to be written in Python. The following relates to Python development in this repository.

### PDM - Python Development Master

We're the prime development team in Pagaya - the first! - To use PDM (or `P`ython `D`evelopment `M`aster), which is a tooling suite for Python
which aims to be the one-stop-shop **project management & package-management solution for Python**.

You can read more at their official documentation [here](https://pdm.fming.dev/).

Common configurations that you should probably set are:
- `pdm config venv.with_pip True` - Will make it so that virtual environments made with `pdm` are made with `pip`, to allow `pip install` packages and experimentation. This should not be abused too much, of course.
- `pdm config strategy.save compatible` - Will make is so that adding dependencies (with `pdm add`) will add to the `pyproject.toml` the dependency with a compatability specifier.

For your convencience, you can run the following in order to configure it quickly. Just run:

``` shell
source ./configure_pdm.sh
```

With `pdm` we'll be doing the following:

- Manage requirements
- Use their build-system in order to build the packages
- Use their publishing utilities to publish the package (although through CI/CD, you won't notice this).
- Maybe even utilize the fact that they can create virtualenvs for you, encapsulating that concept forever.

But, since we're doing a monorepo, it can make some things slightly harder to do. Specifically, all of our
quality checks and inspections, in a functioning monorepo of our design, should be done twice:

1. Run the checks w/ all of the dependencies **as they exist in the repository**
2. Run the checks w/ all of the dependencies **as they exist in the outside world (pypi)**

That's to say, let's say we have a service `datafy-app` which depends on a library called `datafy-utils`. Both are available in the repository.

In production, our `datafy-app` service will use the `datafy-utils` as is available in the `pypi`, and so we will have to know whether the checks
pass prior to us deploying it.

But in local development, we will want to work with both simultaniously, and maybe continuously, and thus we'll want to have a continuous feedback
loop in running the checks with both installed.

Our solution will inherit from the proposition mentioned [here](https://pdm.fming.dev/latest/usage/dependency/#select-a-subset-of-dependency-groups-to-be-installed-or-locked), which describes **2 lockfiles** - one for development, and one for production.

### `pyproject.toml`

Modern Python projects are managed through a magical file called `pyproject.toml`. There are multiple PEPs that define it, since it has evolved over time, and so no one link can explain it all, I think.

But the gist is that the entirety of a Python project, which in this day and age, would be defined in it. With that "entirety" being:
- Metadata of the project.
- Decleration of the dependencies.
- Configuration of it's various tooling (`black`, `ruff`, `pylint`).

Here's an example:

``` toml
# Decleration of a build-system. There are various available, but we're with PDM
# currently, so we'll do with it. Switching would not be a big deal though, honestly.
[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"

# Project metadata.
[project]
name = "example-project"
description = "This is an example project."
version = "0.1.0"
# Dependencies declaration.
dependencies = [
	"requests>=1.2.3",
	"pydantic==1.10.2",
]
requires-python = ">=3.8, <4"

# Tooling configuration.
[tool.black]
line_length = 120
```

So it's generally a good idea to get to know that file.

### Format the code using `black`

`black` is the uncompromising Python formatter. Code should be formatted using it. In cases where it mangles nested literals in a way that's deliberately unwanted, it's possibly to pointedly be turned off for specific sections. Do not be ashamed from doing so if it makes sense.

### Format & Lint the code using `ruff`

`ruff` is the newest tool out of all of that's written here. It takes the most to setup, and as such it took us the most to actually
add to the project. It is a fantastic, blazingly fast Python linter that also auto-fixes a bunch of stuff. It's rules and configurations
are written in the in the root `pyproject.toml` file. Unlike all of the other tools used in the project - this tool supports monorepos
out of the box, and so integration in the `monotools` tool was not needed.

Read more about the tool here:
- [Ruff's Official Documentation](https://beta.ruff.rs/docs/)
- [Ruff's GitHub Repository](https://github.com/astral-sh/ruff)

### Check your typing using `mypy`

`mypy` is a static type checker for Python, and is expected to be run on all Python code present in the repository. It does not need to be *strict*, although being elaborative in type detail is expected.

### Code Linting is done using `pylint`

`pylint` is one of the most popular Python linters available, and thus we integrated it to our workflow. It supports a lot of rules of the gate
and is very configurable, but we found that the default configuration is the one we're the most comfortable with, *most of the time*.

**NOTE:** `pylint` and `ruff` both operate within a similar jurisdiction, but due to `ruff` being more flexible, more performant, and having the ability to automatically fix most of the errors it raises automatically - it is our perferred tool. Ideally, one day we'll fully translate all of `pylint`'s rules over to `ruff`. But since that work is not free - for the meanwhile, we'll run both.

But in the meantime - in cases of conflicts between `pylint` and `ruff` - unless `pylint`'s output is of superiour value and cannot be replicated in `ruff` - we'll elect to disable `pylint`'s handling of that specific rule and enabling `ruff`'s.

Our rules are written in the root `pyproject.toml`, and execution is done via the `monotools` tool.

Also, there are plenty of cases where you may want to turn off `pylint` for a specific line/sequence of lines/files.
This is something that is okay as long as sound judgement is applied.
We may be okay with turning off doc-string requirements for fucntions on one-off scripts - but that's not the case
for security checks on our production code.

- [The Official Documentation](https://pylint.readthedocs.io/en/stable/user_guide/messages/message_control.html)
- [Stack Overflow - Shows how to do multiple rules at once](https://stackoverflow.com/questions/4341746/how-do-i-disable-a-pylint-warning)

### `make` for supplumentary things.

`make` is a very basic build-system. And by very basic I mean, you can define "targets" (which can match filenames or just _be_ plain commands) in relation
to optional dependencies (which are also targets), and executing on these targets can mean doing anything we want. That is to say, we like `make`.

We use make for 2 reasons - To generate **flavored lockfiles**, and to generate the **requirements.txt**

The *flavored lockfiles* are PDM lockfiles that subsets of the *main* lockfile, containing only dependencies relevant to a specific environment.
For example, `pdm.prod.lock` lockfile that reflects production, etc. We've got 3 that are generated in total. Don't pay mind to that.

In regards to `requirements.txt`, as part of compliance, we're using `snyk`, which scans `requirements.txt` files for security flawed Python packages (for specific versions, of course). We're using PDM, which is the best, but `snyk` doesn't support it, so we need to generate `requirements.txt`. Easy.

## How to create new projects

Creating a new project in the repository is very simple. Let's say you want to create a new library/service/tool called `mything`.

**Step 1:** - Enter the appropriate directory (`libs`/`services`/`tools`). Judge which directory is the appropriate one, based on the project itself.
**Step 2:** - Make a new directory where the project will reside. For example: `my-thing`. **MAKE SURE IT IS IN KEBAB CASE!** Always go kebab case where possible. The command will be `mkdir my-thing && cd my-thing` to make and enter the directory.
**Step 3:** - Run the following command afterwards to create the project with our template: `pdm init ../../templates/package`.

That's it. The template by this point is pre-configured with all of our checks and requirements, and should work right out of the gate.
