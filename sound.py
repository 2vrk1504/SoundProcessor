#!/usr/bin/env python3
import argparse
from sound_processor import *

usage_line = \
'''Press \'Q\' or \'q\' to quit
To change cutoff frequency: \'f<cutoff in Hz>\', eg: f5000
To change delay: \'d<delay in sec>\', eg: d0.2
For pitch-shift: \'s<scale of pitch>\', eg: s0.8 or s1.5
Defaults: cutoff = 22050Hz\tdelay = 0.2sec
Have fun!!'''


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text
      
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-l', '--list-devices', action='store_true',
                    help='list audio devices and exit')
parser.add_argument('-b', '--block-duration', type=float,
                    metavar='DURATION', default=50,
                    help='block size (default %(default)s milliseconds)')
parser.add_argument('-d', '--device', type=int_or_str,
                    help='input device (numeric ID or substring)')
parser.add_argument('-g', '--gain', type=float, default=10,
                    help='initial gain factor (default %(default)s)')
parser.add_argument('-r', '--range', type=float, nargs=2,
                    metavar=('LOW', 'HIGH'), default=[100, 2000],
                    help='frequency range (default %(default)s Hz)')
args = parser.parse_args()

low, high = args.range
if high <= low:
    parser.error('HIGH must be greater than LOW')

try:   
    import sounddevice as sd
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
        
    print(usage_line)
    sound_processor = SoundProcessor(args)
    sound_processor.start_processing()

except KeyboardInterrupt:
    parser.exit('Interrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
