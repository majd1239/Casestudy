from setuptools import setup,find_packages

setup(name='Turbines Signal Dataflow',
      install_requires=[
          'pandas==0.23.4',
          'pandas-gbq==0.9.0',
          'sqlalchemy',
          'pymysql',
      ],
      packages=find_packages(),
 )

