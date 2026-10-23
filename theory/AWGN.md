# AWGN (Additive White Gausian Noise)
## Mục đích
- kênh truyền lý tưởng, đơn giản nhất, chỉ thêm nhiễu nhiệt
- Không có hiện tượng fading hay trễ truyền
- ứng dụng: BER, BPSK/QPSK
## 1. Khái niệm
- AWGN mô phỏng việc tín hiệu bị lẫn tạp âm ngẫu nhiên từ môi trường
- Additive: Nhiễu được cộng thêm vào tín hiệu( không nhân, không biến dạng tín hiệu)
- White: Nhiễu có phổ công suất phẳng - năng lượng phân bố đều trên mọi tần số (như ánh sáng trắng có mọi màu)
- Gaussian: Biên độ nhiễu tuân theo phân bố chuẩn (normal distribution) với trung bình 0, phương sai $\sigma^2$
$$
y(t) = x(t) + n(t)
$$
- $x(t)$: tín hiệu gốc
- $n(t)$: nhiễu Gausian $\sim \mathcal{N}(0,\sigma^2)$
- $y(t)$: tín hiệu nhận được tại đầu thu
  
## 2. Mục đích
- thử độ bền hệ thống với nhiễu
- tính BER (Bit Error Rate) theo SNR
- đánh giá hiệu suất điều chế
## 3. SNR và Noise
- Signal-to-Noise Ratio: $\text{SNR} = \frac{P_x}{P_n} = \frac{\text{công suất tín hiệu}}{\text{công suất nhiễu}}$
- SNR theo dB: $\text{SNR}_{dB} = 10 \log_{10}\left(\frac{P_x}{P_n}\right)$

$\Rightarrow$ công suất nhiễu: $P_n = \frac{P_x}{10^{\text{SNR}_{dB}/10}}$
- độ lệch chuẩn của nhiễu thực: $\sigma = \sqrt{P_n}$; nhiễu phức: mỗi nhánh I, Q có $\sigma = \sqrt{P_n/2}$
- Trong code, công suất symbol được chuẩn hóa $E_s = 1$ nên $P_n = N_0 = 10^{-\text{SNR}_{dB}/10}$
- Đổi từ $E_b/N_0$: $\frac{E_s}{N_0}\Big|_{dB} = \frac{E_b}{N_0}\Big|_{dB} + 10\log_{10}k$, với $k = \log_2 M$ bit/symbol

## 4. Gaussian Noise
- nhiễu sinh ra phải có công suất trung bình là $P_n = \lim_{T \to \infty} \frac{1}{T} \int_{-T/2}^{T/2} |n(t)|^2 \, dt$
- Theo xác suất $P_n = E[n^2]$
- gọi các nhiễu chuẩn hóa là $n_i\sim \mathcal{N}(0, 1)$ 
- công suất trung bình mong muốn là $\sigma^2$
- nhiễu thực:
  - $n = \sqrt{P_n}\,n_I = \sigma n_I$
- nhiễu phức:
  - $n = \sqrt{\frac{P_n}{2}}(n_I+jn_Q)$, khi đó $E[|n|^2] = \frac{P_n}{2}(1+1) = P_n$
  
$\Rightarrow$ vì $n_I, n_Q$ là nhiễu Gaussian chuẩn nên $E[n_I^2] = E[n_Q^2] = 1$
- hàm phân phối chuẩn Gaussian:`np.random.randn(N)`