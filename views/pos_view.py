import tkinter as tk
from tkinter import ttk, messagebox
from models.produk import ProdukManager
from models.transaksi import TransaksiManager
import datetime

class POSView(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="#f8f8f8")
        self.controller = controller
        self.pm = ProdukManager("Dataset/produk_kelontong.csv")
        self.tm = TransaksiManager("Dataset/transaksi.csv")
        self.keranjang = []

        tk.Label(self, text="🛒 Point of Sale (POS)", font=("Segoe UI", 14, "bold"), bg="#f8f8f8").pack(pady=10)

        # === FORM INPUT ===
        form = tk.Frame(self, bg="#f8f8f8")
        form.pack()

        tk.Label(form, text="Nama Produk", bg="#f8f8f8").grid(row=0, column=0)
        self.ent_nama = tk.Entry(form)
        self.ent_nama.grid(row=0, column=1)

        tk.Label(form, text="Jumlah", bg="#f8f8f8").grid(row=0, column=2)
        self.ent_jumlah = tk.Entry(form, width=5)
        self.ent_jumlah.grid(row=0, column=3)

        tk.Button(form, text="Tambah ke Keranjang", command=self.tambah_ke_keranjang, bg="#3498db", fg="white").grid(row=0, column=4, padx=10)

        # === TABEL KERANJANG ===
        self.tree = ttk.Treeview(self, columns=("ID", "Nama", "Harga", "Jumlah", "Subtotal"), show="headings", height=8)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(pady=10)

        # === TOTAL & AKSI ===
        self.label_total = tk.Label(self, text="Total: Rp 0", font=("Segoe UI", 12, "bold"), bg="#f8f8f8")
        self.label_total.pack(pady=5)

        aksi = tk.Frame(self, bg="#f8f8f8")
        aksi.pack()

        tk.Button(aksi, text="Bayar", bg="#2ecc71", fg="white", command=self.bayar).pack(side="left", padx=5)
        tk.Button(aksi, text="Reset", bg="#e74c3c", fg="white", command=self.reset_keranjang).pack(side="left", padx=5)

    def tambah_ke_keranjang(self):
        nama_produk = self.ent_nama.get().strip()
        try:
            jumlah = int(self.ent_jumlah.get())
        except ValueError:
            messagebox.showerror("Error", "Jumlah harus berupa angka")
            return

        produk = self.pm.df[self.pm.df["nama_produk"].str.lower() == nama_produk.lower()]
        if produk.empty:
            messagebox.showerror("Error", "Produk tidak ditemukan")
            return

        row = produk.iloc[0]
        if row["stok"] < jumlah:
            messagebox.showwarning("Stok Tidak Cukup", f"Stok tersisa: {row['stok']}")
            return

        subtotal = jumlah * row["harga_satuan"]
        self.keranjang.append({
            "id": row["id_produk"],
            "nama": row["nama_produk"],
            "harga": row["harga_satuan"],
            "jumlah": jumlah,
            "subtotal": subtotal
        })

        self.update_keranjang()
        self.ent_nama.delete(0, 'end')
        self.ent_jumlah.delete(0, 'end')

    def update_keranjang(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        total = 0
        for item in self.keranjang:
            self.tree.insert("", "end", values=(item["id"], item["nama"], item["harga"], item["jumlah"], item["subtotal"]))
            total += item["subtotal"]
        self.label_total.config(text=f"Total: Rp {total:,}")

    def bayar(self):
        if not self.keranjang:
            messagebox.showwarning("Kosong", "Keranjang masih kosong")
            return
        tanggal = datetime.date.today().isoformat()
        for item in self.keranjang:
            self.tm.tambah_transaksi(item["id"], item["jumlah"], item["subtotal"], tanggal)
            sukses, pesan = self.pm.kurangi_stok(item["nama"], item["jumlah"])
        if not sukses:
            messagebox.showwarning("Stok", pesan)
        
        self.pm.kurangi_stok(item["nama"], item["jumlah"])
        self.pm.simpan_data()
        self.tm.simpan_data()
        messagebox.showinfo("Transaksi Berhasil", "✅ Transaksi berhasil disimpan")
        self.reset_keranjang()

    def reset_keranjang(self):
        self.keranjang = []
        self.update_keranjang()
