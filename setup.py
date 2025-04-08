from setuptools import setup, find_packages

setup(
    name='massage_booking',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask==3.1.0',
        'Flask-Login==0.6.3',
        'Flask-Mail==0.10.0',
        'Flask-SQLAlchemy==3.1.1',
        'Flask-WTF==1.2.2',
        'Werkzeug==3.1.3',
        'WTForms==3.2.1',
        'ics==0.7.2',
        'email_validator==2.2.0',
        'python-dotenv==1.1.0'
    ],
    setup_requires=[
        'setuptools>=42'
    ],
)
