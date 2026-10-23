import numpy as np
import matplotlib.pyplot as plt
import os


# Thử import i0 an toàn (tương thích các phiên bản scipy)
try:
    from scipy.special import erfc, i0
except Exception:
    from scipy.special import erfc, iv
    i0 = lambda x: iv(0, x)


from scipy.integrate import quad
import traceback
import sys


# ==========================================
# PHẦN 1: CẤU HÌNH THÔNG SỐ (INPUT)
# ==========================================
print("--- [1/4] ĐANG KHỞI TẠO HỆ THỐNG ---")


fc = 12e9
d = 36000e3
c = 3e8
BW = 1e6
G_tx = 30
G_rx = 30
T_sys = 500
k_boltz = 1.38e-23


# Số bit (đảm bảo chẵn)
num_bits = 200000
if num_bits % 2 != 0:
    num_bits += 1


K_factor_dB = 10
P_tx_dBW_range = np.arange(0, 31, 2)


# ==========================================
# PHẦN 2: TÍNH TOÁN LINK BUDGET
# ==========================================
lamda = c / fc
FSPL_linear = (4 * np.pi * d / lamda) ** 2
FSPL_dB = 10 * np.log10(FSPL_linear)


N_noise_watts = k_boltz * T_sys * BW
N_noise_dBW = 10 * np.log10(N_noise_watts)


print(f"-> Suy hao FSPL: {FSPL_dB:.2f} dB")
print(f"-> Tạp âm nền N: {N_noise_dBW:.2f} dBW")


# ==========================================
# PHẦN 3: HÀM TÍNH BER LÝ THUYẾT RICIAN (CHUẨN XÁC)
# ==========================================
def calculate_rician_theory_exact(snr_db_list, K_db):
    print("--- [2/4] ĐANG TÍNH ĐƯỜNG LÝ THUYẾT (có thể mất vài giây)... ---")
    K = 10 ** (K_db / 10)
    ber_results = []


    def rician_pdf(r):
        if r < 0:
            return 0.0
        try:
            result = 2.0 * r * (K + 1.0) * np.exp(-K - (K + 1.0) * r * r) * i0(2.0 * r * np.sqrt(K * (K + 1.0)))
            return result if np.isfinite(result) else 0.0
        except:
            return 0.0


    for idx, snr_val_db in enumerate(snr_db_list):
        snr_linear = 10 ** (snr_val_db / 10)
        if snr_linear <= 0:
            ber_results.append(0.5)
            continue


        try:
            integrand = lambda r: 0.5 * erfc(np.sqrt(snr_linear / 2.0) * r) * rician_pdf(r)
            val, err = quad(integrand, 0, np.inf, epsabs=1e-10, epsrel=1e-8, limit=300)
            
            # Đảm bảo BER hợp lệ
            if np.isfinite(val) and 0 <= val <= 1:
                ber_results.append(val)
                print(f"   SNR: {snr_val_db:6.2f} dB | BER Theory: {val:.6e}")
            else:
                ber_results.append(0.5)
                print(f"   SNR: {snr_val_db:6.2f} dB | BER Theory: INVALID -> set to 0.5")
        except Exception as e:
            print(f"   SNR: {snr_val_db:6.2f} dB | Error calculating theory: {e}")
            ber_results.append(0.5)


    return ber_results


# ==========================================
# PHẦN 4: VÒNG LẶP MÔ PHỎNG (MONTE CARLO)
# ==========================================
def run_simulation():
    print(f"--- [3/4] BẮT ĐẦU MÔ PHỎNG (K={K_factor_dB} dB) ---")
    sim_ber = []


    EPS = 1e-12


    for P_tx in P_tx_dBW_range:
        P_rx = P_tx + G_tx + G_rx - FSPL_dB
        SNR_dB = P_rx - N_noise_dBW
        SNR_linear = 10 ** (SNR_dB / 10)


        if SNR_linear <= 0:
            SNR_linear = 1e-12


        bits = np.random.randint(0, 2, num_bits)
        symbols_tx = (2 * bits[0::2] - 1) + 1j * (2 * bits[1::2] - 1)
        symbols_tx = symbols_tx / np.sqrt(2)


        num_symbols = len(symbols_tx)
        K = 10 ** (K_factor_dB / 10)
        mu = np.sqrt(K / (K + 1))
        sigma = np.sqrt(1.0 / (2.0 * (K + 1.0)))


        h = mu + sigma * (np.random.randn(num_symbols) + 1j * np.random.randn(num_symbols))
        y_faded = h * symbols_tx


        noise_power = 1.0 / SNR_linear
        noise = np.sqrt(noise_power / 2.0) * (np.random.randn(num_symbols) + 1j * np.random.randn(num_symbols))
        y_received = y_faded + noise


        h_safe = np.where(np.abs(h) < EPS, EPS, h)
        y_equalized = y_received / h_safe


        bits_rx = np.zeros(num_bits, dtype=int)
        bits_rx[0::2] = (np.real(y_equalized) > 0).astype(int)
        bits_rx[1::2] = (np.imag(y_equalized) > 0).astype(int)


        ber = np.sum(bits != bits_rx) / num_bits
        sim_ber.append(ber)
        print(f"   P_tx: {P_tx:2d} dBW | SNR: {SNR_dB:6.2f} dB | BER Sim: {ber:.6e}")


    return sim_ber


# ==========================================
# PHẦN 5: VẼ ĐỒ THỊ
# ==========================================
def plot_results(sim_ber):
    print("--- [4/4] ĐANG TÍNH LÝ THUYẾT VÀ VẼ ĐỒ THỊ ---")
    SNR_range_theory = P_tx_dBW_range + G_tx + G_rx - FSPL_dB - N_noise_dBW
    theory_rician = calculate_rician_theory_exact(SNR_range_theory, K_factor_dB)


    plt.figure(figsize=(10, 6))
    plt.semilogy(P_tx_dBW_range, sim_ber, 'bo-', markersize=6, linewidth=2, label='Mô phỏng (Simulation)')
    plt.semilogy(P_tx_dBW_range, theory_rician, 'r--', linewidth=2, label='Lý thuyết Rician (Theory)')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.xlabel('Công suất phát P_tx (dBW)')
    plt.ylabel('Tỷ lệ lỗi bit (BER)')
    plt.title(f'Kết quả Mô phỏng vs Lý thuyết Rician (K={K_factor_dB} dB)')
    plt.legend()
    plt.ylim(1e-6, 1)


    try:
        plt.show()
    except Exception:
        out_path = os.path.join(os.getcwd(), 'ber_plot.png')
        plt.savefig(out_path)
        print(f"Không hiển thị được cửa sổ đồ thị, đã lưu sang: {out_path}")


def main():
    sim_ber = run_simulation()
    plot_results(sim_ber)
    print("ĐÃ HOÀN THÀNH!")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Ghi traceback vào file để bạn gửi cho tôi nếu cần debug thêm
        tb_path = os.path.join(os.getcwd(), "racian_error.log")
        with open(tb_path, "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        traceback.print_exc()
        print(f"Đã ghi traceback vào: {tb_path}")
        sys.exit(1)
