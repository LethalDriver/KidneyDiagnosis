import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from keras import Sequential
from keras.optimizers import Adam
from keras.losses import CategoricalCrossentropy
from keras.src.layers import Rescaling
from utils import load_images, plot_history
from model import assemble_kidney_classifier
from keras.applications.vgg16 import VGG16

train_data, validation_data, test_data = load_images('CT-KIDNEY-DATASET-Normal-Cyst-Tumor-Stone')

input_shape = (150, 150, 3)

pretrained_model = VGG16(include_top=False,
                         input_shape=input_shape,
                         pooling='max', classes=4,
                         weights='imagenet')

pretrained_model.trainable = False

VGG_model = Sequential([
    Rescaling(1. / 255, input_shape=(150, 150, 3)),
    pretrained_model
])

VGG_model = assemble_kidney_classifier(VGG_model, num_classes=4, first_dense_neurons=512, dropout=0.5)

VGG_model.compile(optimizer=Adam(0.0001),
                  loss=CategoricalCrossentropy(), metrics=["accuracy"])

VGG_model.summary()
history = VGG_model.fit(train_data, epochs=15,
                        validation_data=validation_data)

test_loss, test_accuracy = VGG_model.evaluate(test_data)

plot_history(history)
print(f'Test loss: {test_loss}, Test accuracy: {test_accuracy}')

VGG_model.save('kidney_diagnose.h5')

"""
Epoch 15/15
249/249 [==============================] - 29s 116ms/step - loss: 0.0708 - accuracy: 0.9828 
- val_loss: 0.0274 - val_accuracy: 0.9965
78/78 [==============================] - 15s 175ms/step - loss: 0.0323 - accuracy: 0.9940
Test loss: 0.032348066568374634, Test accuracy: 0.993968665599823
"""