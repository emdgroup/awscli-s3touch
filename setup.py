from setuptools import find_packages, setup
setup(
    name = 'awscli-s3touch',
    packages = find_packages(),
    version = '0.0.1',
    install_requires=['awscli'],
    author='Merck Group',
    package_data={'': ['../LICENSE']},
    url='https://github.com/merckgroup/awscli-s3touch',
    license='Apache License 2.0',
    python_requires='>=3',
    description = 'Simulate S3 events without re-uploading a file.',
    namespace_packages = ['awscli'],
)
