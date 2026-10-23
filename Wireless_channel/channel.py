import numpy as np

def AWGN(signal, snr_db):
    snr_linear = 10**(snr_db / 10)
    Pn = 1 / snr_linear           # chuẩn hóa Eb = 1
    sigma = np.sqrt(Pn / 2)
    noise = sigma * np.random.randn(len(signal)) + 1j * sigma * np.random.randn(len(signal))
    return signal + noise, Pn       # trả về cả noise power

def Rayleigh_fading(signal, snr_db):
    h_real = np.random.normal(0, 1/np.sqrt(2), len(signal))
    h_imag = np.random.normal(0, 1/np.sqrt(2), len(signal))
    h = h_real + 1j * h_imag

    y, N0 = AWGN(signal * h, snr_db)

    # --- MMSE Equalizer ---
    x_hat = np.conj(h) / (np.abs(h)**2 + N0) * y
   
    return x_hat

def compute_ber(tx_bits, rx_bits):
    return np.mean(tx_bits != rx_bits)

class QAM:
    def __init__(self,M):
        self.M = M
        self.k = int(np.log2(M))
        self.constellation = self._generate_constellation()

    def _generate_constellation(self):
        L = int(np.sqrt(self.M))
        xs = np.arange(-(L - 1), L, 2)
        ys = np.arange((L - 1), -L, -2)
        xv, yv = np.meshgrid(xs, ys)
        const = (xv+1j*yv).reshape(-1)
        const /= np.sqrt(np.mean(np.abs(const)**2))
        return const
    
    def bits_to_symbols(self, bit_seq):
        bit_groups = bit_seq.reshape(-1, self.k)
        indices = np.array([int(''.join(map(str, bits)), 2) for bits in bit_groups])
        return self.constellation[indices]
    
    def symbols_to_bits(self, symbols):
        indices = np.array([np.argmin(np.abs(symbol - self.constellation)) for symbol in symbols])
        bit_seq = np.array([list(np.binary_repr(idx, width=self.k)) for idx in indices], dtype=int).flatten()
        return bit_seq
    
class QPSK:
    def __init__(self):
        pass

    def modulate(self,bit_seq):
        bit = bit_seq.reshape(-1,2)
        symbol = (2*bit[:,0]-1) + 1j*(2*bit[:,1]-1)
        return symbol/np.sqrt(2)
    
    def demodulate(self,symbols):
        bits = np.zeros((len(symbols),2),dtype=int)
        bits[:,0] = (np.real(symbols) > 0).astype(int)
        bits[:,1] = (np.imag(symbols) > 0).astype(int)
        return bits.flatten()
    
def rician_fading(signal, snr_db, K_factor):
    s = np.sqrt(K_factor / (K_factor + 1))
    sigma = np.sqrt(1 / (2 * (K_factor + 1)))
    h_real = np.random.normal(s, sigma, len(signal))
    h_imag = np.random.normal(0, sigma, len(signal))
    h = h_real + 1j * h_imag
    y = AWGN(signal * h, snr_db)
    return y, y / h