import tkinter as tk
from tkinter import ttk, messagebox
from models.produk import ProdukManager

class ProductPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#e8f0f2")
        self.pm = ProdukManager("E:/PROJECT_PAD/Dataset/produk_kelontong.csv")

        # Judul
        tk.Label(self, text="Daftar Produk", font=("Segoe UI", 14, "bold"), bg="#e8f0f2").pack(pady=10)

        # Tabel
        self.tree = ttk.Treeview(self, columns=("ID", "Nama", "Kategori", "Harga", "Stok"), show="headings", height=8)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(pady=10)

        # Form tambah
        form_frame = tk.Frame(self, bg="#e8f0f2")
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="ID", bg="#e8f0f2").grid(row=0, column=0)
        self.ent_id = tk.Entry(form_frame, width=10)
        self.ent_id.grid(row=0, column=1)

        tk.Label(form_frame, text="Nama", bg="#e8f0f2").grid(row=0, column=2)
        self.ent_nama = tk.Entry(form_frame, width=15)
        self.ent_nama.grid(row=0, column=3)

        tk.Label(form_frame, text="Kategori", bg="#e8f0f2").grid(row=1, column=0)
        self.ent_kategori = tk.Entry(form_frame, width=10)
        self.ent_kategori.grid(row=1, column=1)

        tk.Label(form_frame, text="Harga", bg="#e8f0f2").grid(row=1, column=2)
        self.ent_harga = tk.Entry(form_frame, width=10)
        self.ent_harga.grid(row=1, column=3)

        tk.Label(form_frame, text="Stok", bg="#e8f0f2").grid(row=2, column=0)
        self.ent_stok = tk.Entry(form_frame, width=10)
        self.ent_stok.grid(row=2, column=1)

        # Tombol
        btn_add = tk.Button(self, text="Tambah Produk", bg="#27ae60", fg="white", command=self.tambah_produk)
        btn_add.pack(pady=10)

        self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for _, row in self.pm.df.iterrows():
            self.tree.insert("", "end", values=(
                row["id_produk"], row["nama_produk"], row["kategori"],
                row["harga_satuan"], row["stok"]
            ))

    def tambah_produk(self):
        id_produk = self.ent_id.get()
        nama = self.ent_nama.get()
        kategori = self.ent_kategori.get()
        try:
            harga = int(self.ent_harga.get())
            stok = int(self.ent_stok.get())
        except ValueError:
            messagebox.showerror("Error", "Harga dan Stok harus angka")
            return

        sukses, pesan = self.pm.tambah_produk(id_produk, nama, kategori, harga, stok)
        if sukses:
            self.load_data()
            self.ent_id.delete(0, 'end')
            self.ent_nama.delete(0, 'end')
            self.ent_kategori.delete(0, 'end')
            self.ent_harga.delete(0, 'end')
            self.ent_stok.delete(0, 'end')
        messagebox.showinfo("Info", pesan)
