import sys
import os
sys.path.append('/usr/local/lib/python3.7/site-packages')

import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt

fs = 44100
duration = 10 # seconds
blocksize = 8192
peak_thresh = 0.001
freq_space = np.linspace(0, fs/2, blocksize//2 + 1)

sd.default.samplerate = fs
sd.default.channels = 1

note_map = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
frequency_map = [
		130.81, 146.83, 164.81, 174.61, 196.00, 220.00, 246.94,			# 3rd octave
		261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88,			# 4th octave
		523.25, 587.33, 659.26, 698.46, 783.99, 880.00, 987.77,			# 5th octave
		1046.50, 1174.66, 1318.51, 1396.91, 1567.98, 1760.00, 1975.53, 	# 6th octave
		2093.00, 2349.32, 2637.02, 2793.82, 3135.96, 3520.00, 3951.06	# 7th octave 
	]

def interpolator(spectrum, sf):
	iis = np.arange(spectrum.size) * sf
	spectrum2 = np.zeros(spectrum.size, dtype=np.complex128)
	new_bin, curr_bin = 0, 0
	while new_bin < spectrum.size and curr_bin < spectrum.size:
		if float(new_bin) == iis[curr_bin]:
			spectrum2[new_bin] = spectrum[curr_bin]
			new_bin += 1
			curr_bin += 1
		elif new_bin < iis[curr_bin]:
			spectrum2[new_bin] = (((spectrum[curr_bin]-spectrum[curr_bin-1])*(new_bin-iis[curr_bin-1])/sf) + spectrum[curr_bin-1])/sf
			new_bin += 1
		else:
			curr_bin += 1
	return spectrum2

def autotune(indata):
	spectrum = np.fft.rfft(indata)
	peak_bin = np.argmax(spectrum)

	if spectrum[peak_bin]/blocksize > peak_thresh: # normalized peak
		peak_freq = peak_bin*fs/blocksize
		closest_freq_index = np.argmin(abs(frequency_map-peak_freq))
		sf = frequency_map[closest_freq_index]/peak_freq	# frequency dilation scaling factor
		print('in', sf, note_map[closest_freq_index%7]+str(closest_freq_index//7+3))

		# harmonizer
		sf1 = frequency_map[closest_freq_index + 2]/peak_freq
		sf2 = frequency_map[closest_freq_index + 4]/peak_freq
		outdata = 0.5*np.fft.irfft(interpolator(spectrum, sf)) + 0.25*np.fft.irfft(interpolator(spectrum, sf1)) + 0.25*np.fft.irfft(interpolator(spectrum, sf2))

	else:
		outdata = indata
	return outdata


print('Recording input (10s)...')
myrecording = sd.rec(int(duration * fs))
sd.wait()
print('Recording complete!')




print('Starting autotune...')
autotune_playback = np.zeros(int(duration * fs))
block_start = 0
while block_start <= duration * fs:
	autotune_playback[block_start: block_start+blocksize] = autotune(myrecording[block_start: block_start+blocksize].flatten())
	block_start += blocksize

print('Autotuning done...')
print('Playing processed audio....')
sd.play(2*autotune_playback)
sd.wait()
