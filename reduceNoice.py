import noisereduce as nr
import numpy as np
from scipy.io import wavfile

def reduce_noise(filepath, reduction_strength=0.5, volume=1.0):
    """Read audio data from a wav file, reduce noise and save the new audi clip to noise_reduce.wav.

    Args:
        filepath (str): Relative path to a wavfile containing the noisy clip.
        reduction_strength (float): A value between 0 and 1 describing ti what extend the noise should be reduced.
        volume(float): A value to increase the volume of the output file. Often usefull in combination with hard noise reductions.
    """
    # Load the data
    rate, data = wavfile.read(filepath)        
    data = data/1.0 
    
    # Reduce noise
    reduced_noise = nr.reduce_noise(audio_clip=data, noise_clip=data[:], prop_decrease=reduction_strength)
    
    # Write to file
    reduced_noise = reduced_noise * volume
    wavfile.write("audio_files/noise_reduce.wav", rate, reduced_noise.astype(np.dtype('i2')))

# Example of using the noise reducer:
reduce_noise("audio_files/eng.wav")