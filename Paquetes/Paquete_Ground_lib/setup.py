from setuptools import setup

setup(
    name = 'GroundMotion_lib',
    version = '1.0.0',
    packages = ['GroundMotion_lib'],
    author = 'Franklin Puelles Nuñez',
    author_email = 'franklinmpg03@gmail.com',
    description = 'Paquete para el trabajo de registros acelerograficos de un suelo que actuan sobre un edificio',
    install_requires=[
        i.strip() for i in open('requirements.txt').readlines()
        ]
    )

# Si se quieren hacer pruebas usar en el promt
# python setup.py develop
# Mayor informacion en el siguiente link
# https://docs.hektorprofe.net/python/distribucion/setuptools/