import json
import os
import setuptools


metadata_path = os.path.join('panki', 'metadata', 'metadata.json')
with open(metadata_path, 'r') as file:
    metadata = json.load(file)

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name=metadata['name'],
    version=metadata['version'],
    url=metadata['url'],
    description=metadata['description'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=metadata['keywords'],
    author=metadata['author']['name'],
    author_email=metadata['author']['email'],
    packages=setuptools.find_packages(exclude=['tests']),
    entry_points={'console_scripts': [metadata['cli']]},
    classifiers=metadata['classifiers'],
    python_requires=metadata['requires']['python'],
    install_requires=metadata['requires']['packages'],
    include_package_data=True
)
