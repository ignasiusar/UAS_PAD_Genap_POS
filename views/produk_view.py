import tkinter as tk
from tkinter import ttk, messagebox
from models.produk import ProdukManager

class ProductPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#e8f0f2")
        self.pm = ProdukManager("E:/PROJECT_PAD/Dataset/produk_kelontong.csv")

        # === JUDUL
        tk.Label(self, text="Daftar Produk", font=("Segoe UI", 16, "bold"), bg="#e8f0f2").pack(pady=10)

        # === FILTER KATEGORI
        filter_frame = tk.Frame(self, bg="#e8f0f2")
        filter_frame.pack(pady=(0, 10))

        tk.Label(filter_frame, text="Filter Kategori:", bg="#e8f0f2").pack(side="left", padx=5)

        self.kategori_var = tk.StringVar()
        self.kategori_combo = ttk.Combobox(filter_frame, textvariable=self.kategori_var, state="readonly")
        self.kategori_combo.pack(side="left")
        self.kategori_combo.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        self.update_kategori_list()

        # === TABEL PRODUK
        self.tree = ttk.Treeview(self, columns=("ID", "Nama", "Kategori", "Harga", "Stok"), show="headings", height=10)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(pady=10)

        # Bind klik dua kali setelah tree dibuat
        self.tree.bind("<Double-1>", self.buka_form_update)

        # === FORM TAMBAH PRODUK
        form_frame = tk.Frame(self, bg="#e8f0f2")
        form_frame.pack(pady=10)

        labels = ["ID", "Nama", "Kategori", "Harga", "Stok"]
        self.entries = {}

        for i, label in enumerate(labels):
            row = i // 2
            col = (i % 2) * 2

            tk.Label(form_frame, text=label, bg="#e8f0f2").grid(row=row, column=col, padx=5, pady=5, sticky="e")
            ent = tk.Entry(form_frame, width=20)
            ent.grid(row=row, column=col + 1, padx=5, pady=5, sticky="w")
            self.entries[label.lower()] = ent

        # === TOMBOL TAMBAH
        btn_add = tk.Button(self, text="Tambah Produk", bg="#27ae60", fg="white", command=self.tambah_produk)
        btn_add.pack(pady=10)

        # === LOAD DATA AWAL
        self.load_data()

    def update_kategori_list(self):
        kategori_list = sorted(self.pm.df["kategori"].dropna().unique().tolist())
        self.kategori_combo["values"] = ["Semua"] + kategori_list
        self.kategori_combo.set("Semua")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        df_filtered = self.pm.df.copy()
        selected_kat = self.kategori_var.get()
        if selected_kat != "Semua" and selected_kat != "":
            df_filtered = df_filtered[df_filtered["kategori"] == selected_kat]

        for _, row in df_filtered.iterrows():
            self.tree.insert("", "end", values=(
                row["id_produk"], row["nama_produk"], row["kategori"],
                row["harga_satuan"], row["stok"]
            ))

    def tambah_produk(self):
        id_produk = self.entries["id"].get()
        nama = self.entries["nama"].get()
        kategori = self.entries["kategori"].get()
        try:
            harga = int(self.entries["harga"].get())
            stok = int(self.entries["stok"].get())
        except ValueError:
            messagebox.showerror("Error", "Harga dan Stok harus angka")
            return

        sukses, pesan = self.pm.tambah_produk(id_produk, nama, kategori, harga, stok)
        if sukses:
            for ent in self.entries.values():
                ent.delete(0, 'end')
            self.update_kategori_list()
            self.load_data()

        messagebox.showinfo("Info", pesan)

    def buka_form_update(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return
        values = self.tree.item(selected_item, "values")
        if not values:
            return

        update_win = tk.Toplevel(self)
        update_win.title("Update Produk")
        update_win.geometry("300x300")
        update_win.grab_set()

        fields = ["ID", "Nama", "Kategori", "Harga", "Stok"]
        update_entries = {}

        for i, field in enumerate(fields):
            tk.Label(update_win, text=field).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            ent = tk.Entry(update_win)
            ent.grid(row=i, column=1, padx=10, pady=5)
            ent.insert(0, values[i])
            if field == "ID":
                ent.config(state="readonly")
            update_entries[field.lower()] = ent

        def simpan_update():
            try:
                harga = int(update_entries["harga"].get())
                stok = int(update_entries["stok"].get())
            except ValueError:
                messagebox.showerror("Error", "Harga dan Stok harus angka")
                return

            sukses, pesan = self.pm.update_produk(
                id_produk=update_entries["id"].get(),
                nama=update_entries["nama"].get(),
                kategori=update_entries["kategori"].get(),
                harga=harga,
                stok=stok
            )

            if sukses:
                messagebox.showinfo("Info", "Produk berhasil diperbarui")
                self.update_kategori_list()
                self.load_data()
                update_win.destroy()
            else:
                messagebox.showerror("Error", pesan)

        tk.Button(update_win, text="Simpan", command=simpan_update, bg="#2980b9", fg="white").grid(
            row=len(fields), column=0, columnspan=2, pady=15
        )
