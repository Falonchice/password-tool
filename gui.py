import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import pyperclip
import random
import string
import os
import time
from password_db import PasswordDB

DB_FILE = "passwords.db"
LOCK_TIMEOUT = 3 * 60  # 3 minutes

class PasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("本地密码管理器")
        self.db = None
        self.last_active = time.time()
        self.locked = True
        self.master_password = ""
        self.setup_login()

    def setup_login(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.locked = True
        frame = tk.Frame(self.root)
        frame.pack(padx=20, pady=20)
        tk.Label(frame, text="请输入主密码:").grid(row=0, column=0, sticky="w")
        self.pass_entry = tk.Entry(frame, show="*", width=24)
        self.pass_entry.grid(row=0, column=1)
        self.pass_entry.focus_set()
        tk.Button(frame, text="登录", command=self.try_login).grid(row=1, column=0, columnspan=2, pady=10)
        self.root.bind('<Return>', lambda e: self.try_login())

    def try_login(self):
        pwd = self.pass_entry.get()
        try:
            self.db = PasswordDB(DB_FILE, pwd)
            self.master_password = pwd
            self.locked = False
            self.show_main()
        except Exception:
            messagebox.showerror("错误", "主密码错误或数据库损坏！")

    def show_main(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.root.geometry("720x430")
        self.last_active = time.time()
        self.root.after(1000, self.check_lock)
        # Top control bar
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=5, pady=2)
        tk.Button(top, text="新增", command=self.add_entry).pack(side="left")
        tk.Button(top, text="编辑", command=self.edit_entry).pack(side="left")
        tk.Button(top, text="删除", command=self.delete_entry).pack(side="left")
        tk.Button(top, text="导入", command=self.import_entries).pack(side="left")
        tk.Button(top, text="导出", command=self.export_entries).pack(side="left")
        tk.Button(top, text="生成密码", command=self.generate_password).pack(side="left")
        tk.Button(top, text="保存", command=self.save_db).pack(side="left")
        tk.Button(top, text="锁定", command=self.setup_login).pack(side="right")
        self.search_var = tk.StringVar()
        tk.Entry(top, textvariable=self.search_var, width=20).pack(side="right", padx=5)
        tk.Button(top, text="搜索", command=self.refresh_list).pack(side="right")
        # Table
        columns = ("name", "username", "password", "remark")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", selectmode="browse")
        for col, colname in zip(columns, ["名称", "账号", "密码", "备注"]):
            self.tree.heading(col, text=colname)
            self.tree.column(col, width=150 if col != "remark" else 200)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.copy_password)
        self.refresh_list()

    def check_lock(self):
        if not self.locked:
            now = time.time()
            if now - self.last_active > LOCK_TIMEOUT:
                messagebox.showinfo("锁定", "长时间无操作，已自动锁定。")
                self.setup_login()
                return
        self.root.after(1000, self.check_lock)

    def refresh_list(self):
        self.last_active = time.time()
        for item in self.tree.get_children():
            self.tree.delete(item)
        kw = self.search_var.get().strip()
        if kw:
            items = self.db.search(kw)
        else:
            items = list(enumerate(self.db.data))
        for i, entry in items:
            self.tree.insert("", "end", iid=str(i), values=(entry['name'], entry['username'], "******", entry['remark']))

    def add_entry(self):
        self.last_active = time.time()
        d = EntryDialog(self.root, "新增条目")
        if d.result:
            name, username, password, remark = d.result
            self.db.add_entry(name, username, password, remark)
            self.refresh_list()

    def edit_entry(self):
        self.last_active = time.time()
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请选择要编辑的条目。")
            return
        idx = int(sel[0])
        entry = self.db.data[idx]
        d = EntryDialog(self.root, "编辑条目", entry)
        if d.result:
            name, username, password, remark = d.result
            self.db.update_entry(idx, name, username, password, remark)
            self.refresh_list()

    def delete_entry(self):
        self.last_active = time.time()
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请选择要删除的条目。")
            return
        idx = int(sel[0])
        if messagebox.askyesno("确认", "确定要删除该条目吗？"):
            self.db.delete_entry(idx)
            self.refresh_list()

    def copy_password(self, event):
        self.last_active = time.time()
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        pwd = self.db.data[idx]['password']
        pyperclip.copy(pwd)
        messagebox.showinfo("已复制", "密码已复制到剪贴板。")

    def export_entries(self):
        self.last_active = time.time()
        fname = filedialog.asksaveasfilename(title="导出为JSON", defaultextension=".json", filetypes=[("JSON files","*.json")])
        if fname:
            self.db.export_to_json(fname)
            messagebox.showinfo("导出", "导出成功！")

    def import_entries(self):
        self.last_active = time.time()
        fname = filedialog.askopenfilename(title="导入JSON", filetypes=[("JSON files","*.json")])
        if fname:
            try:
                self.db.import_from_json(fname)
                self.refresh_list()
                messagebox.showinfo("导入", "导入成功！")
            except Exception as e:
                messagebox.showerror("导入失败", f"导入失败：{e}")

    def generate_password(self):
        self.last_active = time.time()
        length = simpledialog.askinteger("生成密码", "输入密码长度", initialvalue=16, minvalue=4, maxvalue=64)
        if not length:
            return
        chars = string.ascii_letters + string.digits + string.punctuation
        pwd = ''.join(random.choice(chars) for _ in range(length))
        pyperclip.copy(pwd)
        messagebox.showinfo("随机密码", f"已生成并复制到剪贴板：\n{pwd}")

    def save_db(self):
        self.last_active = time.time()
        self.db.save()
        messagebox.showinfo("保存", "已保存到本地。")

class EntryDialog(simpledialog.Dialog):
    def __init__(self, parent, title, entry=None):
        self.entry = entry
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="名称:").grid(row=0, column=0)
        tk.Label(master, text="账号:").grid(row=1, column=0)
        tk.Label(master, text="密码:").grid(row=2, column=0)
        tk.Label(master, text="备注:").grid(row=3, column=0)
        self.e_name = tk.Entry(master, width=30)
        self.e_username = tk.Entry(master, width=30)
        self.e_password = tk.Entry(master, width=30)
        self.e_remark = tk.Entry(master, width=30)
        self.e_name.grid(row=0, column=1)
        self.e_username.grid(row=1, column=1)
        self.e_password.grid(row=2, column=1)
        self.e_remark.grid(row=3, column=1)
        if self.entry:
            self.e_name.insert(0, self.entry['name'])
            self.e_username.insert(0, self.entry['username'])
            self.e_password.insert(0, self.entry['password'])
            self.e_remark.insert(0, self.entry['remark'])
        return self.e_name

    def apply(self):
        name = self.e_name.get().strip()
        username = self.e_username.get().strip()
        password = self.e_password.get().strip()
        remark = self.e_remark.get().strip()
        if not name or not username or not password:
            self.result = None
        else:
            self.result = (name, username, password, remark)

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerGUI(root)
    root.mainloop()