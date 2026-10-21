import csv
import certifi
import mimetypes
import os
import re
import smtplib
import ssl
import threading
from datetime import datetime
from email.message import EmailMessage
from html import escape
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "send_log.csv")
EMAIL_TEMPLATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "email_template.html")


class EmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mộc Coffee | Nhóm 8 - Gửi Email Đồ Án WLAN")
        self.root.geometry("950x780")
        self.root.minsize(800, 650)

        self.csv_path = tk.StringVar()
        self.attachment_path = tk.StringVar()
        self.sender = tk.StringVar()
        self.app_password = tk.StringVar()
        self.subject = tk.StringVar(value="[Nhóm 8] Giới thiệu giải pháp WLAN quán Cafe Mộc Coffee")
        self.project_url = tk.StringVar(value="https://moccoffeehousee.42web.io")
        self.busy = False
        self.output = None
        self.body = None

        self._build_ui()

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="MỘC COFFEE - NHÓM 8", font=("Arial", 22, "bold"), foreground="#1f5b45").pack(anchor="w")
        ttk.Label(outer, text="Chương trình gửi email tự động giới thiệu đồ án mạng không dây (WLAN)", font=("Arial", 11, "italic")).pack(anchor="w", pady=(0, 15))

        account = ttk.LabelFrame(outer, text=" 1. Tài khoản gửi Email (Gmail) ", padding=10)
        account.pack(fill="x", pady=5)
        ttk.Label(account, text="Địa chỉ Gmail:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(account, textvariable=self.sender, width=45).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(account, text="App Password:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(account, textvariable=self.app_password, show="*", width=45).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(account, text="* Lưu ý: Dùng App Password (16 ký tự), KHÔNG dùng mật khẩu Gmail thường.", foreground="red").grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=3)
        account.columnconfigure(1, weight=1)

        files = ttk.LabelFrame(outer, text=" 2. Danh sách người nhận và Tệp đính kèm ", padding=10)
        files.pack(fill="x", pady=5)

        ttk.Label(files, text="File CSV:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(files, textvariable=self.csv_path).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(files, text="Chọn CSV...", command=self.choose_csv).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(files, text="File đính kèm:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(files, textvariable=self.attachment_path).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(files, text="Chọn File...", command=self.choose_attachment).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(files, text="* File CSV bắt buộc có 3 cột: name, email, consent (chỉ gửi khi consent=yes).").grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=3)
        files.columnconfigure(1, weight=1)

        content = ttk.LabelFrame(outer, text=" 3. Nội dung Email (HTML) ", padding=10)
        content.pack(fill="x", pady=5)

        ttk.Label(content, text="Tiêu đề:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(content, textvariable=self.subject).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(content, text="Landing Page:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(content, textvariable=self.project_url).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(content, text="Lời nhắn:").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        self.body = tk.Text(content, height=4, wrap="word", font=("Arial", 10))
        self.body.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.body.insert(
            "1.0",
            "Nhóm 8 chúng em xin gửi đến anh/chị giải pháp thiết kế hệ thống mạng không dây (WLAN) cho quán Cafe Mộc Coffee. Giải pháp giúp tối ưu vùng phủ sóng, chống nghẽn mạng và đảm bảo bảo mật cho khách hàng.",
        )
        content.columnconfigure(1, weight=1)

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=10)
        ttk.Button(actions, text="🔍 Kiểm tra CSV", command=self.preview_csv).pack(side="left", padx=(0, 10))
        self.send_button = ttk.Button(actions, text="🚀 BẮT ĐẦU GỬI EMAIL", command=self.confirm_send)
        self.send_button.pack(side="left")
        ttk.Label(actions, text="(Chỉ gửi cho người có consent = yes)", foreground="#8a3b12").pack(side="left", padx=15)

        result = ttk.LabelFrame(outer, text=" 4. Nhật ký hoạt động ", padding=8)
        result.pack(fill="both", expand=True, pady=5)
        self.status = tk.StringVar(value="Sẵn sàng. Hãy chọn file CSV và kiểm tra trước khi gửi.")
        ttk.Label(result, textvariable=self.status, font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.output = tk.Text(result, height=10, wrap="word", state="disabled", bg="#f4f4f4")
        self.output.pack(fill="both", expand=True)

    @staticmethod
    def normalize_consent(value):
        return (value or "").strip().lower()

    @staticmethod
    def is_approved_consent(value):
        normalized = EmailApp.normalize_consent(value)
        return normalized in {"yes", "y", "true", "1", "co", "có"}

    def log_ui(self, text):
        if self.output is None:
            return
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def choose_csv(self):
        path = filedialog.askopenfilename(title="Chọn danh sách CSV", filetypes=[("CSV files", "*.csv")])
        if path:
            self.csv_path.set(path)

    def choose_attachment(self):
        path = filedialog.askopenfilename(title="Chọn tệp đính kèm", filetypes=[("All files", "*.*"), ("PDF", "*.pdf")])
        if path:
            self.attachment_path.set(path)

    def read_recipients(self):
        path = self.csv_path.get().strip()
        if not path or not os.path.isfile(path):
            raise ValueError("Vui lòng chọn một tệp CSV tồn tại.")

        recipients = []
        with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            required = {"name", "email", "consent"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                raise ValueError("CSV phải có đúng các cột bắt buộc: name,email,consent.")

            for row_num, row in enumerate(reader, start=2):
                name = (row.get("name") or "").strip()
                email = (row.get("email") or "").strip()
                consent = self.normalize_consent(row.get("consent"))

                if not name and not email:
                    continue
                if not name or not email:
                    self.log_ui(f"Dòng {row_num}: Thiếu tên hoặc email, bỏ qua.")
                    continue
                if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                    self.log_ui(f"Dòng {row_num}: Email không đúng định dạng ({email}), bỏ qua.")
                    continue

                recipients.append({"name": name, "email": email, "consent": consent, "row": row_num})

        return recipients

    def preview_csv(self):
        try:
            rows = self.read_recipients()
            allowed = [row for row in rows if self.is_approved_consent(row["consent"])]
            skipped = len(rows) - len(allowed)

            self.status.set(f"Đọc được {len(rows)} dòng. Sẽ gửi: {len(allowed)}. Bỏ qua: {skipped}.")
            self.log_ui("--- KẾT QUẢ KIỂM TRA CSV ---")
            self.log_ui(f"Tổng số dòng hợp lệ: {len(rows)}")
            self.log_ui(f"Số người đồng ý nhận (consent=yes): {len(allowed)}")
            self.log_ui(f"Số người bị bỏ qua: {skipped}")

            for row in rows:
                status = "OK" if self.is_approved_consent(row["consent"]) else "SKIP"
                self.log_ui(f"  [{status}] {row['name']} | {row['email']} | consent={row['consent']}")
        except Exception as exc:
            messagebox.showerror("Lỗi CSV", str(exc))

    def confirm_send(self):
        if self.busy:
            return

        sender = self.sender.get().strip()
        password = self.app_password.get().replace(" ", "").strip()

        if not sender or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập Địa chỉ Gmail và App Password.")
            return
        if not password.isascii():
            messagebox.showerror(
                "App Password không hợp lệ",
                "App Password có ký tự không thuộc bảng ASCII. Hãy tạo App Password 16 ký tự trong Google Account và dán lại; không dùng mật khẩu Gmail thông thường.",
            )
            return
        if len(password) != 16:
            messagebox.showerror(
                "App Password không hợp lệ",
                "App Password của Google gồm 16 ký tự. Hãy kiểm tra và nhập lại (có thể dán có hoặc không có dấu cách).",
            )
            return
        if not re.fullmatch(r"[^@\s]+@gmail\.com", sender, flags=re.IGNORECASE):
            messagebox.showerror("Lỗi", "Địa chỉ Gmail không hợp lệ. Vui lòng nhập email thật của tài khoản Gmail.")
            return
        if not self.subject.get().strip() or not self.project_url.get().strip():
            messagebox.showerror("Lỗi", "Tiêu đề và Landing Page không được để trống.")
            return

        try:
            rows = self.read_recipients()
            allowed = [row for row in rows if self.is_approved_consent(row["consent"])]
            if not allowed:
                messagebox.showwarning("Cảnh báo", "Không có ai trong danh sách có consent = yes. Không thể gửi.")
                return
        except Exception as exc:
            messagebox.showerror("Lỗi dữ liệu", str(exc))
            return

        if not messagebox.askyesno("Xác nhận", f"Hệ thống sẽ gửi {len(allowed)} email.\nBạn có chắc chắn muốn tiếp tục?"):
            return

        self.busy = True
        self.send_button.configure(state="disabled")
        self.status.set("Đang gửi email... Vui lòng đợi (Giao diện vẫn hoạt động).")
        threading.Thread(target=self.send_worker, args=(allowed, sender, password), daemon=True).start()

    def build_message(self, recipient, sender):
        name = recipient["name"]
        subject = self.subject.get().strip()
        url = self.project_url.get().strip()
        body = self.body.get("1.0", "end").strip()

        if not body:
            body = "Nhóm 8 chúng em gửi lời chào và giới thiệu giải pháp WLAN cho quán Cafe Mộc Coffee."

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient["email"]
        msg.set_content(f"Xin chào {name},\n\n{body}\n\nLanding Page dự án: {url}\n\nTrân trọng,\nNhóm 8 - Mộc Coffee")

        with open(EMAIL_TEMPLATE_FILE, "r", encoding="utf-8") as template_file:
            html = template_file.read()
        replacements = {
            "name": escape(name),
            "message": escape(body).replace("\n", "<br>"),
            "project_url": escape(url, quote=True),
        }
        html = re.sub(r"\{\{(name|message|project_url)\}\}", lambda match: replacements[match.group(1)], html)
        msg.add_alternative(html, subtype="html")

        attachment = self.attachment_path.get().strip()
        if attachment:
            if not os.path.isfile(attachment):
                raise ValueError("Tệp đính kèm không tồn tại.")
            mime_type, _ = mimetypes.guess_type(attachment)
            if mime_type:
                maintype, subtype = mime_type.split("/", 1)
            else:
                maintype, subtype = "application", "octet-stream"
            with open(attachment, "rb") as file_obj:
                msg.add_attachment(file_obj.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(attachment))
        return msg

    def write_log(self, recipient, status, detail):
        exists = os.path.exists(LOG_FILE)
        with open(LOG_FILE, "a", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "name", "email", "status", "detail"])
            if not exists or os.path.getsize(LOG_FILE) == 0:
                writer.writeheader()
            writer.writerow({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "name": recipient["name"],
                "email": recipient["email"],
                "status": status,
                "detail": detail,
            })

    def send_worker(self, recipients, sender, password):
        success = 0
        failed = 0

        try:
            context = ssl.create_default_context(cafile=certifi.where())
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(sender, password)

                for recipient in recipients:
                    try:
                        msg = self.build_message(recipient, sender)
                        server.send_message(msg)
                        self.write_log(recipient, "SUCCESS", "SMTP accepted message")
                        success += 1
                        self.root.after(0, self.log_ui, f"✅ THÀNH CÔNG: {recipient['name']} <{recipient['email']}>")
                    except Exception as exc:
                        failed += 1
                        detail = str(exc).replace("\n", " ")[:500]
                        try:
                            self.write_log(recipient, "FAILED", detail)
                        except Exception:
                            pass
                        self.root.after(0, self.log_ui, f"❌ THẤT BẠI: {recipient['email']} | Lỗi: {detail}")

        except Exception as exc:
            failed += len(recipients)
            detail = str(exc).replace("\n", " ")[:500]
            for recipient in recipients:
                try:
                    self.write_log(recipient, "FAILED", detail)
                except Exception:
                    pass
            self.root.after(0, self.log_ui, f"❌ LỖI KẾT NỐI SMTP: {detail}")
        finally:
            self.root.after(0, self.finish_send, success, failed)

    def finish_send(self, success, failed):
        self.busy = False
        self.send_button.configure(state="normal")
        self.status.set(f"Hoàn tất! Thành công: {success} | Thất bại: {failed}.")
        messagebox.showinfo("Đã xong", f"Gửi thành công: {success}\nGửi thất bại: {failed}\n\nXem chi tiết trong file {LOG_FILE}")


if __name__ == "__main__":
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    EmailApp(root)
    root.mainloop()
