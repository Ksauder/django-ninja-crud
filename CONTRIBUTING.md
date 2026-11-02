# Contributing to Django Ninja CRUD

We welcome contributions to Django-Ninja-CRUD! This document outlines how to contribute to this project and provides guidelines to make the process smoother for everyone involved.

For an overview of how to contribute to open-source projects on GitHub, see [GitHub's official documentation](https://docs.github.com/en/get-started/exploring-projects-on-github/finding-ways-to-contribute-to-open-source-on-github).

## Table of Contents
- [Setting up Development Environment](#setting-up-development-environment)
- [Running Tests](#running-tests)
- [Coding and Commit Conventions](#coding-and-commit-conventions)
- [Labels for Issues and PRs](#labels-for-issues-and-prs)
- [Updating an Existing Pull Request](#updating-an-existing-pull-request)

## Setting up Development Environment

1. **Install devenv**: Follow the [devenv installation guide](https://devenv.sh/getting-started/)

2. **Enable auto activation**: Follow the [auto-activation guide](https://devenv.sh/automatic-shell-activation/)

3. **Enter the Development Shell**:
    ```bash
    devenv shell
    ```
    This provisions Python, creates a virtual environment, installs the project dependencies with `uv`, and installs the git hooks (ruff, mypy, and file checks) that run before each commit. To run the hooks manually inside the shell, use `prek run --all-files -c .pre-commit-config.devenv.yaml`.

## Running Tests

After setting up your development environment, you can run tests to make sure
everything is functioning as expected. To run the tests, use the following commands:

```bash
run-tests
```

Or run the git hooks and tests together with `devenv test`.

## Coding and Commit Conventions

- We adhere to the [PEP 8](https://pep8.org/) coding style guide.
- For commits, we follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Labels for Issues and PRs

We use a set of labels to categorize issues and pull requests. This helps in project management and prioritizing work.

- **bug**: For marking issues that are bugs.
- **enhancement**: For new features or improvements.
- **documentation**: Issues related to documentation.
- **good first issue**: Easier issues aimed at beginners.
- **help wanted**: Issues that need additional support.

## Updating an Existing Pull Request

1. **Ensure Your Fork is Up-to-date**:
    ```bash
    git remote add upstream https://github.com/hbakri/django-ninja-crud.git
    git fetch upstream
    ```

2. **Check Out Your Local Branch**: Associated with the PR.

3. **Rebase Your Branch**:
    ```bash
    git rebase upstream/main
    ```

4. **Resolve Conflicts**: If conflicts arise, resolve them.

5. **Commit Your Changes**.

6. **Force Push to Update the PR**:
    ```bash
    git push origin <your-branch> --force
    ```

---

Thank you for contributing to `django-ninja-crud`! Your efforts help make this project better for everyone.
