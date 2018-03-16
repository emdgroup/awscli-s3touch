# awscli-s3touch

Simulate S3 events without re-uploading a file.

This command will trigger S3 events for files that already exist in a bucket.
It solves the issue where you want to replay the ``Put`` events that S3 triggers
when you upload a file to S3. The command will scan the bucket for files and
trigger the associated events based on the bucket notification configuration.

Lambda, SQS and SNS notification types are supported as well as prefix and suffix
filters on the key.

**Note**

The events are executed on the client-side meaning that the executing principal
is not S3 but the local principal. Make sure that you have have sufficient access
to the services that will be notified.

---

## Installation

```bash
$ pip3 install https://github.com/merckgroup/awscli-s3touch/archive/master.zip
$ aws configure set plugins.name awscli.plugins.s3touch

# alternatively, edit ~/.aws/config and add the plugin manually
[plugins]
name = awscli.plugins.s3touch
```

## Synopsis

    aws s3 touch help

    aws s3 touch
          bucket <value>
          [--prefix <value>]
          [--page-size <value>]
          [--max-items <value>]
          [--starting-token <value>]
          [--start-after <value>]
          [--delimiter <value>]

## Options

**bucket (string)** Name of the bucket to list.

**--prefix (string)** Limits the response to keys that begin with the specified prefix.

**--page-size  (integer)** The number of results to return in each response
       to a list operation. The default value is 1000 (the  maximum  allowed).
       Using a lower value may help if an operation times out.

**--max-items (integer)** The total number of items to process.

**--starting-token (string)** A token to specify where to start paginating.
       This is the NextToken from a previous aws ls response.

**--start-after (string)** StartAfter is where you want Amazon S3 to  start
       listing  from.  Amazon  S3  starts  listing  after  this specified key.
       StartAfter can be any key in the bucket.

**--delimiter (string)** Character you use to group keys.

See 'aws help' for descriptions of global parameters.

## Examples

The following command will trigger the S3 events for one file that fol-
lows alphabetically after myfile101.tar.gz in folder myfolder/:

    aws s3 touch my-bucket --max-items 1 --prefix myfolder/ --start-after myfolder/myfile101.tar.gz

By  default, touch will recurse the directory structure. If you want to
restrict the command to a single folder you can provide the --delimiter
option.  This  command  will trigger the S3 events for all files in the
root directory and will not traverse the directory structure:

    aws s3 touch my-bucket --max-items --delimiter '/'

