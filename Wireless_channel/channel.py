import numpy as np
from scipy.special import erfc, i0e
from scipy.integrate import quad

# Quy ước chung: công suất symbol trung bình Es = 1, snr_db là Es/N0 (dB).
# Đổi từ Eb/N0: Es/N0 (dB) = Eb/N0 (dB) + 10*log10(k), với k = số bit/symbol.


def set_seed(seed):
    np.random.seed(seed)


def Q(x):
    return 0.5 * erfc(x / np.sqrt(2))


# ==========================================
# KÊNH TRUYỀN
# ==========================================
def AWGN(signal, snr_db, Es=1.0):
    N0 = Es / 10**(snr_db / 10)
    sigma = np.sqrt(N0 / 2)            # mỗi nhánh I, Q mang N0/2
    noise = sigma * (np.random.randn(len(signal)) + 1j * np.random.randn(len(signal)))
    return signal + noise, N0           # trả về cả N0 để dùng cho MMSE


def rayleigh_channel(n):
    # h ~ CN(0, 1): E[|h|^2] = 1
    return (np.random.randn(n) + 1j * np.random.randn(n)) / np.sqrt(2)


def rician_channel(n, K_factor):
    # K_factor tuyến tính; E[|h|^2] = s^2 + 2*sigma^2 = 1
    s = np.sqrt(K_factor / (K_factor + 1))
    sigma = np.sqrt(1 / (2 * (K_factor + 1)))
    return s + sigma * (np.random.randn(n) + 1j * np.random.randn(n))


def equalize(y, h, N0=None, method='zf'):
    if method == 'zf':
        return y / h
    if method == 'mmse':
        # MMSE làm co chòm sao theo |h|^2/(|h|^2+N0) -> không dùng trực tiếp cho QAM bậc cao
        return np.conj(h) / (np.abs(h)**2 + N0) * y
    raise ValueError(f"Unknown equalizer: {method}")


def Rayleigh_fading(signal, snr_db, equalizer='zf'):
    h = rayleigh_channel(len(signal))
    y, N0 = AWGN(signal * h, snr_db)
    return equalize(y, h, N0, equalizer)


def rician_fading(signal, snr_db, K_factor, equalizer='zf'):
    h = rician_channel(len(signal), K_factor)
    y, N0 = AWGN(signal * h, snr_db)
    return y, equalize(y, h, N0, equalizer)


def compute_ber(tx_bits, rx_bits):
    return np.mean(tx_bits != rx_bits)


# ==========================================
# ĐIỀU CHẾ
# ==========================================
def binary_to_gray(b):
    b = np.asarray(b)
    return b ^ (b >> 1)


def gray_to_binary(g):
    b = np.array(g)
    shift = b >> 1
    while np.any(shift):
        b ^= shift
        shift >>= 1
    return b


class QAM:
    """Square M-QAM, gán nhãn Gray độc lập trên trục I và Q.

    constellation[idx] là symbol mang nhãn k bit = idx (bit đầu là MSB),
    nên hai điểm kề nhau chỉ khác nhau 1 bit.
    """

    def __init__(self, M):
        self.M = M
        self.k = int(np.log2(M))
        if 2**self.k != M or self.k % 2:
            raise ValueError("Chỉ hỗ trợ square QAM: M = 4, 16, 64, 256, ...")
        self.L = int(np.sqrt(M))
        self.half = self.k // 2
        self.levels = np.arange(-(self.L - 1), self.L, 2)     # PAM: -L+1, ..., L-1
        self.scale = np.sqrt(2 * (M - 1) / 3)                 # chuẩn hóa Es = 1
        self.constellation = self._generate_constellation()

    def _generate_constellation(self):
        idx = np.arange(self.M)
        i_label = idx >> self.half
        q_label = idx & (self.L - 1)
        I = self.levels[gray_to_binary(i_label)]
        Qd = self.levels[gray_to_binary(q_label)]
        return (I + 1j * Qd) / self.scale

    def bits_to_symbols(self, bit_seq):
        bit_groups = np.asarray(bit_seq).reshape(-1, self.k)
        weights = 1 << np.arange(self.k - 1, -1, -1)
        indices = bit_groups @ weights
        return self.constellation[indices]

    def _slice(self, x):
        # Quyết định theo từng trục = ML cho square QAM, nhanh hơn so khoảng cách với M điểm
        pos = np.rint((x * self.scale + (self.L - 1)) / 2).astype(int)
        return np.clip(pos, 0, self.L - 1)

    def symbols_to_bits(self, symbols):
        i_label = binary_to_gray(self._slice(np.real(symbols)))
        q_label = binary_to_gray(self._slice(np.imag(symbols)))
        indices = (i_label << self.half) | q_label
        shifts = np.arange(self.k - 1, -1, -1)
        return ((indices[:, None] >> shifts) & 1).reshape(-1)


class QPSK:
    # bit b0 -> dấu của I, bit b1 -> dấu của Q (đã là Gray)
    def modulate(self, bit_seq):
        bit = np.asarray(bit_seq).reshape(-1, 2)
        symbol = (2 * bit[:, 0] - 1) + 1j * (2 * bit[:, 1] - 1)
        return symbol / np.sqrt(2)

    def demodulate(self, symbols):
        bits = np.zeros((len(symbols), 2), dtype=int)
        bits[:, 0] = (np.real(symbols) > 0).astype(int)
        bits[:, 1] = (np.imag(symbols) > 0).astype(int)
        return bits.reshape(-1)


# ==========================================
# BER LÝ THUYẾT
# ==========================================
def ber_mqam_awgn(EbN0_dB, M):
    # Xấp xỉ láng giềng gần nhất với mã Gray (chính xác với M = 4)
    k = np.log2(M)
    g = 10**(np.asarray(EbN0_dB) / 10)
    return (4 / k) * (1 - 1 / np.sqrt(M)) * Q(np.sqrt(3 * k * g / (M - 1)))


def ber_mqam_rayleigh(EbN0_dB, M):
    # Trung bình biểu thức AWGN theo |h|^2 ~ Exp(1): E[Q(sqrt(2*c*g))] = 0.5*(1 - sqrt(c*g/(1 + c*g)))
    k = np.log2(M)
    c = 1.5 * k * 10**(np.asarray(EbN0_dB) / 10) / (M - 1)
    return (2 / k) * (1 - 1 / np.sqrt(M)) * (1 - np.sqrt(c / (1 + c)))


def ber_qpsk_rician(snr_db_list, K_factor):
    """BER QPSK trên kênh Rician (K tuyến tính), snr = Es/N0.

    Pb = ∫ Q(sqrt(snr)*r) f(r) dr. Dùng i0e(x) = exp(-x)*I0(x) để tránh 0*inf = nan.
    """
    K = K_factor
    a = 2 * np.sqrt(K * (K + 1))

    def rician_pdf(r):
        x = a * r
        return 2 * (K + 1) * r * i0e(x) * np.exp(x - K - (K + 1) * r * r)

    ber = []
    for snr_db in np.atleast_1d(snr_db_list):
        snr = 10**(snr_db / 10)
        val, _ = quad(lambda r: Q(np.sqrt(snr) * r) * rician_pdf(r), 0, np.inf, limit=300)
        ber.append(val)
    return np.array(ber)
