import argparse
import sys

from deployment.aws import AWS


def main(args):
    if not args.a:
        raise ValueError('You must pass in your AWS access key. (Use the -a option)')
    if not args.s:
        raise ValueError('You must pass in your AWS secret key. (Use the -s option)')

    aws_args = {
        'access_key': args.a,
        'secret_key': args.s
    }

    aws = AWS(**aws_args)
    aws.zip_application()
    aws.connect_to_s3()
    aws.create_bucket()
    aws.create_key()
    aws.connect_to_beanstalk()
    aws.create_application()
    aws.create_application_environment()
    aws.get_environment_url()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', help='AWS Access Key Id')
    parser.add_argument('-s', help='AWS Secret Key')

    main(parser.parse_args(sys.argv[1:]))
