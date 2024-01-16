from matplotlib import pyplot as plt
from tensorflow.keras.layers import BatchNormalization, Dense, Dropout, Flatten, Rescaling
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing import image_dataset_from_directory
from keras.applications.vgg16 import VGG16
from keras.optimizers import Adam
from keras.losses import CategoricalCrossentropy


def load_images(batch_size=32, image_size=(150, 150), validation_split=0.2,
                images_dir='CT-KIDNEY-DATASET-Normal-Cyst-Tumor-Stone'):
    train_data = image_dataset_from_directory(f'{images_dir}/train', image_size=image_size,
                                              batch_size=batch_size,
                                              validation_split=validation_split,
                                              label_mode='categorical',
                                              subset='training', seed=123)

    validation_data = image_dataset_from_directory(f'{images_dir}/train', image_size=image_size,
                                                   batch_size=batch_size,
                                                   label_mode='categorical',
                                                   validation_split=validation_split,
                                                   subset='validation', seed=123)

    test_data = image_dataset_from_directory(f'{images_dir}/test',
                                             image_size=(150, 150),
                                             batch_size=32,
                                             label_mode='categorical')

    return train_data, validation_data, test_data


def assemble_model(input_shape=(150, 150, 3), num_classes=4, first_dense_neurons=512, dropout=0.5):
    vgg_model = Sequential()

    pretrained_model = VGG16(include_top=False,
                             input_shape=input_shape,
                             pooling='max', classes=num_classes,
                             weights='imagenet')

    vgg_model.add(Rescaling(1. / 255, input_shape=input_shape))
    vgg_model.add(pretrained_model)
    vgg_model.add(Flatten())
    vgg_model.add(Dense(first_dense_neurons, activation='relu'))
    vgg_model.add(BatchNormalization())
    vgg_model.add(Dropout(dropout))

    vgg_model.add(Dense(num_classes, activation='softmax'))
    pretrained_model.trainable = False

    return vgg_model


def plot_history(history):
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')

    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')

    plt.tight_layout()
    plt.show()


train_data, validation_data, test_data = load_images()
VGG_model = assemble_model()

VGG_model.compile(optimizer=Adam(0.0001),
                  loss=CategoricalCrossentropy(), metrics=["accuracy"])

history = VGG_model.fit(train_data, epochs=10,
                        validation_data=validation_data)

test_loss, test_accuracy = VGG_model.evaluate(test_data)

plot_history(history)
print(f'Test loss: {test_loss}, Test accuracy: {test_accuracy}')

VGG_model.save('kidney_diagnose.h5')