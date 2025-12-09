# app.py - PHIÊN BẢN CUỐI CÙNG HOÀN CHỈNH 100% (08/12/2025)
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from functools import wraps
from datetime import datetime
import sqlite3
import os
import json
import secrets
import hashlib

app = Flask(__name__)
app.secret_key = "DTA_QTKT02_BM02_2025_V2_SECURE_2025"
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.jinja_env.filters['fromjson'] = lambda v: json.loads(v) if v else []

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
DB_NAME = "qtkt_database.db"

# ==================== DANH SÁCH NGƯỜI DÙNG (chỉ dùng để lấy thông tin) ====================
USERS = {
    # ==================== BOD ====================
    "truongkhuong@dieutuongam.com": {"name": "TRƯƠNG HUỆ KHƯƠNG", "role": "BOD", "department": "BOD"},
    "hongtuyet@dieutuongam.com": {"name": "NGUYỄN THỊ HỒNG TUYẾT", "role": "BOD", "department": "BOD"},

    # ==================== PHÒNG HCNS-IT ====================
    "it@dieutuongam.com": {"name": "TRẦN CÔNG KHÁNH", "role": "Manager", "department": "PHÒNG HCNS-IT"},
    "anthanh@dieutuongam.com": {"name": "NGUYỄN THỊ AN THANH", "role": "Manager", "department": "PHÒNG HCNS-IT"},
    "hcns@dieutuongam.com": {"name": "NHÂN SỰ DTA", "role": "Employee", "department": "PHÒNG HCNS-IT"},
    "yennhi@dieutuongam.com": {"name": "TRẦN NGỌC YẾN NHI", "role": "Employee", "department": "PHÒNG HCNS-IT"},
    "info@dieutuongam.com": {"name": "Trung Tâm Nghệ Thuật Phật Giáo Diệu Tướng Am", "role": "Employee", "department": "PHÒNG HCNS-IT"},

    # ==================== PHÒNG TÀI CHÍNH KẾ TOÁN ====================
    "ketoan@dieutuongam.com": {"name": "LÊ THỊ MAI ANH", "role": "Manager", "department": "PHÒNG TÀI CHÍNH KẾ TOÁN"},

    # ==================== PHÒNG KINH DOANH HCM ====================
    "xuanhoa@dieutuongam.com": {"name": "LÊ XUÂN HOA", "role": "Manager", "department": "PHÒNG KINH DOANH HCM"},
    "salesadmin@dieutuongam.com": {"name": "NGUYỄN DUY ANH", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "kho@dieutuongam.com": {"name": "HUỲNH MINH TOÀN", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "thoainha@dieutuongam.com": {"name": "TRẦN THOẠI NHÃ", "role": "Manager", "department": "PHÒNG KINH DOANH HCM"},
    "thanhtuan.dta@gmail.com": {"name": "BÀNH THANH TUẤN", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "thientinh.dta@gmail.com": {"name": "BÙI THIỆN TÌNH", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "giathanh.dta@gmail.com": {"name": "NGÔ GIA THÀNH", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "vannhuann.dta@gmail.com": {"name": "PHẠM VĂN NHUẬN", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "minhhieuu.dta@gmail.com": {"name": "LÊ MINH HIẾU", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "thanhtrung.dta@gmail.com": {"name": "NGUYỄN THÀNH TRUNG", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "khanhngan.dta@gmail.com": {"name": "NGUYỄN NGỌC KHÁNH NGÂN", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "thitrang.dta@gmail.com": {"name": "NGUYỄN THỊ TRANG", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "thanhtienn.dta@gmail.com": {"name": "NGUYỄN THANH TIẾN", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},

    # ==================== PHÒNG KINH DOANH HN ====================
    "nguyenngoc@dieutuongam.com": {"name": "NGUYỄN THỊ NGỌC", "role": "Manager", "department": "PHÒNG KINH DOANH HN"},
    "vuthuy@dieutuongam.com": {"name": "VŨ THỊ THÙY", "role": "Manager", "department": "PHÒNG KINH DOANH HN"},
    "mydung.dta@gmail.com": {"name": "HOÀNG THỊ MỸ DUNG", "role": "Employee", "department": "PHÒNG KINH DOANH HN"},

    # ==================== PHÒNG TRUYỀN THÔNG & MARKETING ====================
    "marketing@dieutuongam.com": {"name": "HUỲNH THỊ BÍCH TUYỀN", "role": "Manager", "department": "PHÒNG TRUYỀN THÔNG & MARKETING"},
    "lehong.dta@gmail.com": {"name": "LÊ THỊ HỒNG", "role": "Employee", "department": "PHÒNG TRUYỀN THÔNG & MARKETING"},

    # ==================== PHÒNG KẾ HOẠCH TỔNG HỢP ====================
    "lehuyen@dieutuongam.com": {"name": "NGUYỄN THỊ LỆ HUYỀN", "role": "Manager", "department": "PHÒNG KẾ HOẠCH TỔNG HỢP"},
    "hatrang@dieutuongam.com": {"name": "PHẠM HÀ TRANG", "role": "Manager", "department": "PHÒNG KẾ HOẠCH TỔNG HỢP"},

    # ==================== PHÒNG SÁNG TẠO TỔNG HỢP ====================
    "thietke@dieutuongam.com": {"name": "ĐẶNG THỊ MINH THÙY", "role": "Manager", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},
    "ptsp@dieutuongam.com": {"name": "DƯƠNG NGỌC HIỂU", "role": "Manager", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},
    "qlda@dieutuongam.com": {"name": "PHẠM THẾ HẢI", "role": "Manager", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},
    "minhdat.dta@gmail.com": {"name": "LÂM MINH ĐẠT", "role": "Employee", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},
    "thanhvii.dat@gmail.com": {"name": "LÊ THỊ THANH VI", "role": "Employee", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},
    "quangloi.dta@gmail.com": {"name": "LÊ QUANG LỢI", "role": "Employee", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},
    "tranlinh.dta@gmail.com": {"name": "NGUYỄN THỊ PHƯƠNG LINH", "role": "Employee", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},

    # ==================== BỘ PHẬN HỖ TRỢ - GIAO NHẬN ====================
    "hotro1.dta@gmail.com": {"name": "NGUYỄN VĂN MẠNH", "role": "Employee", "department": "BỘ PHẬN HỖ TRỢ - GIAO NHẬN"},
}

DEPARTMENTS = sorted(set(u["department"] for u in USERS.values()))
NGUON_KINH_PHI = ["Ngân sách công ty", "Dự án", "Quỹ phúc lợi", "Khác"]

# ==================== MẬT KHẨU ====================
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def check_password(stored, provided):
    return stored == hash_password(provided)

# ==================== KHỞI TẠO DB ====================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS qtkt_forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submitter_email TEXT NOT NULL,
            submitter_name TEXT NOT NULL,
            submit_date TEXT NOT NULL,
            phong_ban TEXT NOT NULL,
            so_tien_tam_ung REAL DEFAULT 0,
            ngay_tam_ung TEXT,
            ly_do_tam_ung TEXT,
            city TEXT,
            nguon_kinh_phi TEXT,
            noi_phat_sinh_chi TEXT,
            ma_du_an TEXT,
            chi_tiet_json TEXT,
            tong_thanh_toan_thuc_te REAL DEFAULT 0,
            loai_thanh_toan TEXT DEFAULT 'Thừa',
            attachment TEXT,
            status TEXT DEFAULT 'Chờ duyệt',
            current_approver TEXT,
            next_approver TEXT,
            final_approver_name TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS user_logins (
            email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            must_change_password INTEGER DEFAULT 1,
            changed_at TEXT
        )
    ''')

    # Tạo user + mật khẩu mặc định nếu chưa có
    default_hash = hash_password("123456")
    for email in USERS.keys():
        c.execute("SELECT 1 FROM user_logins WHERE email = ?", (email,))
        if not c.fetchone():
            c.execute("INSERT INTO user_logins (email, password_hash, must_change_password) VALUES (?, ?, 1)",
                      (email, default_hash))

    conn.commit()
    conn.close()

# ==================== DECORATOR ====================
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrap

# ==================== ROUTES ====================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        pw = request.form["password"]

        if email not in USERS:
            flash("Email không tồn tại!", "danger")
            return render_template("login.html")

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT password_hash, must_change_password FROM user_logins WHERE email = ?", (email,))
        row = c.fetchone()
        conn.close()

        if row and check_password(row[0], pw):
            session["user"] = {
                "email": email,
                "name": USERS[email]["name"],
                "role": USERS[email]["role"],
                "department": USERS[email]["department"]
            }
            if row[1] == 1:
                flash("Bạn cần đổi mật khẩu trước khi tiếp tục!", "warning")
                return redirect(url_for("change_password"))
            return redirect(url_for("dashboard"))
        else:
            flash("Mật khẩu sai!", "danger")
    return render_template("login.html")

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    email = session["user"]["email"]
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT must_change_password, password_hash FROM user_logins WHERE email = ?", (email,))
    row = c.fetchone()
    must_change = row[0] == 1
    current_hash = row[1]

    if request.method == "POST":
        old_pw = request.form.get("old_password", "")
        new_pw = request.form["new_password"]
        confirm = request.form["confirm_password"]

        if not must_change and not check_password(current_hash, old_pw):
            flash("Mật khẩu cũ không đúng!", "danger")
        elif new_pw != confirm:
            flash("Mật khẩu xác nhận không khớp!", "danger")
        elif len(new_pw) < 6:
            flash("Mật khẩu mới phải ≥ 6 ký tự!", "danger")
        else:
            new_hash = hash_password(new_pw)
            c.execute("UPDATE user_logins SET password_hash = ?, must_change_password = 0, changed_at = ? WHERE email = ?",
                      (new_hash, datetime.now().strftime("%d/%m/%Y %H:%M"), email))
            conn.commit()
            conn.close()
            flash("Đổi mật khẩu thành công!", "success")
            return redirect(url_for("dashboard"))

    conn.close()
    return render_template("change_password.html", user=session["user"], must_change=must_change)

@app.route("/dashboard")
@login_required
def dashboard():
    user = session["user"]
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    approver_str = f"{user['name']} - {user['department']}"
    c.execute("SELECT * FROM qtkt_forms WHERE next_approver = ? AND status = 'Chờ duyệt' ORDER BY id DESC", (approver_str,))
    pending = c.fetchall()
    conn.close()
    return render_template("qtkt_dashboard.html", user=user, pending=pending)

@app.route("/qtkt_form", methods=["GET", "POST"])
@login_required
def qtkt_form():
    user = session["user"]
    if request.method == "POST":
        try:
            phong_ban = request.form["phong_ban"]
            so_tien_tam_ung = float(request.form.get("so_tien_tam_ung", 0) or 0)
            ngay_tam_ung = request.form["ngay_tam_ung"]
            ly_do_tam_ung = request.form["ly_do_tam_ung"]
            city = request.form["city"]
            nguon_kinh_phi = request.form["nguon_kinh_phi"]
            noi_phat_sinh_chi = request.form.get("noi_phat_sinh_chi", "")
            ma_du_an = request.form.get("ma_du_an", "")

            chi_tiet_list = []
            tong_thanh_toan_thuc_te = 0
            for i in range(100):
                if f"noi_dung_{i}" in request.form:
                    so_tien = float(request.form.get(f"so_tien_ct_{i}", 0) or 0)
                    chi_tiet_list.append({
                        "so_chung_tu": request.form.get(f"so_chung_tu_{i}", ""),
                        "ngay_chung_tu": request.form.get(f"ngay_chung_tu_{i}", ""),
                        "noi_dung": request.form[f"noi_dung_{i}"],
                        "so_tien_ct": so_tien
                    })
                    tong_thanh_toan_thuc_te += so_tien

            loai_thanh_toan = request.form["loai_thanh_toan"]

            filename = None
            if 'attachment' in request.files:
                file = request.files['attachment']
                if file and file.filename:
                    ext = os.path.splitext(file.filename)[1].lower()
                    if ext in {'.pdf','.doc','.docx','.xls','.xlsx','.jpg','.jpeg','.png'}:
                        filename = f"QTKT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(8)}{ext}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            next_approver_full = request.form["approver"]
            next_approver_name = next_approver_full.split(" - ")[0]

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute('''
                INSERT INTO qtkt_forms
                (submitter_email, submitter_name, submit_date, phong_ban,
                 so_tien_tam_ung, ngay_tam_ung, ly_do_tam_ung,
                 city, nguon_kinh_phi, noi_phat_sinh_chi, ma_du_an,
                 chi_tiet_json, tong_thanh_toan_thuc_te, loai_thanh_toan,
                 attachment, status, current_approver, next_approver, final_approver_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Chờ duyệt', ?, ?, ?)
            ''', (
                user["email"], user["name"], datetime.now().strftime("%d/%m/%Y %H:%M"),
                phong_ban, so_tien_tam_ung, ngay_tam_ung, ly_do_tam_ung,
                city, nguon_kinh_phi, noi_phat_sinh_chi, ma_du_an,
                json.dumps(chi_tiet_list, ensure_ascii=False),
                tong_thanh_toan_thuc_te, loai_thanh_toan,
                filename, next_approver_full, next_approver_full, next_approver_name
            ))
            conn.commit()
            conn.close()
            flash(f"Đã gửi quyết toán thành công! Chờ duyệt từ: {next_approver_name}", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash(f"Lỗi: {str(e)}", "danger")

    approvers = [f"{v['name']} - {v['department']}" for k, v in USERS.items() if v["role"] in ["Manager", "BOD"] and k != user["email"]]
    return render_template("qtkt_form.html", user=user, departments=DEPARTMENTS, approvers=approvers, nguon_kinh_phi_list=NGUON_KINH_PHI)

@app.route("/approve/<int:form_id>", methods=["GET", "POST"])
@login_required
def approve(form_id):
    user = session["user"]
    if user["role"] not in ["Manager", "BOD"]:
        flash("Không có quyền duyệt!", "danger")
        return redirect(url_for("dashboard"))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM qtkt_forms WHERE id = ?", (form_id,))
    form = c.fetchone()
    if not form:
        flash("Không tìm thấy!", "danger")
        conn.close()
        return redirect(url_for("dashboard"))

    my_full = f"{user['name']} - {user['department']}"
    if form[18] != my_full:
        flash("Chưa đến lượt bạn duyệt!", "danger")
        conn.close()
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        decision = request.form["decision"]
        current_user_full = f"{user['name']} - {user['department']}"

        if decision == "reject":
            c.execute("UPDATE qtkt_forms SET status = 'Từ chối', next_approver = ?, final_approver_name = ? WHERE id = ?",
                      (current_user_full, user['name'], form_id))
            conn.commit()
            flash("Đã TỪ CHỐI quyết toán!", "danger")
        else:
            if user["role"] == "BOD":
                c.execute("UPDATE qtkt_forms SET status = 'Đã duyệt', next_approver = ?, final_approver_name = ? WHERE id = ?",
                          (current_user_full, user['name'], form_id))
                conn.commit()
                flash("BOD đã DUYỆT HOÀN TẤT!", "success")
            else:
                next_person = request.form.get("next_approver")
                if next_person:
                    c.execute("UPDATE qtkt_forms SET next_approver = ? WHERE id = ?", (next_person, form_id))
                    conn.commit()
                    flash(f"Đã duyệt → Chuyển cho: {next_person.split(' - ')[0]}", "success")

        conn.close()
        return redirect(url_for("dashboard"))

    approvers = [f"{v['name']} - {v['department']}" for k,v in USERS.items() if v["role"] in ["Manager","BOD"]]
    conn.close()
    return render_template("qtkt_approve.html", form=form, user=user, approvers=approvers, is_bod=(user["role"]=="BOD"))

@app.route("/uploads/<filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/list")
@login_required
def qtkt_list():
    user = session["user"]
    if user["role"] not in ["Manager", "BOD"]:
        flash("Bạn không có quyền!", "danger")
        return redirect(url_for("dashboard"))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM qtkt_forms ORDER BY id DESC")
    forms = c.fetchall()
    conn.close()
    return render_template("qtkt_list.html", user=user, forms=forms)

@app.route("/logout")
def logout():
    session.clear()
    flash("Đã đăng xuất!", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    print("="*80)
    print("HỆ THỐNG QUYẾT TOÁN TẠM ỨNG QTKT02-BM02 – HOÀN THIỆN 100%")
    print("✓ Đổi mật khẩu lần đầu bắt buộc")
    print("✓ Mật khẩu lưu vĩnh viễn – không reset khi chạy lại")
    print("✓ Người duyệt cuối hoạt động chính xác")
    print("http://0.0.0.0:5000")
    print("="*80)
    app.run(host="0.0.0.0", port=5000, debug=False)