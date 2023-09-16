from setuptools import setup

desc = 'Paquete con funciones utiles para la edicion de codigos de OpenSees,'
desc += 'y textos en generales. Como registros sismicos'

setup(
    name = 'libreria_OpenSees',
    version = '2.0.1',
    description = desc,
    author = 'Franklin Puelles Nuñez',
    author_email = 'franklinmpg03@gmail.com',
    packages = ['libreria_OpenSees'],
    install_requires = [
        i.strip() for i in open('requirements.txt').readlines()
        ]
    )

# Si se quieren hacer pruebas usar en el promt
# python setup.py develop
# Mayor informacion en el siguiente link
# https://docs.hektorprofe.net/python/distribucion/setuptools/


# Para instalar ir a la carpeta con cmd y ejecutar los siguientes comandos
# pip install (nombre del paquete,'libreria_OpenSees')
# pip3 install (nombre del paquete,'libreria_OpenSees')

# Para desinstalar
# pip3 uninstall nombre libreria
