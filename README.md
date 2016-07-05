Install & Setup
=================

Clone repository: <code>git clone https://github.com/lukashambsch/hello-automation.git</code>

Set up a python <a href="https://virtualenv.pypa.io/en/stable/">virtualenv</a> and <a href="https://virtualenv.pypa.io/en/stable/userguide/#activate-script">activate</a> it.

Once your virtualenv is activated run <code>pip install -r requirements.txt</code> from the root directory of the project.

Deployment
==============

The project has an expressjs app that serves the static page in the app directory. The python module that interacts with AWS is located in the deployment directory. The deployment script is the deploy.py file in the root directory of the project. The tests for the python module are located in the test directory.

Deploy the app by running <code>python deploy.py -a <aws_access_key_id> -s <aws_secret_key></code>.
