import numpy as np
import cv2
from flask import Flask, render_template, send_from_directory, request
from tensorflow.keras.models import load_model
from skimage.feature import graycomatrix, graycoprops

# Konfigurasi aplikasi Flask
app = Flask(__name__, static_folder='images')

# Path model
MODEL_1_PATH = './models/best_model1.h5'  # Tanpa GLCM
MODEL_2_PATH = './models/best_model2.h5'  # Dengan GLCM

# Fungsi ekstraksi fitur GLCM
def extract_glcm_features(image):
    dists = [1, 3, 5]
    angles_deg = [0, 45, 90, 135]
    angles_rad = [np.deg2rad(angle) for angle in angles_deg]
    features = []

    for dist in dists:
        for angle in angles_rad:
            GLCM = graycomatrix(image, distances=[dist], angles=[angle], symmetric=True, normed=True)
            features.append(graycoprops(GLCM, 'energy')[0, 0])
            features.append(graycoprops(GLCM, 'correlation')[0, 0])
            features.append(graycoprops(GLCM, 'homogeneity')[0, 0])
            features.append(graycoprops(GLCM, 'contrast')[0, 0])
    
    return np.array(features)

# Fungsi preprocessing citra
def preprocess_image(image, use_glcm):
    image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (224, 224))
    img_norm = image.astype('float32') / 255.0
    img_norm = np.expand_dims(img_norm, axis=-1)
    img_input = np.expand_dims(img_norm, axis=0)
    
    if use_glcm:
        glcm_features = extract_glcm_features(image)
        return img_input, np.expand_dims(glcm_features, axis=0)
    
    return img_input, None

# Halaman utama
@app.route('/')
def home():
    return render_template('index.html')

# Halaman prediksi
@app.route('/predict')
def predict():
    return render_template('predict.html')

# Route untuk memproses gambar dan melakukan prediksi
@app.route('/result', methods=['POST'])
def predict_result():
    if request.method == 'POST':
        file = request.files['image']
        model_choice = request.form['model_choice']

        # Load model berdasarkan pilihan
        if model_choice == "model1":
            model = load_model(MODEL_1_PATH)
            use_glcm = False
        elif model_choice == "model2":
            model = load_model(MODEL_2_PATH)
            use_glcm = True
        else:
            return render_template('predict.html', error="Harap pilih model yang valid.")

        if file:
            image = file.read()
            img_input, glcm_input = preprocess_image(image, use_glcm)

            if use_glcm:
                predictions = model.predict([img_input, glcm_input])
            else:
                predictions = model.predict(img_input)

            probabilities = predictions[0]
            labels_dict = {0: "Normal", 1: "Pneumonia", 2: "Tuberkulosis"}
            predicted_class = np.argmax(probabilities)
            predicted_label = labels_dict[predicted_class]

            return render_template('result.html', prediction=predicted_label, probabilities={labels_dict[i]: prob for i, prob in enumerate(probabilities)})
        
        return render_template('result.html', error="Harap unggah file gambar yang valid.")
    

# Route untuk melayani file CSV dari folder 'data'
@app.route('/data/<path:filename>')
def serve_file(filename):
    return send_from_directory('data', filename)

# Halaman proses
@app.route('/process')
def process():
    return render_template('process.html')

# Halaman informasi
@app.route('/information')
def information():
    return render_template('information.html')

# Halaman tentang
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
