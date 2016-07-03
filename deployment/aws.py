import os
import time
import zipfile

import boto.ec2
import boto.beanstalk


class AWS:
    def __init__(self, access_key, secret_key, region='us-west-2', image_id='ami-455c5975'):
        self.conn = None
        self.beanstalk = None
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.image_id = image_id
        self.zip_name = 'app.zip'

    def connect_to_ec2(self):
        self.conn = boto.ec2.connect_to_region(self.region,
                                               aws_access_key_id=self.access_key,
                                               aws_secret_access_key=self.secret_key)

    def create_instance(self):
        reservation = self.conn.run_instances(self.image_id,
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

    def create_application(self, name, version):
        self.app_name, self.version = name, version
        apps = (self.beanstalk.describe_applications([name])
                ['DescribeApplicationsResponse']['DescribeApplicationsResult']['Applications'])
        if apps:
            self.delete_application(self.app_name)
        self.beanstalk.create_application_version(self.app_name, self.version, auto_create_application=True)

    def delete_application(self, name):
        self.beanstalk.delete_application(name)

    def create_application_environment(self):
        self.env = self.beanstalk.create_environment(
            self.app_name,
            version_label=self.version,
            environment_name='stelligent',
            solution_stack_name='64bit Amazon Linux 2016.03 v2.1.3 running Node.js'
        )

    def zip_application(self):
        path = 'app/'
        handler = zipfile.ZipFile(self.zip_name, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(path):
            for f in files:
                handler.write(os.path.join(root, f))
        self.zip_path = os.path.abspath(self.zip_name)
