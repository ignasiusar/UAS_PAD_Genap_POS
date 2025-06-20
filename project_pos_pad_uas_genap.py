import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# === PATH FILE ===
PATH_PRODUK = "E:/PROJECT_PAD/Dataset/produk_kelontong.csv"
PATH_TRANSAKSI = "E:/PROJECT_PAD/Dataset/transaksi.csv"

# === LOAD DATA PRODUK & TRANSAKSI ===
def load_produk():
    return pd.read_csv(PATH_PRODUK)

def load_transaksi():
    try:
        return pd.read_csv(PATH_TRANSAKSI)
    except FileNotFoundError:
        return pd.DataFrame(columns=["tanggal", "produk", "jumlah", "harga_satuan", "total"])

# === SIMPAN DATA PRODUK & TRANSAKSI ===
def simpan_produk(df):
    df.to_csv(PATH_PRODUK, index=False)

def simpan_transaksi(df):
    df.to_csv(PATH_TRANSAKSI, index=False)

# === CARI PRODUK BERDASARKAN NAMA ATAU ID ===
def cari_produk_stok(df, keyword):
    df_filtered = df[df["nama_produk"].str.contains(keyword, case=False, na=False) | df["id_produk"].astype(str).str.contains(keyword)]
    if df_filtered.empty:
        return None, None
    row = df_filtered.iloc[0]
    return row["nama_produk"], (row["harga_satuan"], row["stok"])

# === TAMBAH TRANSAKSI & UPDATE STOK ===
def tambah_transaksi(df_produk, df_transaksi, nama_produk, jumlah, tanggal=None):
    if tanggal is None:
        tanggal = datetime.now().strftime("%Y-%m-%d")

    _, hasil = cari_produk_stok(df_produk, nama_produk)
    if hasil is None:
        return "❌ Produk tidak ditemukan.", False

    harga, stok = hasil
    if jumlah > stok:
        return f"⚠️ Stok tidak cukup. Sisa stok: {stok}", False

    total = harga * jumlah
    df_transaksi.loc[len(df_transaksi)] = [tanggal, nama_produk, jumlah, harga, total]
    df_produk.loc[df_produk["nama_produk"] == nama_produk, "stok"] -= jumlah
    simpan_produk(df_produk)
    return f"✅ {jumlah}x {nama_produk} ditambahkan. Total: Rp{total:,}", True

# === INISIALISASI DATA ===
data_produk = load_produk()
data_transaksi = load_transaksi()
keranjang = []

# === SETUP GUI UTAMA ===
root = tk.Tk()
root.title("POS - Toko Kelontong")
root.geometry("1100x650")
root.configure(bg="#f4f6f7")

# === WARNA DAN FRAME ===
sidebar_bg = "#34495e"
content_bg = "#ecf0f1"
button_bg = "#2ecc71"
button_fg = "white"

frame_sidebar = tk.Frame(root, width=200, bg=sidebar_bg)
frame_sidebar.pack(side='left', fill='y')

frame_main = tk.Frame(root, bg=content_bg)
frame_main.pack(side='right', expand=True, fill='both')

# === CLEAR MAIN FRAME ===
def clear_main_frame():
    for widget in frame_main.winfo_children():
        widget.destroy()

# === HALAMAN UTAMA ===
def tampil_home():
    clear_main_frame()
    tk.Label(frame_main, text="Selamat Datang di Aplikasi POS Toko Kelontong", font=("Arial", 18, "bold"), bg=content_bg, fg="#2c3e50").pack(pady=50)
    tk.Label(frame_main, text="Gunakan menu di sebelah kiri untuk navigasi.", font=("Arial", 12), bg=content_bg).pack(pady=5)

# === TAMPIL LIST PRODUK DENGAN FILTER DAN FORM TAMBAH ===
def tampil_product_list():
    clear_main_frame()
    df_produk = load_produk()

    tk.Label(frame_main, text="Daftar Produk", font=("Arial", 16, "bold"), bg=content_bg).pack(pady=10)

    kategori_set = sorted(df_produk['kategori'].unique())
    selected_kategori = tk.StringVar()
    selected_kategori.set("Semua Kategori")

    def update_treeview():
        for item in tree_produk.get_children():
            tree_produk.delete(item)
        for _, row in df_produk.iterrows():
            if selected_kategori.get() != "Semua Kategori" and row["kategori"] != selected_kategori.get():
                continue
            tree_produk.insert("", "end", values=(row["id_produk"], row["nama_produk"], row["kategori"], f"Rp{row['harga_satuan']:,}", row["stok"]))

    filter_frame = tk.Frame(frame_main, bg=content_bg)
    filter_frame.pack(pady=5)
    tk.Label(filter_frame, text="Filter Kategori:", bg=content_bg).pack(side="left", padx=5)
    kategori_option = ttk.Combobox(filter_frame, textvariable=selected_kategori, values=["Semua Kategori"] + kategori_set, state="readonly")
    kategori_option.pack(side="left")
    kategori_option.bind("<<ComboboxSelected>>", lambda e: update_treeview())

    tree_produk = ttk.Treeview(frame_main, columns=("ID", "Produk", "Kategori", "Harga", "Stok"), show='headings')
    for col in tree_produk["columns"]:
        tree_produk.heading(col, text=col)
    tree_produk.pack(pady=10, fill='x')
    update_treeview()

    def open_form_tambah(data_lama=None):
        win = tk.Toplevel(root)
        win.title("Tambah Produk")
        win.geometry("300x300")

        form_entries = {}
        fields = ["ID", "Nama", "Kategori", "Harga", "Stok"]
        for i, label in enumerate(fields):
            tk.Label(win, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            ent = tk.Entry(win)
            ent.grid(row=i, column=1, padx=5, pady=5)
            if data_lama:
                ent.insert(0, data_lama.get(label.lower(), ""))
                if label.lower() == "id":
                    ent.config(state="readonly")
            form_entries[label.lower()] = ent

        def simpan():
            try:
                new_row = {
                    "id_produk": form_entries["id"].get(),
                    "nama_produk": form_entries["nama"].get(),
                    "kategori": form_entries["kategori"].get(),
                    "harga_satuan": int(form_entries["harga"].get()),
                    "stok": int(form_entries["stok"].get())
                }

                if not new_row["nama_produk"]:
                    raise ValueError("Nama produk kosong.")

                if data_lama is None and df_produk["id_produk"].astype(str).str.contains(new_row["id_produk"]).any():
                    messagebox.showerror("Duplikat", "ID produk sudah ada.")
                    return

                if data_lama:
                    idx = df_produk[df_produk["id_produk"] == new_row["id_produk"]].index[0]
                    df_produk.loc[idx, "stok"] += new_row["stok"]
                else:
                    df_produk.loc[len(df_produk)] = new_row

                simpan_produk(df_produk)
                win.destroy()
                tampil_product_list()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Simpan", bg=button_bg, fg="white", command=simpan).grid(row=6, column=1, pady=10)

    def on_tree_select(event):
        selected = tree_produk.focus()
        if selected:
            values = tree_produk.item(selected, 'values')
            id_produk = values[0]
            nama = values[1]
            stok = int(values[4])
            if messagebox.askyesno("Tambah Stok", f"Ingin menambah stok untuk '{nama}'?"):
                open_form_tambah({
                    "id": id_produk,
                    "nama": nama,
                    "kategori": values[2],
                    "harga": values[3].replace("Rp", "").replace(",", ""),
                    "stok": 0
                })

    tree_produk.bind("<Double-1>", on_tree_select)
    tk.Button(frame_main, text="➕ Tambah Produk Baru", bg=button_bg, fg="white", command=lambda: open_form_tambah()).pack()

# === TAMPIL POS (TRANSAKSI) ===
def tampil_pos():
    clear_main_frame()
    tk.Label(frame_main, text="Point Of Sales Toko Kelontong", font=("Arial", 16, "bold"), bg=content_bg).pack(pady=10)

    frame_top = tk.Frame(frame_main, bg=content_bg)
    frame_top.pack(pady=5)

    global entry_cari, entry_jumlah
    tk.Label(frame_top, text="Cari Produk", bg=content_bg).grid(row=0, column=0, padx=5, sticky="w")
    entry_cari = tk.Entry(frame_top, width=30)
    entry_cari.grid(row=0, column=1, padx=5)

    tk.Label(frame_top, text="Qty", bg=content_bg).grid(row=0, column=2, padx=5)
    entry_jumlah = tk.Entry(frame_top, width=10)
    entry_jumlah.grid(row=0, column=3, padx=5)

    tk.Button(frame_top, text="+ Tambah", bg=button_bg, fg=button_fg, command=tambah_ke_keranjang).grid(row=0, column=4, padx=5)

    global label_hasil
    label_hasil = tk.Label(frame_main, text="", bg=content_bg, fg="blue")
    label_hasil.pack(pady=5)

    global tree
    tree = ttk.Treeview(frame_main, columns=("Kode", "Produk", "Jumlah", "Harga", "Subtotal"), show='headings')
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(pady=10, fill='x')

    tk.Button(frame_main, text="🗑️ Hapus Item", bg="red", fg="white", command=hapus_dari_keranjang).pack(pady=5)

    frame_total = tk.Frame(frame_main, bg=content_bg)
    frame_total.pack(pady=10)

    global label_total, entry_uang
    label_total = tk.Label(frame_total, text="Total Belanja: Rp0", font=("Arial", 12, "bold"), bg=content_bg)
    label_total.grid(row=0, column=0, sticky='w', padx=5)

    tk.Label(frame_total, text="Uang Pembeli:", bg=content_bg).grid(row=1, column=0, sticky="w", padx=5)
    entry_uang = tk.Entry(frame_total)
    entry_uang.grid(row=1, column=1, padx=5)

    tk.Button(frame_total, text="Bayar & Struk", command=proses_pembayaran).grid(row=1, column=2, padx=10)

# === ✅ DIPERBAIKI AGAR DATA PRODUK & TRANSAKSI SELALU REALTIME ===
def tambah_ke_keranjang():
    nama = entry_cari.get()
    try:
        jumlah = int(entry_jumlah.get())
        if jumlah <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Input Salah", "Jumlah harus berupa angka positif.")
        return

    df_produk = load_produk()
    df_transaksi = load_transaksi()
    tanggal = datetime.now().strftime("%Y-%m-%d")
    pesan, sukses = tambah_transaksi(df_produk, df_transaksi, nama, jumlah, tanggal)

    if sukses:
        simpan_transaksi(df_transaksi)
        simpan_produk(df_produk)
        id_produk = df_produk[df_produk["nama_produk"].str.lower() == nama.lower()]["id_produk"].values[0]
        harga, _ = cari_produk_stok(df_produk, nama)[1]
        total = harga * jumlah
        keranjang.append((id_produk, nama, jumlah, harga, total))
        tampilkan_keranjang()
    label_hasil.config(text=pesan)

def tampilkan_keranjang():
    for row in tree.get_children():
        tree.delete(row)
    total = 0
    for id_produk, nama, jumlah, harga, subtotal in keranjang:
        total += subtotal
        tree.insert('', 'end', values=(id_produk, nama, jumlah, f"Rp{harga:,}", f"Rp{subtotal:,}"))
    label_total.config(text=f"Total Belanja: Rp{total:,}")
    return total

def hapus_dari_keranjang():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Tidak Ada Pilihan", "Pilih item dari keranjang dulu.")
        return
    values = tree.item(selected_item)["values"]
    nama_produk = values[1]
    global keranjang
    keranjang = [item for item in keranjang if item[1] != nama_produk]
    tampilkan_keranjang()

def proses_pembayaran():
    try:
        uang = int(entry_uang.get())
    except ValueError:
        messagebox.showerror("Input Salah", "Masukkan jumlah uang bayar.")
        return
    total_belanja = sum(item[4] for item in keranjang)
    if uang < total_belanja:
        messagebox.showwarning("Uang Kurang", "Uang tidak mencukupi untuk pembayaran.")
        return
    if not messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin memproses transaksi ini?"):
        return

    kembalian = uang - total_belanja
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    struk = f"\n===== STRUK PEMBAYARAN =====\nTanggal: {now}\n"
    for _, nama, jumlah, harga, total in keranjang:
        struk += f"{jumlah}x {nama} @ Rp{harga:,} = Rp{total:,}\n"
    struk += f"\nTotal : Rp{total_belanja:,}\nDibayar: Rp{uang:,}\nKembali: Rp{kembalian:,}\n===========================\n"
    messagebox.showinfo("Struk Pembayaran", struk)
    reset_semua()

# === ✅ Reset realtime (load ulang data) ===
def reset_semua():
    global keranjang
    keranjang = []
    tampilkan_keranjang()
    entry_cari.delete(0, tk.END)
    entry_jumlah.delete(0, tk.END)
    entry_uang.delete(0, tk.END)
    label_hasil.config(text="")
    label_total.config(text="Total Belanja: Rp0")

# === SIDEBAR MENU ===
tk.Label(frame_sidebar, text="POS Kelontong", bg=sidebar_bg, fg="white", font=("Arial", 14, "bold")).pack(pady=20)
menu_items = {
    "Home": tampil_home,
    "Product List": tampil_product_list,
    "POS": tampil_pos
}
for nama, fungsi in menu_items.items():
    tk.Button(frame_sidebar, text=nama, bg=button_bg, fg=button_fg, relief="flat", anchor="w", command=fungsi).pack(fill="x", padx=10, pady=5)

# === MULAI APLIKASI ===
tampil_home()
root.mainloop()
