import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

def jalankan_visualisasi():
    try:
        subprocess.Popen([sys.executable, "visualisasi_main.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menjalankan visualisasi:\n{e}")

def jalankan_pos():
    try:
        subprocess.Popen([sys.executable, "project_pos_pad_uas_genap.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menjalankan POS:\n{e}")

def keluar():
    root.destroy()

# === GUI MAIN MENU ===
root = tk.Tk()
root.title("Sistem Toko Kelontong - Menu Utama")
root.geometry("400x250")
root.resizable(False, False)

tk.Label(root, text="SISTEM TOKO KELONTONG", font=("Helvetica", 16, "bold")).pack(pady=20)

tk.Button(root, text="Visualisasi & Laporan", font=("Helvetica", 12), width=30, command=jalankan_visualisasi).pack(pady=10)
tk.Button(root, text=" Point of Sale (POS)", font=("Helvetica", 12), width=30, command=jalankan_pos).pack(pady=10)
tk.Button(root, text=" Keluar", font=("Helvetica", 12), width=30, command=keluar).pack(pady=10)

root.mainloop()
