"""Local API-key entry window. Never contacts a server or reads the clipboard on launch."""
from pathlib import Path
import os
import re
import tempfile
import tkinter as tk
from tkinter import messagebox, ttk


ROOT = Path(__file__).resolve().parent


def save_key(value, root=ROOT):
    key = value.strip()
    if not key or any(c.isspace() or c == '\x00' for c in key):
        raise ValueError('请粘贴完整的 API Key，内容不能包含空格或换行。')
    env_path = root / '.env'
    lines = env_path.read_text(encoding='utf-8-sig').splitlines() if env_path.exists() else []
    lines = [line for line in lines if not re.match(r'^\s*(?:export\s+)?ARK_API_KEY\s*=', line)]
    lines.append('ARK_API_KEY=' + key)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=root,
                                         prefix='.env.', suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write('\n'.join(lines) + '\n')
        os.replace(temporary, env_path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class KeyConfigWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('方舟 API Key 配置')
        self.geometry('640x300')
        self.minsize(540, 280)
        self.key = tk.StringVar()
        self.visible = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value='尚未输入密钥')
        body = ttk.Frame(self, padding=22)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text='粘贴你在火山方舟创建的 API Key',
                  font=('Microsoft YaHei UI', 12)).pack(anchor='w', pady=(0, 14))
        row = ttk.Frame(body)
        row.pack(fill='x')
        self.entry = ttk.Entry(row, textvariable=self.key, show='*', font=('Consolas', 11))
        self.entry.pack(side='left', fill='x', expand=True, ipady=5)
        ttk.Button(row, text='粘贴', command=self.paste).pack(side='left', padx=(10, 0))
        ttk.Checkbutton(body, text='显示密钥', variable=self.visible,
                        command=self.toggle_visibility).pack(anchor='w', pady=(10, 0))
        ttk.Label(body, textvariable=self.status).pack(anchor='w', pady=(8, 0))
        ttk.Label(body, text='密钥仅保存在本机。保存配置不会生成视频或扣费。',
                  wraplength=570).pack(anchor='w', pady=(10, 14))
        buttons = ttk.Frame(body)
        buttons.pack(fill='x')
        ttk.Button(buttons, text='保存配置', command=self.save).pack(side='right')
        ttk.Button(buttons, text='取消', command=self.destroy).pack(side='right', padx=(0, 10))
        self.key.trace_add('write', self.update_status)
        self.bind('<Return>', lambda event: self.save())
        self.bind('<Escape>', lambda event: self.destroy())
        self.entry.focus_set()

    def update_status(self, *_):
        length = len(self.key.get().strip())
        self.status.set(f'已输入 {length} 个字符' if length else '尚未输入密钥')

    def paste(self):
        try:
            value = self.clipboard_get()
        except tk.TclError:
            self.status.set('剪贴板里没有文字，请先在方舟页面复制 API Key。')
            return
        self.key.set(value.strip())
        self.entry.focus_set()

    def toggle_visibility(self):
        self.entry.configure(show='' if self.visible.get() else '*')

    def save(self):
        try:
            save_key(self.key.get())
        except ValueError as error:
            messagebox.showerror('请检查密钥', str(error), parent=self)
            return
        except (OSError, UnicodeError):
            messagebox.showerror('未能保存', '配置文件无法写入，请确认工作流文件夹可写。', parent=self)
            return
        self.key.set('')
        messagebox.showinfo('配置已保存', 'API Key 已保存到本地。\n尚未发起任何生成请求。', parent=self)
        self.destroy()


if __name__ == '__main__':
    KeyConfigWindow().mainloop()
