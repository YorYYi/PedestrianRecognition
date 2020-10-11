##########################################################################################################
###########################################  FINAL MODELS  ###############################################
##########################################################################################################



class DataGeneratorFINALCrossingDetection(Sequence):
    def __init__(self, list_IDs, path_instances, n_frames, batch_size=32, dim=(128, 128, 32), n_channels=1, n_clases=1, shuffle=True, normalized=True):
        self.dim = dim
        self.batch_size = batch_size
        self.list_IDs = list_IDs
        self.n_channels = n_channels
        self.n_classes = n_clases
        self.shuffle = shuffle
        self.n_frames = n_frames
        self.normalized = normalized
        self.path_instances = path_instances
        self.on_epoch_end()

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.list_IDs))
        if self.shuffle:
            np.random.shuffle(self.indexes)

    def __data_generation(self, list_IDs_temp):

        X = np.empty((self.batch_size, self.n_frames, *self.dim, self.n_channels))
        y = np.empty(self.batch_size, dtype=float)

        for i, ID_instance in enumerate(list_IDs_temp):

            with (self.path_instances / ID_instance).open('rb') as input:
                instance = pickle.load(input)

            """Me quedo unicamente con el campo de frames de la instancia que almacena el vector de numpy con los fotograma
            de los vídeos"""
            frames = instance['frames']

            label = instance['crossing']

            #Normalización de los frames
            if self.normalized:
                frames = frames * 1 / 255

            #Se almacenan los frames ordenados y su etiqueta
            X[i, ] = frames
            y[i] = label

        return X, to_categorical(y, num_classes=self.n_classes)

    def __getitem__(self, index):

        indexes_batch = self.indexes[int(index * self.batch_size):int((index + 1) * self.batch_size)]

        #Obtengo el identificador de las instancias que van a estar en el batch index
        list_IDs_temp = [self.list_IDs[k] for k in indexes_batch]

        #LLamo a la función para generar los datos con el identificador de las instancias que forman el batch
        X, y = self.__data_generation(list_IDs_temp)

        return X, y

    def get_ID_instances_and_labels(self):

        #Obtengo el identificador de las instancias en el orden en el que son generadas
        ID_instances = [self.list_IDs[k] for k in self.indexes]

        real_labels = []
        for ID_instance in ID_instances:

            with (self.path_instances / ID_instance).open('rb') as input:
                instance = pickle.load(input)

            real_labels.append(instance['crossing'])

        return ID_instances, to_categorical(real_labels, num_classes=self.n_classes)

    def __len__(self):
        return int(np.floor(len(self.list_IDs) / self.batch_size))



"""class DataGeneratorFINALRegression(Sequence):
    def __init__(self, list_IDs, path_instances, n_frames, batch_size=32, dim=(128, 128, 32), n_channels=1, n_clases=1, shuffle=True, normalized=True):
        self.dim = dim
        self.batch_size = batch_size
        self.list_IDs = list_IDs
        self.n_channels = n_channels
        self.n_clases = n_clases
        self.shuffle = shuffle
        self.n_frames = n_frames
        self.normalized = normalized
        self.path_instances = path_instances
        self.on_epoch_end()

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.list_IDs))  
        if self.shuffle:
            np.random.shuffle(self.indexes)

    def __data_generation(self, list_IDs_temp):

        X = np.empty((self.batch_size, self.n_frames, *self.dim, self.n_channels))
        y = np.empty(self.batch_size, dtype=float)

        for i, ID_instance in enumerate(list_IDs_temp):

            with (self.path_instances / ID_instance).open('rb') as input:
                instance = pickle.load(input)

            Me quedo unicamente con el campo de frames de la instancia que almacena el vector de numpy con los fotograma
            de los vídeos
            frames = instance["frames"]

            intention_prob = instance["intention_prob"]

            #Normalización de los frames
            if self.normalized:
                frames = frames * 1 / 255

            #Se almacenan los frames ordenados y su etiqueta
            X[i, ] = frames
            y[i] = intention_prob


        return X, y

    def __getitem__(self, index):

        indexes_batch = self.indexes[int(index * self.batch_size):int((index + 1) * self.batch_size)]

        #Obtengo el identificador de las instancias que van a estar en el batch index
        list_IDs_temp = [self.list_IDs[k] for k in indexes_batch]

        #LLamo a la función para generar los datos con el identificador de las instancias que forman el batch
        X, y = self.__data_generation(list_IDs_temp)

        return X, y

    def get_ID_instances_and_real_labels(self):

        #Obtengo el identificador de las instancias en el orden en el que son generadas
        ID_instances = [self.list_IDs[k] for k in self.indexes]

        real_labels = []
        for ID_instance in ID_instances:

            with (self.path_instances / ID_instance).open('rb') as input:
                instance = pickle.load(input)

            real_labels.append(instance["intention_prob"])

        return ID_instances, real_labels

    def __len__(self):
        return int(np.floor(len(self.list_IDs) / self.batch_size))

class DataGeneratorFINALClassification(Sequence):
    def __init__(self, list_IDs, path_instances, n_frames, batch_size=32, dim=(128, 128, 32), n_channels=1, n_clases=1, shuffle=True, normalized=True):
        self.dim = dim
        self.batch_size = batch_size
        self.list_IDs = list_IDs
        self.n_channels = n_channels
        self.n_clases = n_clases
        self.shuffle = shuffle
        self.n_frames = n_frames
        self.normalized = normalized
        self.path_instances = path_instances
        self.on_epoch_end()

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.list_IDs))  
        if self.shuffle:
            np.random.shuffle(self.indexes)

    def __data_generation(self, list_IDs_temp):

        X = np.empty((self.batch_size, self.n_frames, *self.dim, self.n_channels))
        y = np.empty(self.batch_size, dtype=float)

        for i, ID_instance in enumerate(list_IDs_temp):

            with (self.path_instances / ID_instance).open('rb') as input:
                instance = pickle.load(input)

            Me quedo unicamente con el campo de frames de la instancia que almacena el vector de numpy con los fotograma
            de los vídeos
            frames = instance["frames"]

            intention_prob = instance["intention_prob"]

            if intention_prob >= 0.5:
                y[i] = 1
            else:
                y[i] = 0

            #Normalización de los frames
            if self.normalized:
                frames = frames * 1 / 255

            #Se almacenan los frames ordenados y su etiqueta
            X[i, ] = frames

        return X, y

    def __getitem__(self, index):

        indexes_batch = self.indexes[int(index * self.batch_size):int((index + 1) * self.batch_size)]

        #Obtengo el identificador de las instancias que van a estar en el batch index
        list_IDs_temp = [self.list_IDs[k] for k in indexes_batch]

        #LLamo a la función para generar los datos con el identificador de las instancias que forman el batch
        X, y = self.__data_generation(list_IDs_temp)

        return X, y

    def get_ID_instances_and_real_labels(self):

        #Obtengo el identificador de las instancias en el orden en el que son generadas
        ID_instances = [self.list_IDs[k] for k in self.indexes]

        real_labels = []
        for ID_instance in ID_instances:

            with (self.path_instances / ID_instance).open('rb') as input:
                instance = pickle.load(input)

            if instance["intention_prob"] >= 0.8:
                real_labels.append(1)
            else:
                real_labels.append(0)

        return ID_instances, real_labels

    def __len__(self):
        return int(np.floor(len(self.list_IDs) / self.batch_size))"""
