==============
awscli-s3touch
==============

Simulate S3 events without re-uploading a file.

-----
Usage
-----

::

    $ aws s3 touch my-bucket --prefix folder/

------------
Installation
------------

::

    $ pip3 install https://github.com/merckgroup/awscli-s3touch/archive/master.zip
    $ aws configure set plugins.name awscli.plugins.s3touch

    # alternatively, edit ~/.aws/config and add the plugin manually
    [plugins]
    name = awscli.plugins.s3touch
