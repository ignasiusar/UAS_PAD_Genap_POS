import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
from views.produk_view import ProductPage
from views.pos_view import POSView

def jalankan_visualisasi():
    try:
        subprocess.Popen([sys.executable, "visualisasi_main.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menjalankan visualisasi:\n{e}")

def jalankan_daftar():
    try:
        new_window = tk.Toplevel(root)
        new_window.title("Daftar Produk")
        new_window.geometry("800x500")  # Atur sesuai ukuran yang kamu mau

        halaman_produk = ProductPage(new_window)
        halaman_produk.pack(fill="both", expand=True)
    except Exception as e:
        messagebox.showerror("Error", f"Gagal membuka POS:\n{e}")

def jalankan_pos():
    new_window = tk.Toplevel(root)
    new_window.title("Point of Sale")
    new_window.geometry("900x600")
    POSView(new_window).pack(fill="both", expand=True)

def keluar():
    root.destroy()

# === GUI MAIN MENU ===
root = tk.Tk()
root.title("Sistem Toko Kelontong - Menu Utama")
root.geometry("400x250")
root.resizable(False, False)

tk.Label(root, text="SISTEM TOKO KELONTONG", font=("Segoe UI", 16, "bold")).pack(pady=20)

tk.Button(root, text="Visualisasi & Laporan", font=("Segoe UI", 12), width=30, command=jalankan_visualisasi).pack(pady=10)
tk.Button(root, text=" Daftar Produk", font=("Segoe UI", 12), width=30, command=jalankan_daftar).pack(pady=10)
tk.Button(root, text=" Point Of Sales (POS)", font=("Segoe UI", 12), width=30, command=jalankan_pos).pack(pady=10)
tk.Button(root, text=" Keluar", font=("Segoe UI", 12), width=30, command=keluar).pack(pady=10)

root.mainloop()
