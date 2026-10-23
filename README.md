# Lab2_Networking_Compute_ApplicationLayer
# Mộc Coffee - Công cụ gửi email

Ứng dụng desktop viết bằng Python và Tkinter, dùng để gửi email HTML giới thiệu đồ án WLAN của Nhóm 8 qua Gmail SMTP. Ứng dụng chỉ gửi đến những địa chỉ có xác nhận đồng ý nhận email.

## Các tệp trong thư mục

- `main.py`: chương trình và giao diện gửi email.
- `email_template.html`: mẫu HTML của email. Các biến được thay khi gửi là `{{name}}`, `{{message}}` và `{{project_url}}`.
- `recipients.csv`: danh sách người nhận mẫu. Hãy kiểm tra và thay bằng danh sách bạn có quyền sử dụng trước khi gửi.
- `send_log.csv`: nhật ký kết quả; chương trình tự tạo nếu tệp chưa tồn tại và ghi thêm sau mỗi lần gửi.

## Yêu cầu

- Python 3.
- Tkinter để hiển thị giao diện đồ họa (thường có sẵn trong bản Python dành cho desktop).
- Kết nối Internet.
- Tài khoản Gmail và **App Password** của Google. Ứng dụng không dùng mật khẩu Gmail thông thường.

## Cài đặt

Mở Terminal (macOS/Linux) hoặc PowerShell (Windows), chuyển đến thư mục chứa các tệp dự án:

```bash
cd đường/dẫn/đến/Nhom8_MocCoffee
```

Tạo môi trường ảo và cài thư viện `certifi` mà chương trình sử dụng:

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install certifi
```

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install certifi
```

Nếu PowerShell không cho phép kích hoạt môi trường ảo, có thể chạy trực tiếp bằng `.\.venv\Scripts\python.exe` thay cho `python` ở các lệnh bên dưới.

## Chuẩn bị Gmail

1. Bật xác minh 2 bước cho tài khoản Google.
2. Tạo **App Password** trong phần bảo mật của tài khoản Google.
3. Dùng địa chỉ Gmail và App Password 16 ký tự trong ứng dụng. Có thể dán App Password có hoặc không có dấu cách; chương trình tự bỏ dấu cách.
4. Không chia sẻ App Password, không ghi mật khẩu vào mã nguồn hoặc CSV. Đóng ứng dụng sau khi sử dụng.

Google có thể không cung cấp App Password cho một số loại tài khoản hoặc cấu hình bảo mật. Khi đó hãy kiểm tra hướng dẫn bảo mật hiện tại của Google.

## Chuẩn bị danh sách người nhận

CSV cần có các cột `name`, `email` và `consent`; có thể mở `recipients.csv` để xem định dạng:

```csv
name,email,consent
Nguyễn An,an@example.com,yes
Trần Bình,binh@example.com,no
```

- `name`: tên hiển thị trong lời chào.
- `email`: địa chỉ email hợp lệ.
- `consent`: chỉ gửi khi giá trị là `yes`, `y`, `true`, `1`, `co` hoặc `có` (không phân biệt chữ hoa/thường).
- Dòng thiếu tên/email hoặc có email sai định dạng sẽ bị bỏ qua. Những giá trị đồng ý khác danh sách trên cũng bị bỏ qua.

Lưu tệp dưới định dạng CSV, dùng dấu phẩy phân cách cột và giữ nguyên hàng tiêu đề. Chỉ đưa vào danh sách các địa chỉ bạn có quyền sử dụng và đã đồng ý nhận email.

## Chạy và sử dụng

Kích hoạt môi trường ảo nếu chưa kích hoạt, sau đó chạy:

```bash
python main.py
```

Trong cửa sổ ứng dụng:

1. Nhập Gmail gửi và App Password.
2. Chọn tệp CSV có danh sách người nhận.
3. Tùy chọn chọn tệp đính kèm; không chọn nếu không cần đính kèm.
4. Kiểm tra hoặc chỉnh sửa tiêu đề, URL landing page và lời nhắn.
5. Nhấn **Kiểm tra CSV** để xem những người sẽ được gửi và những người bị bỏ qua.
6. Nhấn **BẮT ĐẦU GỬI EMAIL** và xác nhận số lượng trước khi gửi.
7. Xem kết quả trên giao diện và trong `send_log.csv`.

Ứng dụng kết nối `smtp.gmail.com` qua cổng 587 với TLS. Nhật ký có thời gian, tên, email, trạng thái và thông tin kết quả/lỗi. Trạng thái `SUCCESS` nghĩa là máy chủ SMTP đã nhận email, không đảm bảo email đã vào hộp thư đến của người nhận.

## Tùy chỉnh mẫu email

- Có thể sửa nội dung và kiểu trình bày trong `email_template.html`.
- Giữ nguyên các biến `{{name}}`, `{{message}}` và `{{project_url}}` nếu muốn ứng dụng tự điền tên người nhận, lời nhắn và URL.
- Tiêu đề, URL landing page và lời nhắn ban đầu có thể chỉnh ngay trong giao diện trước khi gửi.

## Lưu ý

- Hãy kiểm tra kỹ danh sách, nội dung và tệp đính kèm trước khi gửi; thao tác gửi email không thể thu hồi.
- Ứng dụng ghi thêm vào `send_log.csv` hiện có, không tự xóa các lần gửi trước.
- Không đưa CSV chứa dữ liệu cá nhân, App Password hoặc thông tin bí mật lên kho mã nguồn công khai.
