import tensorflow as tf

# Load model .h5
model = tf.keras.models.load_model('best_model2.h5')

# Konversi ke TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Simpan ke file
with open('best_model2.tflite', 'wb') as f:
    f.write(tflite_model)
