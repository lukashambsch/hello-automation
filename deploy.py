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
    if args.r:
        aws_args['region'] = args.r
    if args.i:
        aws_args['image_id'] = args.i

    aws = AWS(**aws_args)
    aws.zip_application()
    #aws.connect_to_ec2()
    #aws.create_instance()
    #print aws.instance
    #aws.connect_to_beanstalk()
    #aws.create_application('hello-automation', '0.0')
    #aws.create_application_environment()
    print aws.zip_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', help='AWS Access Key Id')
    parser.add_argument('-s', help='AWS Secret Key')
    parser.add_argument('-r', help='AWS EC2 region')
    parser.add_argument('-i', help='AWS EC2 Image Id')

    main(parser.parse_args(sys.argv[1:]))
