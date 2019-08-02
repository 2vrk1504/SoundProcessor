import sounddevice as sd
import numpy as np
import scipy.interpolate as sp

class SoundProcessor:

    def __init__(self, args):
        self.args = args
        self.blocksize = 1024 # int(self.samplerate * self.args.block_duration / 1000)
        self.samplerate = sd.query_devices(self.args.device, 'input')['default_samplerate']
        self.size = 2**16
        self.delay = 0.2
        self.scale = 1.2
        self.cutoff = self.samplerate/2
        self.pitch_change = False
        self.compute_H()
        
    def compute_H(self):
        self.set_H_delay()
        self.set_ideal_LPF(self.H_delay.size)
        self.H = self.H_delay * self.ideal_LPF

    def set_H_delay(self):
        if self.delay == 0:
            self.H_delay = np.ones(self.H_delay.size)
            return
        h_delay = np.zeros(self.size)
        h_delay[::int(self.samplerate*self.delay)] = 0.3**(np.arange(int(np.ceil(self.size/self.samplerate/self.delay)))) 
        self.P = len(h_delay)
        self.H_delay = np.fft.rfft( np.concatenate((h_delay, np.zeros(self.blocksize))) )

    def set_ideal_LPF(self, size):
        self.ideal_LPF = np.zeros(size)    # Actually not ideal... lol, divide by 2, because only +ve freqs
        self.ideal_LPF[0: int(self.size*self.cutoff*1./self.samplerate)] = 1

    """ Processing happens here! """
    def process_block(self, indata, frames):
        if self.pitch_change:
            x0 = indata[:, 0]
            Xf = np.fft.rfft(x0)
            iis = np.arange(Xf.size) * self.scale
            Xf2 = np.zeros(Xf.size, dtype=np.complex128)
            
            new_bin, curr_bin = 0, 0

            # f_real = sp.interp1d(iis, Xf.real, kind='cubic')
            # f_imag = sp.interp1d(iis, Xf.imag, kind='cubic')
            # Xf2 = (f_real(np.arange(Xf.size)) + 1j*f_imag(np.arange(Xf.size)))/self.scale

            while new_bin < Xf.size and curr_bin < Xf.size:
                if float(new_bin) == iis[curr_bin]:
                    Xf2[new_bin] = Xf[curr_bin]
                    new_bin += 1
                    curr_bin += 1
                elif new_bin < iis[curr_bin]:
                    Xf2[new_bin] = (((Xf[curr_bin]-Xf[curr_bin-1])*(new_bin-iis[curr_bin-1])/self.scale) + Xf[curr_bin-1])/self.scale
                    new_bin += 1
                else:
                    curr_bin += 1

            #print (Xf.size)
            outdata = np.fft.irfft(Xf2)
        else:
            x0 = np.concatenate((indata[:,0], np.zeros(self.P))) 
            y0 = np.fft.irfft(np.fft.rfft(x0) * self.H)
            y0[:self.P] = y0[:self.P] + self.buffer
            outdata = 1.5*y0[:-self.P]
            self.buffer[:] = y0[-self.P:]
        return outdata

    def start_processing(self):
        self.compute_H()
        self.buffer = np.zeros(self.P)

        self.LPF_AND_DELAY_MODE = '''\nIN LPF AND DELAY MODE\n'''
        self.PITCH_SHIFT_MODE = '''\nIN PITCH SHIFT MODE\n'''

        def callback(indata, outdata, frames, time, status):
            if status:
                text = ' ' + str(status) + ' '
                # print('\x1b[34;40m', text.center(self.args.columns, '#'),
                #       '\x1b[0m', sep='')

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
                            if self.pitch_change: 
                                self.pitch_change = False
                                print(self.LPF_AND_DELAY_MODE)
                            self.delay = float(response[1:])
                            self.compute_H()
                        elif response[0] == 'f':
                            if self.pitch_change: 
                                self.pitch_change = False
                                print(self.LPF_AND_DELAY_MODE)
                            self.cutoff = float(response[1:])
                            self.compute_H()
                        elif response[0] == 's':
                            if not self.pitch_change: 
                                self.pitch_change = True
                                print(self.PITCH_SHIFT_MODE)
                            self.scale = float(response[1:])
                    except Exception as e:
                        print(e)
                        break



        