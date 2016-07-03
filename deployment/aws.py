import os
import time
import shutil

import boto.ec2
import boto.beanstalk
from boto.s3.connection import S3Connection
from boto.s3.key import Key


class AWS:
    def __init__(self, access_key, secret_key):
        self.ec2 = None
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

    def connect_to_ec2(self):
        self.ec2 = boto.ec2.connect_to_region(self.region,
                                              aws_access_key_id=self.access_key,
                                              aws_secret_access_key=self.secret_key)

    def create_instance(self):
        reservation = self.ec2.run_instances(self.image_id,
                                             security_groups=['default'],
                                             instance_type='t2.micro')
        print reservation
        instance = reservation.instances[0]
        time.sleep(10)
        while instance.state != 'running':
            time.sleep(5)
            instance.update()
            print 'Instance state: {}'.format(instance.state)

        print 'Instance {} done!'.format(instance.id)

        self.instance = instance

    def connect_to_beanstalk(self):
        self.beanstalk = boto.beanstalk.connect_to_region(self.region,
                                                          aws_access_key_id=self.access_key,
                                                          aws_secret_access_key=self.secret_key)

    def create_application(self):
        apps = (self.beanstalk.describe_applications([self.app_name])
                ['DescribeApplicationsResponse']['DescribeApplicationsResult']['Applications'])
        if apps:
            self.delete_application(self.app_name)
            while (self.beanstalk.describe_applications([self.app_name])
                   ['DescribeApplicationsResponse']['DescribeApplicationsResult']['Applications']):
                print 'Deleting Application: {}...'.format(self.app_name)
                time.sleep(5)
        self.app = self.beanstalk.create_application_version(self.app_name,
                                                             self.version,
                                                             s3_bucket=self.bucket_name,
                                                             s3_key=self.key_name,
                                                             auto_create_application=True)

    def delete_application(self, name):
        self.beanstalk.delete_application(name, terminate_env_by_force=True)

    def create_application_environment(self):
        self.env = self.beanstalk.create_environment(
            self.app_name,
            version_label=self.version,
            environment_name=self.env_name,
            solution_stack_name='64bit Amazon Linux 2016.03 v2.1.3 running Node.js'
        )

    def zip_application(self):
        path = 'app/'
        shutil.make_archive(self.key_name, 'zip', root_dir=path)
        self.zip_path = os.path.abspath(self.key_name + '.zip')

    def connect_to_s3(self):
        self.s3 = S3Connection(self.access_key, self.secret_key)

    def create_bucket(self):
        bucket = self.s3.lookup(self.bucket_name)
        if bucket is None:
            self.s3.create_bucket(self.bucket_name)

    def create_key(self):
        bucket = self.s3.get_bucket(self.bucket_name)
        k = Key(bucket)
        k.key = self.key_name
        k.set_contents_from_filename(self.zip_path)
