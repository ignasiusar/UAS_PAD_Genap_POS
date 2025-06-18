import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# === PATH FILE ===
PATH_PENJUALAN = "E:/PROJECT_PAD/Dataset/data_penjualan_kelontong.csv"
PATH_TRANSAKSI = "E:/PROJECT_PAD/Dataset/transaksi.csv"

# === LOAD DATA ===
def load_penjualan():
    return pd.read_csv(PATH_PENJUALAN)

def load_transaksi():
    try:
        return pd.read_csv(PATH_TRANSAKSI)
    except FileNotFoundError:
        return pd.DataFrame(columns=["tanggal", "produk", "jumlah", "harga_satuan", "total"])

# === SIMPAN DATA ===
def simpan_penjualan(df):
    df.to_csv(PATH_PENJUALAN, index=False)

def simpan_transaksi(df):
    df.to_csv(PATH_TRANSAKSI, index=False)

# === CARI PRODUK ===
def cari_produk_stok(df, nama_produk):
    df_produk = df[df["produk"] == nama_produk]
    if df_produk.empty:
        return nama_produk, None
    stok = df_produk.iloc[-1]["stok_akhir"]
    harga = df_produk.iloc[-1]["harga_satuan"]
    return nama_produk, (harga, stok)

# === TAMBAH TRANSAKSI ===
def tambah_transaksi(df_penjualan, df_transaksi, nama_produk, jumlah, tanggal=None):
    if tanggal is None:
        tanggal = datetime.now().strftime("%Y-%m-%d")
    
    _, hasil = cari_produk_stok(df_penjualan, nama_produk)
    if hasil is None:
        return "❌ Produk tidak ditemukan.", False

    harga, stok = hasil
    if jumlah > stok:
        return f"⚠️ Stok tidak cukup. Sisa stok: {stok}", False

    total = harga * jumlah
    df_transaksi.loc[len(df_transaksi)] = [tanggal, nama_produk, jumlah, harga, total]
    df_penjualan.loc[df_penjualan["produk"] == nama_produk, "stok_akhir"] -= jumlah
    return f"✅ {jumlah}x {nama_produk} ditambahkan. Total: Rp{total:,}", True

# === INISIALISASI ===
data_penjualan = load_penjualan()
data_transaksi = load_transaksi()
keranjang = []

# === GUI FUNCTIONS ===
def search_produk():
    nama = entry_cari.get()
    _, hasil = cari_produk_stok(data_penjualan, nama)
    if hasil:
        harga, stok_akhir = hasil
        label_hasil.config(text=f"✅ {nama} | Harga: Rp{harga:,} | Stok: {stok_akhir}")
    else:
        label_hasil.config(text="❌ Produk tidak ditemukan.")

def tambah_ke_keranjang():
    nama = entry_cari.get()
    try:
        jumlah = int(entry_jumlah.get())
        if jumlah <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Input Salah", "Jumlah harus berupa angka positif.")
        return

    tanggal = datetime.now().strftime("%Y-%m-%d")
    pesan, sukses = tambah_transaksi(data_penjualan, data_transaksi, nama, jumlah, tanggal)

    if sukses:
        harga, _ = cari_produk_stok(data_penjualan, nama)[1]
        total = harga * jumlah
        keranjang.append((nama, jumlah, harga, total))
        tampilkan_keranjang()
    label_hasil.config(text=pesan)

def tampilkan_keranjang():
    for row in tree.get_children():
        tree.delete(row)
    total = 0
    for nama, jumlah, harga, subtotal in keranjang:
        total += subtotal
        tree.insert('', 'end', values=(nama, jumlah, f"Rp{harga:,}", f"Rp{subtotal:,}"))
    label_total.config(text=f"Total Belanja: Rp{total:,}")
    return total

def proses_pembayaran():
    global data_transaksi
    try:
        uang = int(entry_uang.get())
    except ValueError:
        messagebox.showerror("Input Salah", "Masukkan jumlah uang bayar.")
        return

    total_belanja = sum(item[3] for item in keranjang)
    if uang < total_belanja:
        messagebox.showwarning("Uang Kurang", "Uang tidak mencukupi untuk pembayaran.")
        return

    kembalian = uang - total_belanja
    simpan_penjualan(data_penjualan)
    simpan_transaksi(data_transaksi)
    messagebox.showinfo("Berhasil", f"Pembayaran selesai.\nKembalian: Rp{kembalian:,}")
    reset_semua()

def reset_semua():
    global keranjang, data_transaksi
    keranjang = []
    data_transaksi = load_transaksi()
    tampilkan_keranjang()
    entry_cari.delete(0, tk.END)
    entry_jumlah.delete(0, tk.END)
    entry_uang.delete(0, tk.END)
    label_hasil.config(text="")
    label_total.config(text="Total Belanja: Rp0")

# === GUI SETUP ===
root = tk.Tk()
root.title("POS - Toko Kelontong")
root.geometry("1000x600")
root.resizable(False, False)

# === GAYA ===
sidebar_bg = "#2c3e50"
content_bg = "#ecf0f1"
button_bg = "#34495e"
button_fg = "white"

# === FRAME SIDEBAR ===
frame_sidebar = tk.Frame(root, width=180, bg=sidebar_bg)
frame_sidebar.pack(side='left', fill='y')

tk.Label(frame_sidebar, text="Grocery POS", bg=sidebar_bg, fg="white", font=("Arial", 14, "bold")).pack(pady=20)

menu_items = ["Home", "Category List", "Product List", "POS", "Regresi"]
for item in menu_items:
    btn = tk.Button(frame_sidebar, text=item, bg=button_bg, fg=button_fg, relief="flat", anchor="w")
    btn.pack(fill="x", padx=10, pady=5)

# === FRAME KONTEN UTAMA ===
frame_main = tk.Frame(root, bg=content_bg)
frame_main.pack(side='right', expand=True, fill='both')

tk.Label(frame_main, text="Point of Sales", font=("Arial", 16, "bold"), bg=content_bg).pack(pady=10)

# === FRAME TAMBAH PRODUK ===
frame_top = tk.Frame(frame_main, bg=content_bg)
frame_top.pack(pady=5)

tk.Label(frame_top, text="Select Product", bg=content_bg).grid(row=0, column=0, padx=5, sticky="w")
entry_cari = tk.Entry(frame_top, width=30)
entry_cari.grid(row=0, column=1, padx=5)

tk.Label(frame_top, text="Qty", bg=content_bg).grid(row=0, column=2, padx=5)
entry_jumlah = tk.Entry(frame_top, width=10)
entry_jumlah.grid(row=0, column=3, padx=5)

tk.Button(frame_top, text="+ Add Item", command=tambah_ke_keranjang).grid(row=0, column=4, padx=5)

# === LABEL HASIL PENCARIAN ===
label_hasil = tk.Label(frame_main, text="", bg=content_bg, fg="blue")
label_hasil.pack(pady=5)

# === TABEL KERANJANG ===
tree = ttk.Treeview(frame_main, columns=("Produk", "Jumlah", "Harga", "Subtotal"), show='headings')
for col in tree["columns"]:
    tree.heading(col, text=col)
tree.pack(pady=10, fill='x')

# === TOTAL & PEMBAYARAN ===
frame_total = tk.Frame(frame_main, bg=content_bg)
frame_total.pack(pady=10)

label_total = tk.Label(frame_total, text="Total Belanja: Rp0", font=("Arial", 12, "bold"), bg=content_bg)
label_total.grid(row=0, column=0, sticky='w', padx=5)

tk.Label(frame_total, text="Uang Pembeli:", bg=content_bg).grid(row=1, column=0, sticky="w", padx=5)
entry_uang = tk.Entry(frame_total)
entry_uang.grid(row=1, column=1, padx=5)

tk.Button(frame_total, text="Bayar & Simpan", command=proses_pembayaran).grid(row=1, column=2, padx=10)

# === JALANKAN APP ===
root.mainloop()
