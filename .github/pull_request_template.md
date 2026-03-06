## All submissions

* [ ] Does your pull request title follow Conventional Commits (`type(scope)!: summary`)?
    * Allowed `type` values in this repository: `feat`, `fix`, `perf`, `refactor`, `docs`, `style`, `test`, `build`, `ci`, `chore`, `revert`.
    * Example pull request title: `fix(session): normalize IoT endpoint parsing`.
    * For breaking changes in PR titles, use `!` before `:` (example: `feat!: remove deprecated session API`).
    * You can find additional details [here](https://www.conventionalcommits.org/en/v1.0.0/#summary).
    * Release Please uses these commit types to determine release bumps (`feat` -> minor, `fix`/`perf` -> patch, `!` -> major).
* [ ] Did you verify that your changes pass pre-commit checks before opening this pull request?
    * The pre-commit checks are identical to required status checks for pull requests in this repository. Know that suppressing pre-commit checks via the `--no-verify` | `-nv` arguments will not help you avoid the PR status checks!
    * To ensure that pre-commit checks work on your branch before running `git commit`, run `pre-commit install` and `pre-commit install-hooks` beforehand. 
    * If needed, run the full suite locally with `pre-commit run --all-files`.
* [ ] Have you checked that your changes don't relate to other open pull requests?

<!-- You can erase any parts of this template not applicable to your Pull Request. -->

## New feature submissions

* [ ] Does your new feature include documentation? If not, why not?
    * [ ] Does that documentation match the numpydoc guidelines?
    * [ ] Did you locally test your documentation changes using `uv run --directory docs make clean html` from the root directory?
* [ ] Did you write unit tests for the new feature? If not, why not?
    * [ ] Did the unit tests pass?

## Submission details

Describe your changes here. Be detailed!
