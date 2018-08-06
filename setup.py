from setuptools import setup

with open('README.md', 'r') as h:
    README = h.read()

setup(
    name='nbviewerbot',
    version='0.1.0',
    description='Convert GitHub Jupyter Notebook links on Reddit to nbviewer',
    long_description=README,
    long_description_content_type='text/markdown',
    author='John Paton',
    author_email='john@johnpaton.net',
    url='https://github.com/JohnPaton/nbviewerbot',
    packages=['nbviewerbot'],
    install_requires=[
        'praw',
        'bs4',
        'lxml',
        'python-dotenv',
        'click',
        'backoff',
    ],
    python_requires='>=3.4',
    entry_points={
        'console_scripts':[
            'nbviewerbot = nbviewerbot.nbviewerbot:cli'
        ]
    },
    include_package_data=True,
    package_data={'nbviewerbot': ['.env', '.env_template', 'resources.d/*']},
    zip_safe=True,
)
