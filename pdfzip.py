import os
import shutil
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pymupdf

LEVELS = {
    "轻度（清晰优先）": dict(dpi_threshold=200, dpi_target=150, quality=80),
    "标准（推荐）": dict(dpi_threshold=150, dpi_target=120, quality=65),
    "强力（体积优先）": dict(dpi_threshold=100, dpi_target=72, quality=45),
}


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def output_path(src):
    base, _ = os.path.splitext(src)
    out = f"{base}_压缩.pdf"
    i = 2
    while os.path.exists(out):
        out = f"{base}_压缩({i}).pdf"
        i += 1
    return out


def compress(src, level):
    out = output_path(src)
    tmp = out + ".tmp"
    with pymupdf.open(src) as doc:
        if doc.needs_pass:
            raise ValueError("文件有密码保护，无法压缩")
        doc.rewrite_images(**LEVELS[level])
        doc.subset_fonts()
        doc.save(tmp, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True, clean=True, use_objstms=1)
    before, after = os.path.getsize(src), os.path.getsize(tmp)
    if after >= before:
        os.remove(tmp)
        shutil.copyfile(src, out)
        after = before
    else:
        os.replace(tmp, out)
    return out, before, after


class App:
    def __init__(self, root):
        self.root = root
        self.files = []
        root.title("PDF 压缩工具")
        root.geometry("640x420")
        root.minsize(520, 340)

        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")
        ttk.Button(top, text="选择 PDF 文件…", command=self.pick).pack(side="left")
        ttk.Label(top, text="  压缩强度：").pack(side="left")
        self.level = tk.StringVar(value="标准（推荐）")
        ttk.Combobox(top, textvariable=self.level, values=list(LEVELS), state="readonly", width=16).pack(side="left")
        self.start_btn = ttk.Button(top, text="开始压缩", command=self.start, state="disabled")
        self.start_btn.pack(side="right")

        self.progress = ttk.Progressbar(root, mode="determinate")
        self.progress.pack(fill="x", padx=10)

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill="both", expand=True)
        self.log = tk.Text(frame, wrap="word", state="disabled", font=("Microsoft YaHei UI", 10))
        bar = ttk.Scrollbar(frame, command=self.log.yview)
        self.log.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.log.pack(side="left", fill="both", expand=True)
        self.write("点击「选择 PDF 文件…」，可多选。压缩后的文件保存在原文件所在目录，文件名加「_压缩」后缀，原文件不会改动。")

    def write(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def pick(self):
        files = filedialog.askopenfilenames(title="选择要压缩的 PDF", filetypes=[("PDF 文件", "*.pdf"), ("所有文件", "*.*")])
        if not files:
            return
        self.files = list(files)
        self.write(f"\n已选择 {len(self.files)} 个文件：")
        for f in self.files:
            self.write(f"  {f}")
        self.start_btn.configure(state="normal")

    def start(self):
        self.start_btn.configure(state="disabled")
        self.progress.configure(maximum=len(self.files), value=0)
        threading.Thread(target=self.run, args=(list(self.files), self.level.get()), daemon=True).start()

    def run(self, files, level):
        total_before = total_after = 0
        ok = 0
        for i, f in enumerate(files, 1):
            self.root.after(0, self.write, f"\n[{i}/{len(files)}] 正在压缩：{os.path.basename(f)}")
            try:
                out, before, after = compress(f, level)
            except Exception as e:
                self.root.after(0, self.write, f"  失败：{e}")
            else:
                ok += 1
                total_before += before
                total_after += after
                if after < before:
                    msg = f"  {human(before)} → {human(after)}（减少 {100 - after * 100 / before:.1f}%）\n  已保存：{out}"
                else:
                    msg = f"  该文件已无法进一步压缩，已原样复制为：{out}"
                self.root.after(0, self.write, msg)
            self.root.after(0, self.progress.configure, {"value": i})
        self.root.after(0, self.done, ok, len(files), total_before, total_after)

    def done(self, ok, n, before, after):
        self.write(f"\n完成：成功 {ok}/{n}，总计 {human(before)} → {human(after)}")
        self.start_btn.configure(state="normal")
        messagebox.showinfo("PDF 压缩工具", f"完成：成功 {ok}/{n}\n{human(before)} → {human(after)}")


def main():
    root = tk.Tk()
    app = App(root)
    files = [f for f in sys.argv[1:] if os.path.isfile(f)]
    if files:
        app.files = files
        app.write(f"\n已选择 {len(files)} 个文件：")
        for f in files:
            app.write(f"  {f}")
        app.start_btn.configure(state="normal")
    root.mainloop()


if __name__ == "__main__":
    main()
