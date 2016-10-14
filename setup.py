from distutils.core import setup

setup(
    name='django-arangodb',
    version='0.0.1',
    packages=['sample_app', 'sample_app.migrations', 'sample_project', 'arangodb_driver', 'arangodb_driver.models'],
    url='https://github.com/pablotcarreira/django-arangodb',
    license='BSD',
    author='Pablo Torres Carreira',
    author_email='pablotcarreira@gmail.com',
    description='Django database backend for ArangoDB '
)
