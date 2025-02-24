Contributing
============

Thank you for choosing to contribute to this project!

Please follow the below documentation closely.

Requirements
------------

- Python 3.10+
- An AWS account
- An IAM role with ``s3:ListBuckets`` permissions
- A local environment variable named ``ROLE_ARN`` containing your IAM role ARN

Steps
-----

1. Fork this project.
2. Clone the newly created (i.e. forked) repository in your account to your local machine.
3. From your terminal, navigate to where the forked repository was cloned to your local machine, i.e. ``cd boto3-refresh-session``.
4. Run ``poetry install --all-groups``
   
   * This command installs all developer and package dependencies.

5. Run ``pre-commit install && pre-commit install-hooks``
   
   * This command installs all pre-commit hooks.

6. Create a local environment variable containing your role ARN from your terminal by running ``export ROLE_ARN=<your role ARN>``
7. Make your changes.
   
   * You will be met by a pull request checklist when you attempt to create a pull request with your changes. Follow that checklist to ensure your changes satisfy the requirements in order to expedite the review process.

8. If your changes include an additional dependency, then you will need to run ``poetry install <dependency>``. This command will update ``pyproject.toml`` with your dependency.
9. Commit and push your changes to a branch on the forked repository.
   
   * ``pre-commit`` will run a few checks when ``git commit`` is run. Those checks **must** succeed for you to proceed to ``git push``!

10.  Open a pull request that compares your forked repository branch with the ``main`` branch of the production repository.
11.  Upon creation (or update), your pull request will:

     *  Trigger status checks

        *  .. warning::
               **Forked pull requests cannot use repository secrets!** Therefore, unit tests cannot be performed via Github Actions! Please bear with the codeowners as they evaluate your work, due to that limitation. Include screenshots of successful local ``pre-commit`` runs in order to expedite the review process! Apologies -- this limitation of Github is steadfast, and the codeowners are looking for additional strategies for circumventing this limitation in the meantime. We understand it is frustrating that status checks will fail, no matter what, until a solution is found.
     
     *  Require code owner approval in order to be merged

12.  Make and submit additional changes, if requested; else, merge your approved pull request.