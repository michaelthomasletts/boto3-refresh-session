## Basic Setup

Clone the repository.

```bash
$ git clone https://github.com/michaelthomasletts/boto3-refresh-session.git && cd boto3-refresh-session
```

Install poetry. Follow the instructions to do that [here](https://python-poetry.org/docs/). Then, install the dependencies for working on this project.

```bash
$ poetry install
```

Make your changes.

## Testing

You will need an AWS account in order to run unit tests.

After creating an account, create an IAM user and IAM role, unless you already have them available already. Provide a trust relationship between them such that your IAM user (or AWS account) can assume that role. Lastly, allow that IAM role permission to list buckets in S3, i.e. `s3:ListBucket`. Copy the role ARN.

Using that role ARN, create a local environment variable like so.

```bash
$ export ROLE_ARN=<your-role-arn>
```

Next, create an IAM access key for the user you just created like so.

```bash
$ aws iam create-access-key --user-name <your-user-name>
```

Create an `~/.aws/config` file like so.

```bash
$ aws configure
```

Enter the access key and secret access key values that were generated in the previous step.

Finally, add your changes to git.

```bash
$ git add .
```

To run the tests, you have two options: run `pre-commit run` or `git commit ...`. The latter is simpler. So that will be demonstrated here.

```bash
$ git commit -m "<message>"
```

If the tests fail, then you will need to modify your code and repeat the above steps again, e.g. `git add .`, etc. If, however, your tests succeed then you are ready to push your changes!