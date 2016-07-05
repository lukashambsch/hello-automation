import os
import time
import shutil

import boto
import boto.ec2
import boto.beanstalk
from boto.s3.connection import S3Connection
from boto.s3 import key


class AWS:
    def __init__(self, access_key, secret_key):
        self.beanstalk = None
        self.s3 = None
        self.access_key = access_key
        self.secret_key = secret_key
        self.env_name = 'hello-env'
        self.app_name = 'hello-automation'
        self.version = 'v1'
        self.region = 'us-west-2'
        self.image_id = 'ami-455c5975'
        self.bucket_name = 'lukashambsch-helloautomation'
        self.key_name = 'app'

    def connect_to_beanstalk(self):
        '''Creates connections to Elastic Beanstalk'''
        self.beanstalk = boto.beanstalk.connect_to_region(self.region,
                                                          aws_access_key_id=self.access_key,
                                                          aws_secret_access_key=self.secret_key)

    def create_application(self):
        '''
        Creates versioned application in elastic beanstalk
        If application by that name already exists, it will be deleted and a new one
        will be created.
        '''
        # Check if app already exists
        apps = (self.beanstalk.describe_applications([self.app_name])
                ['DescribeApplicationsResponse']['DescribeApplicationsResult']['Applications'])

        # If app exists delete it.
        if len(apps) > 0:
            self.delete_application(self.app_name)
            #  Log while waiting for deletion, so user knows what is going on.
            while (self.beanstalk.describe_applications([self.app_name])
                   ['DescribeApplicationsResponse']['DescribeApplicationsResult']['Applications']):
                print 'Deleting Application: {}...'.format(self.app_name)
                time.sleep(10)

        # Create application
        self.app = self.beanstalk.create_application_version(self.app_name,
                                                             self.version,
                                                             s3_bucket=self.bucket_name,
                                                             s3_key=self.key_name,
                                                             auto_create_application=True)

    def delete_application(self, name):
        '''
        Deletes the application and associated environment for the given application name.
        '''
        self.beanstalk.delete_application(name, terminate_env_by_force=True)

    def create_application_environment(self):
        '''
        Creates environment to host application.
        '''
        self.env = self.beanstalk.create_environment(
            self.app_name,
            version_label=self.version,
            environment_name=self.env_name,
            solution_stack_name='64bit Amazon Linux 2016.03 v2.1.3 running Node.js'
        )

    def get_environment_url(self):
        '''
        Checks for when environment is ready. When ready, give url where app can be viewed.
        '''
        # instantiate self.created
        self.created = {'Status': None}

        while self.created['Status'] != 'Ready':
            # Filter machines based on status. For this purpose the only app with a status that is not terminated
            # will be our current app. Would need to be updated when multiple apps are hosted.
            self.created = [e for e in self.beanstalk.describe_environments()
                            ['DescribeEnvironmentsResponse']['DescribeEnvironmentsResult']['Environments']
                            if e['Status'] != 'Terminated'][0]
            print 'Creating Environment...Current Status: {}'.format(self.created['Status'])
            time.sleep(10)

        # Notify user that deployment is complete and website is ready for viewing.
        print 'Environment Complete! You can view the site at: {}'.format(self.created['EndpointURL'])

    def zip_application(self):
        '''
        Creates zip of application files to be deployed.
        '''
        path = 'app/'
        shutil.make_archive(self.key_name, 'zip', root_dir=path)
        self.zip_path = os.path.abspath(self.key_name + '.zip')

    def connect_to_s3(self):
        '''Creates an s3 connection'''
        self.s3 = boto.connect_s3(self.access_key, self.secret_key)

    def create_bucket(self):
        '''
        If the bucket does not already exist, create the bucket.
        '''
        bucket = self.s3.lookup(self.bucket_name)
        if bucket is None:
            self.s3.create_bucket(self.bucket_name)

    def create_key(self):
        '''
        Creates the key to store the application in S3.
        If key by that name exists already, it will be overwritten.
        '''
        bucket = self.s3.get_bucket(self.bucket_name)
        k = key.Key(bucket)
        k.key = self.key_name
        k.set_contents_from_filename(self.zip_path)
