import subprocess
import os

Directorio= os.getcwd()

## subprocess.run(['C:/Users/Franklin/AppData/Local/Programs/Python/Python38-32/python','-c',"print('hola mundo')"] )


subprocess.run(['python','setup.py','sdist'], shell=True)






##################################INSTALL#######################################


Version='1.12'
Paquete='libreria_OpenSees-{}.tar.gz'.format(Version)

Path=Directorio+'/dist/'+Paquete


subprocess.run(['pip','install',Path], shell=True)





# #instal en anaconda


# subprocess.run(['C:/Users/Franklin/anaconda3/Scripts/activate.bat C:/Users/Franklin/anaconda3'],
# 	shell=True)
