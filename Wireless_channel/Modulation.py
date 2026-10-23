"""Mô phỏng BER QPSK qua tuyến vệ tinh GEO với kênh Rician, so sánh với lý thuyết."""
import numpy as np
import matplotlib.pyplot as plt

from channel import QPSK, AWGN, rician_channel, equalize, compute_ber, ber_qpsk_rician

# ==========================================
# PHẦN 1: CẤU HÌNH THÔNG SỐ
# ==========================================
fc = 12e9           # tần số sóng mang (Hz)
d = 36000e3         # khoảng cách GEO (m)
c = 3e8
BW = 1e6            # băng thông (Hz), giả sử tốc độ symbol = BW nên SNR = Es/N0
G_tx = 30           # dBi
G_rx = 30           # dBi
T_sys = 500         # nhiệt độ tạp âm hệ thống (K)
k_boltz = 1.38e-23

num_bits = 200000
K_factor_dB = 10
P_tx_dBW_range = np.arange(0, 31, 2)


# ==========================================
# PHẦN 2: LINK BUDGET
# ==========================================
def link_budget():
    lamda = c / fc
    FSPL_dB = 20 * np.log10(4 * np.pi * d / lamda)
    N_noise_dBW = 10 * np.log10(k_boltz * T_sys * BW)
    return FSPL_dB, N_noise_dBW


def snr_from_ptx(P_tx_dBW, FSPL_dB, N_noise_dBW):
    P_rx_dBW = P_tx_dBW + G_tx + G_rx - FSPL_dB
    return P_rx_dBW - N_noise_dBW


# ==========================================
# PHẦN 3: MÔ PHỎNG MONTE CARLO
# ==========================================
def run_simulation(snr_db_list, K_factor):
    qpsk = QPSK()
    sim_ber = []
    for snr_db in snr_db_list:
        bits = np.random.randint(0, 2, num_bits)
        symbols_tx = qpsk.modulate(bits)

        h = rician_channel(len(symbols_tx), K_factor)
        y, N0 = AWGN(h * symbols_tx, snr_db)
        bits_rx = qpsk.demodulate(equalize(y, h, N0, 'zf'))

        ber = compute_ber(bits, bits_rx)
        sim_ber.append(ber)
        print(f"   SNR: {snr_db:6.2f} dB | BER Sim: {ber:.6e}")
    return np.array(sim_ber)


# ==========================================
# PHẦN 4: VẼ ĐỒ THỊ
# ==========================================
def plot_results(sim_ber, theory_ber):
    plt.figure(figsize=(10, 6))
    # BER = 0 không vẽ được trên trục log
    plt.semilogy(P_tx_dBW_range, np.where(sim_ber > 0, sim_ber, np.nan), 'bo-',
                 markersize=6, linewidth=2, label='Mô phỏng (Simulation)')
    plt.semilogy(P_tx_dBW_range, theory_ber, 'r--', linewidth=2, label='Lý thuyết Rician (Theory)')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.xlabel('Công suất phát P_tx (dBW)')
    plt.ylabel('Tỷ lệ lỗi bit (BER)')
    plt.title(f'QPSK qua kênh Rician (K={K_factor_dB} dB): Mô phỏng vs Lý thuyết')
    plt.legend()
    plt.ylim(1e-6, 1)
    plt.show()


def main():
    FSPL_dB, N_noise_dBW = link_budget()
    print(f"-> Suy hao FSPL: {FSPL_dB:.2f} dB")
    print(f"-> Tạp âm nền N: {N_noise_dBW:.2f} dBW")

    K_factor = 10**(K_factor_dB / 10)
    snr_db_list = snr_from_ptx(P_tx_dBW_range, FSPL_dB, N_noise_dBW)

    print(f"--- Mô phỏng (K={K_factor_dB} dB) ---")
    sim_ber = run_simulation(snr_db_list, K_factor)
    theory_ber = ber_qpsk_rician(snr_db_list, K_factor)
    plot_results(sim_ber, theory_ber)


if __name__ == "__main__":
    main()
