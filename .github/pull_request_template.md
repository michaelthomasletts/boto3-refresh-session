## All submissions

* [ ] Did you include the version part parameter, i.e. [major | minor | patch], to the beginning of the pull request title so that the version is bumped correctly? 
    * Example pull request title: '[minor] Added a new parameter to the `AutoRefreshableSession` object.'
    * Note: the version part parameter is only required for major and minor updates. Patches may exclude the part parameter from the pull request title, as the default is 'patch'.
* [ ] Did you verify that your changes pass pre-commit checks before opening this pull request?
    * The pre-commit checks are identical to required status checks for pull requests in this repository. Know that suppressing pre-commit checks via the `--no-verify` | `-nv` arguments will not help you avoid the status checks!
* [ ] Have you checked that your changes don't relate to other open pull requests?

<!-- You can erase any parts of this template not applicable to your Pull Request. -->

## New feature submissions

* [ ] Does your new feature include documentation? If not, why not?
* [ ] Does that documentation match the numpydoc guidelines?
* [ ] Did you locally test your documentation changes using `sphinx-build doc doc/_build` from the root directory?
* [ ] Did you write unit tests for the new feature? If not, why not?
* [ ] Did the unit tests pass?
* [ ] Did you know that locally running unit tests requires an AWS account? 
    * You must create a ROLE_ARN environment variable on your machine using `export ROLE_ARN=<your role arn here>`.

## Submission details

Describe your changes here. Be detailed!