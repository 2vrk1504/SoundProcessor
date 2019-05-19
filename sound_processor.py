import sounddevice as sd
import numpy as np

class SoundProcessor:

    def __init__(self, args):
        self.args = args
        self.blocksize = 1024 #int(samplerate * self.args.block_duration / 1000)
        self.samplerate = sd.query_devices(self.args.device, 'input')['default_samplerate']
        self.size = 2**16
        self.delay = 0.2
        self.cutoff = self.samplerate/2
        
    def compute_H(self):
        if self.delay == 0:
            self.H_delay = 1 * self.ideal_LPF
            return
        self.h_delay = np.zeros(self.size)
        self.h_delay[::int(self.samplerate*self.delay)] = 0.3**(np.arange(int(np.ceil(2**16/self.samplerate/self.delay)))) 
        self.P = len(self.h_delay)
        self.H_delay = np.fft.rfft( np.concatenate((self.h_delay, np.zeros(self.blocksize))) )

        # LPF
        self.ideal_LPF = np.zeros(self.H_delay.size)    # Actually not ideal... lol
        self.ideal_LPF[0: int(self.size*self.cutoff*1./self.samplerate)] = 1
        self.H_delay = self.H_delay * self.ideal_LPF
    

    """ Processing happens here! """
    def process_block(self, indata, frames):
        x0 = np.concatenate((indata[:,0], np.zeros(self.P))) 
        y0 = np.fft.irfft(np.fft.rfft(x0) * self.H_delay)
        y0[:self.P] = y0[:self.P] + self.buffer
        outdata = 1.5*y0[:-self.P]
        self.buffer[:] = y0[-self.P:]
        return outdata

    def start_processing(self):
        self.compute_H()
        self.buffer = np.zeros(self.P)

        def callback(indata, outdata, frames, time, status):
            if status:
                text = ' ' + str(status) + ' '
                print('\x1b[34;40m', text.center(self.args.columns, '#'),
                      '\x1b[0m', sep='')

            if str(status) != 'input underflow':
                outdata[:, 0] = self.process_block(indata, frames)

        with sd.Stream(device=self.args.device, channels=1, callback=callback,
                            blocksize=self.blocksize,
                            samplerate=self.samplerate):
            while True:
                response = input()
                if response in ('q', 'Q'):
                    break
                else:
                    try:
                        if response[0] == 'd':
                            self.delay = float(response[1:])
                            self.compute_H()
                        elif response[0] == 'f':
                            self.cutoff = float(response[1:])
                            self.compute_H()
                    except Exception as e:
                        print(e)
                        break



        