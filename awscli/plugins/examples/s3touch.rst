The following command will trigger the S3 events for one file that follows
alphabetically after ``myfile101.tar.gz`` in folder ``myfolder/``::

    aws s3 touch my-bucket --max-items 1 --prefix myfolder/ --start-after myfolder/myfile101.tar.gz

By default, touch will recurse the directory structure. If you want to restrict
the command to a single folder you can provide the ``--delimiter`` option. This
command will trigger the S3 events for all files in the root directory and
will not traverse the directory structure::

    aws s3 touch my-bucket --max-items --delimiter '/'
