import kerastuner
from DataGenerator import DataGenerator


class MyTunerBayesian(kerastuner.tuners.BayesianOptimization):
    def run_trial(self, trial, train_ids_instances, validation_ids_instances, dim, path_instances, n_frames,
                    verbose, epochs, callbacks):

        params = {'dim': dim,
                  'path_instances': path_instances,
                  'batch_size': trial.hyperparameters.Choice('batch_size', values=[8, 16, 32, 64, 128], default=32),
                  'n_clases': 2,
                  'n_channels': 3,
                  'n_frames': n_frames,
                  'normalized': trial.hyperparameters.Boolean('normalized', default=True),
                  'shuffle': trial.hyperparameters.Boolean('shuffle', default=True),
                  'step_swaps': trial.hyperparameters.Int('step_swaps', min_value=1, max_value=int(epochs/n_frames), default=5, step=1)}

        train_generator = DataGenerator(train_ids_instances, **params)

        validation_generator = DataGenerator(validation_ids_instances, **params)

        super(MyTunerBayesian, self).run_trial(trial, train_generator, validation_data=validation_generator, verbose=verbose, epochs=epochs, callbacks=callbacks)


class MyTunerRandom(kerastuner.tuners.RandomSearch):
    def run_trial(self, trial, train_ids_instances, validation_ids_instances, dim, path_instances, n_frames):