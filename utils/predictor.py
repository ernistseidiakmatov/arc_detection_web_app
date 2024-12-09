import numpy as np
import pandas as pd
import tensorflow as tf
from scipy import stats
from sklearn.preprocessing import StandardScaler 
import joblib

class SignalPredictor:
    def __init__(self, model_type, model=None):
        self.model_type = model_type
        self.model = model
        self.interpreter = None
        self.input_details = None
        self.ouput_details = None


    def load_model(self):
        
        if self.model_type == "lstm":
            model_dir = "models/tflite_LSTM_v0.3.tflite"
        else:
            model_dir = "models/tflite_MLP_v0.3.tflite"
        interpreter = tf.lite.Interpreter(model_path=model_dir)
        interpreter.allocate_tensors()
        self.interpreter = interpreter
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict(self, signal):
        if signal.shape != (1, 9):
            signal = signal.reshape(1, 9)
        
        if len(signal.shape) == 2:
            signal = np.expand_dims(signal, axis=0)
        
        signal = signal.astype(np.float32)
        self.interpreter.set_tensor(self.input_details[0]['index'], signal)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        output_data = np.squeeze(output_data)
        predicted_class = np.argmax(output_data)
        probabilities = output_data
        
        return predicted_class, probabilities


def calc_features(signal):
    # Remove DC offset
    offset = np.mean(signal)
    signal_no_dc = signal - offset

    # Calculate time-domain features
    mean = offset  # The original mean before offset removal
    std = np.std(signal_no_dc)
    var = np.var(signal_no_dc)
    skewness = stats.skew(signal_no_dc)
    kurtosis = stats.kurtosis(signal_no_dc)
    peak_to_peak = np.ptp(signal_no_dc)
    rms = np.sqrt(np.mean(np.square(signal_no_dc)))

    # Frequency-domain features
    N = len(signal)
    fft_result = np.fft.fft(signal)
    
    # Calculate magnitude (similar to C code)
    fft_vals = np.abs(fft_result) / N  # Divide by N as in your C code
    
    # Only keep the first half (positive frequencies)
    fft_vals = fft_vals[:N//2 + 1]
    
    # Calculate frequencies
    freqs = np.fft.fftfreq(N, d=1/150000)[:N//2 + 1]
    
    # Find dominant frequency (ignoring DC component)
    dominant_freq = freqs[np.argmax(fft_vals[1:]) + 1]

    power = np.square(fft_vals)
    power = power / sum(power)
    spectral_entropy = -np.sum(power * np.log2(power + 1e-12))

    return [mean, std, var, skewness, kurtosis, peak_to_peak, rms, dominant_freq, spectral_entropy]
    

def get_dataset(arc="datasets/dummy_data/arc.csv",  non_arc="datasets/dummy_data/non-arc.csv", sep=' '):
    arc = pd.read_csv(arc, sep=sep, header=None)
    non_arc = pd.read_csv(non_arc, sep=sep, header=None)

    return np.array(pd.concat([arc, non_arc], ignore_index=True))


# just apply on signle signal input
def get_single_signal_feature(signal):
    features = calc_features(signal)
    return np.array(features)

def get_scaler():
    return joblib.load("models/std_scaler.bin")