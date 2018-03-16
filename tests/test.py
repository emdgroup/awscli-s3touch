from src.awscli.plugins.s3touch import S3Touch
from awscli.customizations.commands import BasicCommand
from awscli import EnvironmentVariables
import botocore.session
from unittest.mock import MagicMock

session = botocore.session.Session(EnvironmentVariables)

touch = S3Touch(session)

class Args(object):
  bucket = None

args = MagicMock()
args.bucket='s3touch-test-testbucket-1t8e1q1m8s2h8'
args.delimiter=None
args.start_after=None
args.prefix=None

touch._run_main(args, {})
