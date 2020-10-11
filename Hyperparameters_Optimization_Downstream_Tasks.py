#LIMITAR CPU AL 45%
import os
import tensorflow as tf
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="0"
config = tf.compat.v1.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.45

#Se carga el fichero de configuración
import yaml

with open('config.yaml', 'r') as file_descriptor:
    config = yaml.load(file_descriptor, Loader=yaml.FullLoader)

"""Inicialización de los generadores de números aleatorios. Se hace al inicio del codigo para evitar que el importar
otras librerias ya inicializen sus propios generadores"""

if not config['Keras_Tuner']['random']:

    SEED = config['Keras_Tuner']['seed']
    from numpy.random import seed
    seed(SEED)
    import tensorflow as tf
    tf.random.set_seed(SEED)
    from random import seed
    seed(SEED)

#############################################SOLUCIONAR EL ERROR DE LA LIBRERIA CUDNN###################################
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

configProto = ConfigProto()
configProto.gpu_options.allow_growth = True
session = InteractiveSession(config=configProto)

########################################################################################################################

import HyperModels_Pretext_Tasks
from FuncionesAuxiliares import read_instance_file_txt

from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.callbacks import ReduceLROnPlateau
from tensorflow.keras.callbacks import TensorBoard

import Tuners_Pretext_Tasks

from kerastuner.tuners import BayesianOptimization, Hyperband, RandomSearch

import pickle

#import logging

from os.path import join

import time

import DataGenerators_Pretext_Tasks

from pathlib import Path

import json













# AÑADIR A ESTOS DIRECTORIOS EL MODELO FINAL PARA EL CUÁL SE ESTA CALCULANDO

path_output_results_CL = Path(
    join(config['Keras_Tuner']['path_dir_results'], dataset, 'Transfer_Learning', pretext_task, tuner_type, model_name,
         'Classification_Layer'))

path_output_results_FT = Path(
    join(config['Keras_Tuner']['path_dir_results'], dataset, 'Transfer_Learning', pretext_task, tuner_type, model_name,
         'Fine_Tuning'))

path_output_hyperparameters_CL = Path(
    join(config['Keras_Tuner']['path_hyperparameters'], dataset, 'Transfer_Learning', pretext_task, tuner_type,
         model_name, 'Classification_Layer'))

path_output_hyperparameters_FT = Path(
    join(config['Keras_Tuner']['path_hyperparameters'], dataset, 'Transfer_Learning', pretext_task, tuner_type,
         model_name, 'Fine_Tuning'))

path_output_results_CL.mkdir(parents=True, exist_ok=True)

path_output_results_FT.mkdir(parents=True, exist_ok=True)

path_output_hyperparameters_CL.mkdir(parents=True, exist_ok=True)

path_output_hyperparameters_FT.mkdir(parents=True, exist_ok=True)

path_weights = config['Keras_Tuner']['Transfer_Learning']['path_weights_conv_layers']

if pretext_task == 'Shuffle' and model_name == 'CONV3D' and type_model == 'Crossing-detection':
    hypermodel_cl = HyperModels_Pretext_Tasks.HyperModel_FINAL_Shuffle_CONV3D_CrossingDetection_CL(
        input_shape=(n_frames, dim[0], dim[1], 3), num_classes=num_classes, path_weights=path_weights)

if tuner_type == 'Random_Search':

    if type_model == 'Crossing-detection':
        tuner = Tuners_Pretext_Tasks.TunerRandomFINALCrossingDetection(
            hypermodel_cl,
            objective=config['Keras_Tuner']['tuner']['objetive'],
            seed=config['Keras_Tuner']['tuner']['seed'],
            max_trials=config['Keras_Tuner']['tuner']['max_trials'],
            executions_per_trial=config['Keras_Tuner']['tuner']['executions_per_trial'],
            directory=path_output_results_CL,
            project_name=project_name,
            overwrite=False
        )

elif tuner_type == 'HyperBand':

    if type_model == 'Crossing-detection':
        tuner = Tuners_Pretext_Tasks.TunerHyperBandFINALCrossingDetection(
            hypermodel_cl,
            objective=config['Keras_Tuner']['tuner']['objetive'],
            seed=config['Keras_Tuner']['tuner']['seed'],
            max_epochs=config['Keras_Tuner']['tuner']['max_epochs'],
            executions_per_trial=config['Keras_Tuner']['tuner']['executions_per_trial'],
            directory=path_output_results_CL,
            project_name=project_name,
            overwrite=False
        )

else:

    if type_model == 'Crossing-detection':
        tuner = Tuners_Pretext_Tasks.TunerBayesianFINALCrossingDetection(
            hypermodel_cl,
            objective=config['Keras_Tuner']['tuner']['objetive'],
            seed=config['Keras_Tuner']['tuner']['seed'],
            max_trials=config['Keras_Tuner']['tuner']['max_trials'],
            num_initial_points=config['Keras_Tuner']['tuner']['num_initial_points'],
            directory=path_output_results_CL,
            project_name=project_name,
            overwrite=False
        )

earlystopping = EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=1, mode='min',
                              restore_best_weights=True)

reducelronplateau = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, verbose=1, mode='min',
                                      min_delta=0.0001, cooldown=0, min_lr=0)

# !!!!!!PONER reducelronplateau COMO CALLBACKS Y AJUSTAR SUS HIPERPARÁMETROS!!!!!!!!!!!!!!

tuner.search_space_summary()

start_time = time.time()

tuner.search(train_ids_instances, validation_ids_instances, dim, path_instances, n_frames, 1, epochs,
             [earlystopping, reducelronplateau])

stop_time = time.time()

elapsed_time = stop_time - start_time

tuner.results_summary()

best_hp = tuner.get_best_hyperparameters()[0].values

# Se almacena el tuner en un fichero binario
with (path_output_results_CL / project_name / 'tuner.pkl').open('wb') as file_descriptor:
    pickle.dump(tuner, file_descriptor)

with (path_output_results_CL / project_name / 'search_time.txt').open('w') as filehandle:
    filehandle.write("Tiempo de busqueda: %f\n" % elapsed_time)

# Se guardan los hiperparámetros
with (path_output_hyperparameters_CL / (project_name + '.json')).open('w') as filehandle:
    json.dump(best_hp, filehandle)

# Fine Tuning

if pretext_task == 'Shuffle' and model_name == 'CONV3D' and type_model == 'Crossing-detection':
    hypermodel_ft = HyperModels_Pretext_Tasks.HyperModel_FINAL_Shuffle_CONV3D_CrossingDetection_FT(
        input_shape=(n_frames, dim[0], dim[1], 3), num_classes=num_classes, path_weights=path_weights,
        hyperparameters=best_hp)

if tuner_type == 'Random_Search':

    tuner = RandomSearch(
        hypermodel_ft,
        objective=config['Keras_Tuner']['tuner']['objetive'],
        seed=config['Keras_Tuner']['tuner']['seed'],
        max_trials=config['Keras_Tuner']['tuner']['max_trials'],
        executions_per_trial=config['Keras_Tuner']['tuner']['executions_per_trial'],
        directory=path_output_results_FT,
        project_name=project_name,
        overwrite=False
    )

elif tuner_type == 'HyperBand':

    tuner = Hyperband(
        hypermodel_ft,
        objective=config['Keras_Tuner']['tuner']['objetive'],
        seed=config['Keras_Tuner']['tuner']['seed'],
        max_epochs=config['Keras_Tuner']['tuner']['max_epochs'],
        executions_per_trial=config['Keras_Tuner']['tuner']['executions_per_trial'],
        directory=path_output_results_FT,
        project_name=project_name,
        overwrite=False
    )

else:

    tuner = BayesianOptimization(
        hypermodel_ft,
        objective=config['Keras_Tuner']['tuner']['objetive'],
        seed=config['Keras_Tuner']['tuner']['seed'],
        max_trials=config['Keras_Tuner']['tuner']['max_trials'],
        num_initial_points=config['Keras_Tuner']['tuner']['num_initial_points'],
        directory=path_output_results_FT,
        project_name=project_name,
        overwrite=False
    )

params = {
    'dim': dim,
    'path_instances': path_instances,
    'batch_size': best_hp['batch_size'],
    'n_clases': num_classes,
    'n_channels': 3,
    'n_frames': n_frames,
    'normalized': best_hp['normalized'],
    'shuffle': best_hp['normalized'],
}

if type_model == 'Crossing-detection':
    train_generator = DataGenerators_Pretext_Tasks.DataGeneratorFINALCrossingDetection(train_ids_instances, **params)
    validation_generator = DataGenerators_Pretext_Tasks.DataGeneratorFINALCrossingDetection(validation_ids_instances, **params)

earlystopping = EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=1, mode='min',
                              restore_best_weights=True)

reducelronplateau = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, verbose=1, mode='min',
                                      min_delta=0.0001, cooldown=0, min_lr=0)

tuner.search_space_summary()

start_time = time.time()

tuner.search(x=train_generator, validation_data=validation_generator, epochs=epochs,
             callbacks=[earlystopping, reducelronplateau])

stop_time = time.time()

elapsed_time = stop_time - start_time

tuner.results_summary()

best_hp = tuner.get_best_hyperparameters()[0].values

# Se almacena el tuner en un fichero binario
with (path_output_results_FT / project_name / 'tuner.pkl').open('wb') as file_descriptor:
    pickle.dump(tuner, file_descriptor)

with (path_output_results_FT / project_name / 'search_time.txt').open('w') as filehandle:
    filehandle.write("Tiempo de busqueda: %f\n" % elapsed_time)

# Se guardan los hiperparámetros
with (path_output_hyperparameters_FT / (project_name + '.json')).open('w') as filehandle:
    json.dump(best_hp, filehandle)