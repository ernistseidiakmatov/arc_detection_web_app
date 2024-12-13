import numpy as np
from scipy import stats
from scipy.signal import welch
import json


def calc_signal_stats_avg(csv_file):
   
    signals = np.loadtxt(csv_file, delimiter=',')
    
    offset = np.mean(signals, axis=1, keepdims=True)
    signals_no_dc = signals - offset
    
    # Time-domain features
    mean = offset.ravel()  # More efficient than squeeze()
    std = np.std(signals_no_dc, axis=1)
    var = np.square(std)  # Faster than np.var()
    skewness = stats.skew(signals_no_dc, axis=1)
    kurtosis = stats.kurtosis(signals_no_dc, axis=1)
    peak_to_peak = np.ptp(signals_no_dc, axis=1)
    rms = np.sqrt(np.mean(np.square(signals_no_dc), axis=1))
    
    # Frequency-domain features
    N = signals.shape[1]
    fft_result = np.fft.rfft(signals_no_dc)  # Use rfft for real input
    fft_vals = np.abs(fft_result) / N
    
    freqs = np.fft.rfftfreq(N, d=1/150000)
    dominant_freq = freqs[np.argmax(fft_vals[:, 1:], axis=1) + 1]
    
    power = np.square(fft_vals)
    power /= np.sum(power, axis=1, keepdims=True)
    spectral_entropy = -np.sum(power * np.log2(power + 1e-12), axis=1)
    
    # Calculate averages
    feature_names = ['mean', 'std', 'var', 'skewness', 'kurtosis', 'peak_to_peak', 'rms', 'dominant_freq', 'spectral_entropy']
    avg_features = np.mean([mean, std, var, skewness, kurtosis, peak_to_peak, rms, dominant_freq, spectral_entropy], axis=1)
    # Create results dictionary
    avg_stats = dict(zip(feature_names, np.round(avg_features, 4)))
    avg_stats["number of samples"] = len(signals)
    
    return avg_stats

def calc_signal_stats(csv_file):
    # Remove DC offset
    signal = np.loadtxt(csv_file, delimiter=',')
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

    feature_names = ["mean", "std", "var", "skewness", "kurtosis", "peak_to_peak", "rms", "dominant_freq", "spectral_entropy"]
    avg_features = [mean, std, var, skewness, kurtosis, peak_to_peak, rms, dominant_freq, spectral_entropy]
    avg_stats = dict(zip(feature_names, np.round(avg_features, 4)))
    avg_stats["number of samples"] = 1
    return avg_stats