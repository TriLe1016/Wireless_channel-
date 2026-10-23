# Rayleigh Fading
## Mục đích
- thường để mô phỏng khu đô thị dày đặc, khoảng cách truyền dài và có nhiều chướng ngại
- là kênh truyền đa đường (multipath)
- không có đường truyền trực tiếp (LOS), tín hiệu chỉ đến nhờ phản xạ, tán xạ, khúc xạ

## Khái niệm
- Biên độ tín hiệu phải tuân theo phân phối Rayleigh
- Pha tín hiệu ngẫu nhiên, phân bố từ 0 đến 2$\pi$
$$
y(t) = h(t).x(t)+n(t)
$$
- hệ số kênh Rayleigh: $h(t) = h_I(t) + jh_Q(t)$ mô tả biến đổi biên độ và pha
- $h_I(t)$ và $h_Q(t)$ là 2 biến Gaussian độc lập, $\mu = 0, \sigma^2$:
$$
h_I, h_Q \sim \mathcal{N}(0,\sigma^2)
$$
- Công suất trung bình của kênh: $E[|h|^2] = 2\sigma^2$. Thường chuẩn hóa $E[|h|^2] = 1 \Rightarrow \sigma^2 = \frac{1}{2}$
- Biên độ: $|h| = \sqrt{h_I^2 + h_Q^2}$
- Pha: $\theta = \arctan\frac{h_Q}{h_I}$, phân bố đều từ 0 đến $2\pi$
- $|h|$ tuân theo phân phối rayleigh:
$$
f_{|h|}(r) = \frac{r}{\sigma^2} e^{- \frac{r^2}{2\sigma^2}}, \quad r \ge 0
$$

## Nguyên nhân
Khi tín hiệu đến từ nhiều đường multipath, tổng hợp có thể biểu diễn bằng **vector phức**:

$$
h = \sum_{k=1}^{N} a_k e^{j \phi_k}
$$

Trong đó:  
- $a_k$ : biên độ của từng đường  
- $\phi_k$ : pha ngẫu nhiên của từng đường

Khi $N$ lớn và $\phi_k$ phân bố đồng đều, theo **Định lý Trung tâm Giới hạn (Central Limit Theorem)**, tổng này xấp xỉ **Gaussian trong miền phức**, dẫn tới **biên độ $|h|$ tuân theo phân phối Rayleigh**.

## Mô phỏng 
`h = (np.random.randn(N) + 1j*np.random.randn(N)) / np.sqrt(2)`
- $h = \frac{1}{\sqrt{2}} \left( n_I + j n_Q \right)$, với $n_I, n_Q \sim \mathcal{N}(0, 1)$, tức là $\sigma^2 = \frac{1}{2}$ và $E[|h|^2] = 1$
- Cân bằng ZF: $\hat{x} = y/h$. Với kênh 1 tap và $h$ đã biết, cách này cho quyết định ML
- Cân bằng MMSE: $\hat{x} = \frac{h^*}{|h|^2 + N_0}y$. Kết quả bị co về gốc một hệ số $\frac{|h|^2}{|h|^2+N_0}$, nên không dùng trực tiếp để quyết định QAM bậc cao
- BER QPSK lý thuyết trên kênh Rayleigh: $P_b = \frac{1}{2}\left(1 - \sqrt{\frac{\bar\gamma_b}{1+\bar\gamma_b}}\right)$, với $\bar\gamma_b = E_b/N_0$
# Phân phối Rayleigh

**Định lý:** Nếu \(X, Y\) độc lập và cùng phân phối Gaussian:

$$
X, Y \sim N(0, \sigma^2)
$$

thì biến:

$$
R = \sqrt{X^2 + Y^2}
$$

sẽ có phân phối Rayleigh với hàm mật độ xác suất:

$$
f_R(r) = \frac{r}{\sigma^2} \, e^{- \frac{r^2}{2\sigma^2}}, \quad r \ge 0
$$

Trong đó:  
- \(R\) là biên độ kết hợp của hai biến Gaussian \(X\) và \(Y\).  
- $\sigma$ là độ lệch chuẩn ($\sigma^2$ là phương sai) của mỗi thành phần Gaussian.
