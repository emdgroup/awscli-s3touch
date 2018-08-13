from setuptools import find_packages, setup
setup(
    name = 'awscli-s3touch',
    description='Simulate S3 events without re-uploading a file.',
    long_description=open('README.md').read(),
    packages = ['awscli.plugins.s3touch'],
    package_dir={'':'src'},
    version = '0.1.0',
    install_requires=['awscli'],
    author='EMD Group (emdgroup.com)',
    url='https://github.com/merckgroup/awscli-s3touch',
    license='Apache License 2.0',
    python_requires='>=3',
    package_data={'': ['examples/*.rst']},
    zip_safe=True,
)
