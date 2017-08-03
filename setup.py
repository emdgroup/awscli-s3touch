from setuptools import find_packages, setup
setup(
    name = 'awscli-s3touch',
    description='Simulate S3 events without re-uploading a file.',
    long_description=open('README.rst').read(),
    packages = ['awscli.plugins.s3touch'],
    version = '0.0.6',
    install_requires=['awscli'],
    author='Merck Group',
    url='https://github.com/merckgroup/awscli-s3touch',
    license='Apache License 2.0',
    python_requires='>=3',
    package_data={'': ['examples/*.rst']},
)
