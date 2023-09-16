import math
import os.path
import time
import shutil
from datetime import datetime
import matplotlib.pyplot as plt

import joblib
from tensorflow.keras import Model, layers, optimizers

import GroundMotion_lib.deeplearning as dl

# IMPORTAR DATOS
ti = time.time()

processing_obj = dl.ProcessingObject()
processing_obj.load_important('data_3Pisos')

print (processing_obj.split_data_edi())

tf = time.time()

print(f'Se importo en {tf - ti}')
# poolLayer = layers.AvgPool1D(pool_size = 4)
# poolLayer = layers.MaxPool1D(pool_size = 4)

# MODELO DE SISMOS
input_layer_sismo = layers.Input(shape = processing_obj.shapeSuelo)

flatten_layer = layers.Flatten()(input_layer_sismo)

multi_layer_sis = layers.Dense(100, activation = 'relu')(flatten_layer)

multi_layer_sis = layers.Dense(100, activation = 'relu')(multi_layer_sis)

multi_layer_sis = layers.Dense(100, activation = 'relu')(multi_layer_sis)

multi_layer_sis = layers.Dense(500, activation = 'relu')(multi_layer_sis)

modelo_sismo = Model(inputs = input_layer_sismo, outputs = multi_layer_sis)
modelo_sismo.summary()

# MODELO DE EDIFICIOS
input_layer_edificos = layers.Input(shape = 12)
multi_layer = layers.Dense(100, activation = 'relu')(input_layer_edificos)
# MAS DE 25 PISOS

multi_layer = layers.Dense(100, activation = 'relu')(multi_layer)

multi_layer = layers.Dense(100, activation = 'relu')(multi_layer)

multi_layer = layers.Dense(500, activation = 'relu')(multi_layer)

modelo_edificios = Model(inputs = input_layer_edificos, outputs = multi_layer)
modelo_edificios.summary()

# MODELO COMBINADO

combinacion_layer = layers.concatenate((modelo_sismo.output, modelo_edificios.output))
multi_layer = layers.Dense(200, activation = 'relu')(combinacion_layer)

multi_layer = layers.Dense(200, activation = 'relu')(multi_layer)

multi_layer = layers.Dense(500, activation = 'relu')(multi_layer)

final_multi_layer = layers.Dense(math.prod(processing_obj.shapeNiveles), activation = 'relu')(multi_layer)
final_multi_layer = layers.Reshape(target_shape = processing_obj.shapeNiveles)(final_multi_layer)
modelo_combinado = Model(inputs = [input_layer_sismo, input_layer_edificos], outputs = final_multi_layer)

modelo_combinado.summary()
print('Modelo Definido \n')

continuar = input('DESEA CONTINUAR? Y/N: ')

if continuar.upper() == 'N':
    exit()

print('Creando train y test data\n')
sismo_train, sismo_test = processing_obj.split_data_suelo()
edi_train, edi_test = processing_obj.split_data_edi()
out_train, out_test = processing_obj.split_data_niv()

edi_train = edi_train.reshape(-1, 12)
edi_test = edi_test.reshape(-1, 12)

print('Seteando el compilador')

learningRate = 0.0001
learningDecay = 0.000001
callbackCantidad = 10
callbackTipo = 'last'
epocas = 50
btachSize = 50

print(f'''
    learning rate= None
	learning decay= None
    CallbackStop= {callbackTipo} con {callbackCantidad}
    epocas= {epocas}
    batch_size={btachSize}''')

# opt = optimizers.Adam(learning_rate = learningRate, decay=learningDecay )
# opt = optimizers.Adam(learning_rate = learningRate)
opt = optimizers.Adam()

modelo_combinado.compile(optimizer = opt, loss = 'MSE', metrics = ['acc'])

callback_stop = dl.CallbackStopTrain(callbackCantidad, callbackTipo)

print('empezando el fit')
historia = modelo_combinado.fit(x = [sismo_train, edi_train], y = out_train,
                                epochs = epocas, batch_size = btachSize,
                                validation_data = ((sismo_test, edi_test), out_test),
                                callbacks = [callback_stop])

print('Ploteando')
dl.plot_historia_loss(historia)
dl.plot_historia_acc(historia)
print(type(historia))

ruta_guardado = f'Modelos Tensorflow/{datetime.now().strftime("%Y.%m.%d-%H.%M")}-modelo_1_mlp'
modelo_combinado.save(ruta_guardado)
joblib.dump(historia.history,
            f'{ruta_guardado}/train_history.hst')
shutil.copy(os.path.basename(__file__),
            f'{ruta_guardado}/code.py')



index_plot_test = processing_obj.test_index[0:4]
dl.plot_edi(modelo_combinado, processing_obj, index_plot_test,
            dir_edi = 'objetos_edificios', dirrecion = 0, numero_columnas = 6)



index_plot_train = processing_obj.train_index[0:4]
dl.plot_edi(modelo_combinado, processing_obj, index_plot_train,
            dir_edi = 'objetos_edificios', dirrecion = 0, numero_columnas = 6)



#ruta_guardado_plots = f'Plots/{datetime.now().strftime("%Y.%m.%d-%H.%M")}-modelo_conv.png'
#plt.savefig(ruta_guardado_plots)

#plot1.save(ruta_guardado_plots)
#plot2.save(ruta_guardado_plots)

#[0:4]






