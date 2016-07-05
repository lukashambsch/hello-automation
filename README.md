IMPORTANT
===============
If there is currently an app named hello-automation linked with your AWS account, the deployment script will delete it (along with it's environment). You can change the app name that this deployment uses by changing the self.app_name value in the \_\_init\_\_ of the AWS class in deployment/aws.py.

Install & Setup
=================

Clone repository: <code>git clone https://github.com/lukashambsch/hello-automation.git</code>

Set up a python <a href="https://virtualenv.pypa.io/en/stable/">virtualenv</a> and <a href="https://virtualenv.pypa.io/en/stable/userguide/#activate-script">activate</a> it.

Once your virtualenv is activated run <code>pip install -r requirements.txt</code> from the root directory of the project to install the project's dependencies. (Ignore error message similar to: failed with error code 1 in /Users/lukashambsch/envs/test-hello/build/cryptography)

Deployment
==============

The project has an expressjs app that serves the static page in the app directory. The python module that interacts with AWS is located in the deployment directory. The deployment script is the deploy.py file in the root directory of the project. The tests for the python module are located in the test directory.

Deploy the app by running <code>python deploy.py -a aws_access_key -s aws_secret_key</code>. Where aws_access_key is the AWS access key for your account and aws_secret_key is the AWS secret key for your account.

It may take a while (15-20 minutes) for the environment to be built and the app to be deployed. Once everything is complete, a url will be displayed in the terminal. This url is where you can view the static web page.

Unit Tests
============
You can run the unit tests by running <code>python -m pytest
test/</code> from the root directory of the project.
