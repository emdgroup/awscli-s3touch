Simulate S3 events without re-uploading a file.

This command will trigger S3 events for files that already exist in a bucket.
It solves the issue where you want to replay the ``Put`` events that S3 triggers
when you upload a file to S3. The command will scan the bucket for files and
trigger the associated events based on the bucket notification configuration.

Currently, only the Lambda event notification is available.

.. note::

    The events are executed on the client-side meaning that the executing principal
    is not S3 but the local principal. Make sure that you have have sufficient access
    to the services that will be notified.
