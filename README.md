# SoundProcessor

## Description
A basic real-time digital sound processor, which can do the follows on mic input:
1. Add an echo/delay effect
2. Can Low Pass Filter
3. Can modify pitch of sound

Also, a post-processing Auto-Tune feature.
It corrects sound recorded by mic input to fit the C Major scale.
Record your voice and have fun. 

## Dependencies
- numpy
- sounddevice

## How to use:
1. Install `numpy` and `sounddevice`
2. Download this repository and change directory to the repository's directory.
3. Running the program
    1. `python3 sound.py` for real-time sound processing
    2. `python3 auto_tune_Test.py` for Auto-Tune functionality.
4. Make sure to provide Microphone and Speaker access to the program.

Note: Please use headphones so that the mic does not catch the output of the program. Else it can lead to positive feedback shrieks.
