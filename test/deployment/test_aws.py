import pytest

import mock

from deployment.aws import AWS


ACCESS_KEY = 'test_access_key'
SECRET_KEY = 'test_secret_key'
ENV_NAME = 'hello-env'
APP_NAME = 'hello-automation'
VERSION = 'v1'
REGION = 'us-west-2'
IMAGE_ID = 'ami-455c5975'
BUCKET_NAME = 'lukashambsch-helloautomation'
KEY_NAME = 'app'
REGION = 'us-west-2'
SOLUTION_STACK_NAME = '64bit Amazon Linux 2016.03 v2.1.3 running Node.js'



class BaseTestAWS(object):
    @pytest.fixture
    def aws(self):
        return AWS(ACCESS_KEY, SECRET_KEY)


class TestAWSInit(BaseTestAWS):
    def test_beanstalk(self, aws):
        assert aws.beanstalk is None

    def test_s3(self, aws):
        assert aws.s3 is None

    def test_access_key(self, aws):
        assert aws.access_key == ACCESS_KEY

    def test_secret_key(self, aws):
        assert aws.secret_key == SECRET_KEY

    def test_env_name(self, aws):
        assert aws.env_name == 'hello-env'

    def test_app_name(self, aws):
        assert aws.app_name == 'hello-automation'

    def test_version(self, aws):
        assert aws.version == 'v1'

    def test_region(self, aws):
        assert aws.region == 'us-west-2'

    def test_image_id(self, aws):
        assert aws.image_id == 'ami-455c5975'

    def test_bucket_name(self, aws):
        assert aws.bucket_name == 'lukashambsch-helloautomation'

    def test_key_name(self, aws):
        assert aws.key_name == 'app'


class TestAWSBeanstalk(BaseTestAWS):
    @mock.patch('deployment.aws.boto.beanstalk.connect_to_region')
    def test_connect_to_beanstalk(self, mock_beanstalk, aws):
        aws.connect_to_beanstalk()
        mock_beanstalk.assert_called_with(REGION, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

    def test_create_application(self, aws):
        aws.beanstalk = mock.Mock()
        aws.beanstalk.describe_applications.return_value = {
            'DescribeApplicationsResponse': {
                'DescribeApplicationsResult': {
                    'Applications': []
                }
            }
        }
        aws.create_application()
        aws.beanstalk.create_application_version.assert_called_with(APP_NAME,
                                                                    VERSION,
                                                                    s3_bucket=BUCKET_NAME,
                                                                    s3_key=KEY_NAME,
                                                                    auto_create_application=True)

    def test_delete_application(self, aws):
        name = 'test'
        aws.beanstalk = mock.Mock()
        aws.delete_application(name)
        aws.beanstalk.delete_application.assert_called_with(name, terminate_env_by_force=True)

    def test_create_application_environment(self, aws):
        aws.beanstalk = mock.Mock()
        aws.create_application_environment()
        aws.beanstalk.create_environment.assert_called_with(APP_NAME,
                                                            version_label=VERSION,
                                                            environment_name=ENV_NAME,
                                                            solution_stack_name=SOLUTION_STACK_NAME)

    def test_get_environment_url(self, aws):
        url = 'http://test.com'
        aws.beanstalk = mock.Mock()
        aws.beanstalk.describe_environments.return_value = {
            'DescribeEnvironmentsResponse': {
                'DescribeEnvironmentsResult': {
                    'Environments': [{
                        'Status': 'Ready',
                        'EndpointURL': url
                    }]
                }
            }
        }
        aws.get_environment_url()
        assert aws.created['EndpointURL'] == url


class TestAWSS3(BaseTestAWS):
    @mock.patch('deployment.aws.boto.connect_s3')
    def test_connect_to_s3(self, mock_s3, aws):
        aws.connect_to_s3()
        mock_s3.assert_called_with(ACCESS_KEY, SECRET_KEY)

    def test_create_bucket_lookup(self, aws):
        aws.s3 = mock.Mock()
        aws.create_bucket()
        aws.s3.lookup.assert_called_with(BUCKET_NAME)

    def test_create_bucket_create(self, aws):
        aws.s3 = mock.Mock()
        aws.s3.lookup.return_value = None
        aws.create_bucket()
        aws.s3.create_bucket.assert_called_with(BUCKET_NAME)

    @mock.patch('deployment.aws.boto.s3.key.Key')
    def test_create_key_get_bucket(self, mock_key, aws):
        aws.s3 = mock.Mock()
        aws.zip_path = 'tst'
        aws.create_key()
        aws.s3.get_bucket.assert_called_with(BUCKET_NAME)

    @mock.patch('deployment.aws.boto.s3.key.Key')
    def test_create_key_Key(self, mock_key, aws):
        mock_bucket = mock.Mock()
        aws.s3 = mock.Mock()
        aws.s3.get_bucket.return_value = mock_bucket
        aws.zip_path = 'tst'
        aws.create_key()
        mock_key.assert_called_with(mock_bucket)

    @mock.patch('deployment.aws.boto.s3.key.Key')
    def test_create_key_key_name(self, mock_key, aws):
        created_key = mock.Mock()
        mock_key.return_value = created_key
        aws.s3 = mock.Mock()
        aws.zip_path = 'tst'
        aws.create_key()
        assert created_key.key == KEY_NAME

    @mock.patch('deployment.aws.boto.s3.key.Key')
    def test_create_key_set_contents(self, mock_key, aws):
        created_key = mock.Mock()
        mock_key.return_value = created_key
        aws.s3 = mock.Mock()
        aws.zip_path = 'tst'
        aws.create_key()
        created_key.set_contents_from_filename.assert_called_with(aws.zip_path)
