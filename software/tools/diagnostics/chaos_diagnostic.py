#!/usr/bin/env python3
"""
chaos_diagnostic.py
Professional chaos diagnostic tool for RC oscillator circuits
Performance-optimized with compact output
"""

import sys
from pathlib import Path

# Add ADC adapter to Python path
adapter_path = Path(__file__).parent.parent.parent / "adapters" / "adc-adapters" / "waveshare-ads1263"
sys.path.insert(0, str(adapter_path))

import ADS1263
import numpy as np
import time
from scipy import signal
from scipy.fft import fft, fftfreq
import warnings
warnings.filterwarnings('ignore')

# Configuration
REF = 5.0                # Reference voltage (V)
SAMPLE_DURATION = 3      # Sampling duration (seconds)
CHANNEL_VCE1 = 3         # ADC channel (IN3)
EXPECTED_SAMPLES = 35000 # Expected samples (~11 kHz × 3s)

def raw_to_voltage(raw, ref=REF):
    """
    Convert raw ADC values to voltage using vectorized operations
    
    Args:
        raw: NumPy array of raw ADC values (32-bit signed)
        ref: Reference voltage (default: 5.0V)
    
    Returns:
        NumPy array of voltage values
    """
    mask = (raw >> 31) == 1
    result = np.zeros_like(raw, dtype=float)
    result[mask] = -(ref * 2 - raw[mask] * ref / 0x80000000)
    result[~mask] = raw[~mask] * ref / 0x7FFFFFFF
    return result

def capture_data(duration=SAMPLE_DURATION):
    """
    Capture ADC data with optimized performance
    
    Args:
        duration: Sampling duration in seconds
    
    Returns:
        tuple: (data array, sampling frequency) or (None, None) on error
    """
    
    ADC = ADS1263.ADS1263()
    if ADC.ADS1263_init_ADC1('ADS1263_38400SPS') == -1:
        print("❌ ADC initialization failed!")
        return None, None
    
    # Configure ADC
    ADC.ADS1263_SetMode(0)  # Single-ended mode
    ADC.ADS1263_SetChannal(CHANNEL_VCE1)
    
    # Pre-allocate array for performance
    raw_data = np.zeros(EXPECTED_SAMPLES, dtype=np.int32)
    
    print(f"\n⚡ Capturing {duration}s of data...", end='', flush=True)
    
    start = time.time()
    idx = 0
    
    try:
        # Fast capture loop
        while idx < EXPECTED_SAMPLES and (time.time() - start) < duration:
            ADC.ADS1263_WaitDRDY()
            raw_data[idx] = ADC.ADS1263_Read_ADC_Data()
            idx += 1
        
        elapsed = time.time() - start
        
    except KeyboardInterrupt:
        elapsed = time.time() - start
        print(" Interrupted")
    finally:
        ADC.ADS1263_Exit()
    
    # Trim array and convert to voltage
    raw_data = raw_data[:idx]
    data = raw_to_voltage(raw_data)
    fs = idx / elapsed
    
    print(f" ✓")
    print(f"   {idx} samples @ {fs:.0f} Hz | VCE1: {np.min(data):.3f}V - {np.max(data):.3f}V")
    
    return data, fs

def analyze_chaos(data, fs):
    """
    Analyze signal for chaotic behavior using multiple metrics
    
    Metrics:
    - Spectral complexity (frequency domain)
    - Power distribution (energy concentration)
    - Aperiodicity (autocorrelation)
    - Dynamic range (signal variation)
    
    Args:
        data: Signal data array
        fs: Sampling frequency (Hz)
    
    Returns:
        int: Chaos score (0-100)
    """
    
    # Basic statistics
    mean = np.mean(data)
    std = np.std(data)
    p2p = np.max(data) - np.min(data)
    
    print(f"\n📊 Signal: Mean {mean:.3f}V | Std {std:.3f}V | P2P {p2p:.3f}V")
    
    # Signal quality check
    if p2p < 0.3:
        print("❌ Signal too weak! Adjust potentiometer to center position.\n")
        return 0
    
    # ========================================================================
    # FFT Analysis
    # ========================================================================
    n = len(data)
    yf = fft(data - mean)
    xf = fftfreq(n, 1/fs)[:n//2]
    power = 2.0/n * np.abs(yf[:n//2])
    
    # Find dominant frequency
    dominant_idx = np.argmax(power)
    dominant_freq = xf[dominant_idx]
    
    # Peak detection
    threshold = np.max(power) * 0.1
    peaks, _ = signal.find_peaks(power, height=threshold)
    
    # Power concentration in top 3 frequencies
    total_power = np.sum(power)
    top3_power = np.sum(np.sort(power)[-3:]) / total_power
    
    print(f"🔍 Spectrum: {dominant_freq:.0f} Hz dominant | {len(peaks)} peaks | Top-3: {top3_power*100:.1f}%")
    
    # ========================================================================
    # Autocorrelation Analysis
    # ========================================================================
    data_norm = data - mean
    max_lag = min(2000, len(data)//4)
    autocorr = np.correlate(data_norm, data_norm, mode='full')
    autocorr = autocorr[len(data)-1:len(data)-1+max_lag]
    autocorr = autocorr / autocorr[0]
    
    # Find decay length (first crossing below 0.5)
    decay = np.where(autocorr < 0.5)[0]
    decay_len = decay[0] if len(decay) > 0 else max_lag
    
    # Count secondary peaks (periodicity indicator)
    sec_peaks, _ = signal.find_peaks(autocorr[10:], height=0.3)
    
    print(f"🔄 Autocorr: Decay {decay_len} samples ({decay_len/fs*1000:.1f}ms) | Sec. peaks: {len(sec_peaks)}")
    
    # ========================================================================
    # CHAOS SCORE CALCULATION
    # ========================================================================
    
    # 1. Spectral Complexity (0-30 points)
    #    Optimal: 500-2000 peaks (broadband chaos)
    if len(peaks) < 100:
        score_spectral = (len(peaks) / 100) * 15
    elif len(peaks) < 500:
        score_spectral = 15 + ((len(peaks) - 100) / 400) * 10
    elif len(peaks) <= 2000:
        score_spectral = 30  # Optimal
    else:
        score_spectral = max(20, 30 - ((len(peaks) - 2000) / 500) * 5)
    
    # 2. Power Distribution (0-25 points)
    #    Optimal: Distributed power (low concentration)
    if top3_power > 0.7:
        score_power = 0      # Too concentrated = periodic
    elif top3_power > 0.1:
        score_power = 5      # Still somewhat concentrated
    elif top3_power >= 0.001:
        score_power = 25     # Optimal distribution
    else:
        score_power = 15     # Too flat = white noise
    
    # 3. Aperiodicity (0-25 points)
    #    Optimal: Fast decay, no secondary peaks
    if len(sec_peaks) == 0:
        score_autocorr = 25  # Perfect aperiodicity
    elif len(sec_peaks) <= 3:
        score_autocorr = 20  # Acceptable
    elif len(sec_peaks) <= 7:
        score_autocorr = 10  # Somewhat periodic
    else:
        score_autocorr = 0   # Strongly periodic
    
    # 4. Dynamic Range (0-20 points)
    #    Optimal: Std = 0.15-0.20V
    if std < 0.05:
        score_dynamic = (std / 0.05) * 5
    elif std < 0.15:
        score_dynamic = 5 + ((std - 0.05) / 0.10) * 10
    elif std <= 0.20:
        score_dynamic = 20   # Optimal
    elif std <= 0.25:
        score_dynamic = 15   # Still acceptable
    else:
        score_dynamic = 10   # Possibly too noisy
    
    # Total score (0-100)
    total_score = score_spectral + score_power + score_autocorr + score_dynamic
    
    # ========================================================================
    # OUTPUT
    # ========================================================================
    print(f"\n{'─' * 70}")
    print("  CHAOS SCORE")
    print(f"{'─' * 70}")
    
    def score_bar(score, max_score):
        """Generate visual score bar"""
        filled = int(score / max_score * 20)
        return '█' * filled + '░' * (20 - filled)
    
    print(f"  Spectral Complexity    {score_spectral:>5.0f}/30  {score_bar(score_spectral, 30)}")
    print(f"  Power Distribution     {score_power:>5.0f}/25  {score_bar(score_power, 25)}")
    print(f"  Aperiodicity           {score_autocorr:>5.0f}/25  {score_bar(score_autocorr, 25)}")
    print(f"  Dynamic Range          {score_dynamic:>5.0f}/20  {score_bar(score_dynamic, 20)}")
    
    print(f"\n  ╔════════════════════════════════════╗")
    print(f"  ║  TOTAL: {total_score:>5.0f} / 100             ║")
    print(f"  ╚════════════════════════════════════╝\n")
    
    # ========================================================================
    # ASSESSMENT & RECOMMENDATIONS
    # ========================================================================
    
    if total_score >= 85:
        print("  ⭐⭐⭐ PERFECT CHAOS! ⭐⭐⭐")
        print("  🎯 SWEET SPOT FOUND - Remember this position!")
    
    elif total_score >= 70:
        print("  🎯 STRONG CHAOS!")
        if score_autocorr < 20:
            print("  💡 Tip: Turn slightly toward center → reduce periodicity")
        elif score_spectral < 25:
            print("  💡 Tip: Turn slightly right → increase complexity")
        else:
            print("  💡 Nearly perfect!")
    
    elif total_score >= 50:
        print("  ⚠️  WEAK CHAOS / TRANSITION REGION")
        if len(sec_peaks) > 5:
            print("  💡 Tip: Turn toward center → reduce periodicity")
        else:
            print("  💡 Tip: Continue adjusting for higher score")
    
    elif total_score >= 20:
        print("  ⭕ PERIODIC / BIFURCATION EDGE")
        if dominant_freq < 1000:
            print("  💡 Tip: Turn left (increase frequency)")
        else:
            print("  💡 Tip: Turn right")
    
    else:
        print("  ❌ NO CHAOS - Too weak or too stable")
        print("  💡 Tip: Turn to center position (~50%)")
    
    print()
    
    return total_score

def main():
    """Main execution function"""
    
    print("\n╔═══════════════════════════════════════════════════════════════════╗")
    print("║            RC OSCILLATOR - CHAOS DIAGNOSTIC TOOL                  ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    
    # Capture data
    data, fs = capture_data(SAMPLE_DURATION)
    
    if data is None or len(data) < 1000:
        print("\n❌ Data capture failed\n")
        return
    
    # Analyze for chaotic behavior
    analyze_chaos(data, fs)
    
    print("─" * 70)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()