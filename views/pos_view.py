import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from models.produk import ProdukManager
from models.transaksi import TransaksiManager
import datetime
from reportlab.pdfgen import canvas


class POSView(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="#f8f8f8")
        self.controller = controller
        self.pm = ProdukManager("Dataset/produk_kelontong.csv")
        self.tm = TransaksiManager("Dataset/transaksi.csv")
        self.keranjang = []

        tk.Label(self, text="🛒 Point of Sale (POS)", font=("Segoe UI", 16, "bold"), bg="#f8f8f8", fg="#2c3e50").pack(pady=10)

        # === FORM INPUT ===
        form = tk.LabelFrame(self, text="Add Product", bg="#ffffff", font=("Segoe UI", 10, "bold"), fg="#2c3e50", padx=10, pady=10, relief="groove")
        form.pack(pady=10, padx=10, fill="x")

        tk.Label(form, text="Nama Produk", bg="#ffffff").grid(row=0, column=0)
        self.ent_nama = tk.Entry(form)
        self.ent_nama.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Jumlah", bg="#ffffff").grid(row=0, column=2)
        self.ent_jumlah = tk.Entry(form, width=5)
        self.ent_jumlah.grid(row=0, column=3, padx=5)

        tk.Button(form, text="Tambah ke Keranjang", command=self.tambah_ke_keranjang, bg="#2980b9", fg="white").grid(row=0, column=4, padx=10)

        # === TABEL KERANJANG ===
        self.tree = ttk.Treeview(self, columns=("ID", "Nama", "Harga", "Jumlah", "Subtotal"), show="headings", height=8)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(pady=10)

        # === TOTAL & AKSI ===
        self.label_total = tk.Label(self, text="Total: Rp 0", font=("Segoe UI", 12, "bold"), bg="#f8f8f8", fg="#2c3e50")
        self.label_total.pack(pady=5)

        aksi = tk.Frame(self, bg="#f8f8f8")
        aksi.pack()

        tk.Button(aksi, text="Bayar", bg="#27ae60", fg="white", command=self.bayar).pack(side="left", padx=5)
        tk.Button(aksi, text="Reset", bg="#e74c3c", fg="white", command=self.reset_keranjang).pack(side="left", padx=5)

        # === INPUT PEMBAYARAN & KEMBALIAN ===
        pembayaran_frame = tk.Frame(self, bg="#f8f8f8")
        pembayaran_frame.pack(pady=5)

        tk.Label(pembayaran_frame, text="Pembayaran (Rp):", bg="#f8f8f8").grid(row=0, column=0, sticky="e")
        self.ent_bayar = tk.Entry(pembayaran_frame, width=10)
        self.ent_bayar.grid(row=0, column=1, padx=5)

        self.label_kembalian = tk.Label(pembayaran_frame, text="Kembalian: Rp 0", font=("Segoe UI", 11), bg="#f8f8f8", fg="#2c3e50")
        self.label_kembalian.grid(row=0, column=2, padx=10)

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

        try:
            jumlah_bayar = int(self.ent_bayar.get())
        except ValueError:
            messagebox.showerror("Error", "Masukkan jumlah pembayaran yang valid")
            return

        total = sum(item["subtotal"] for item in self.keranjang)

        if jumlah_bayar < total:
            messagebox.showwarning("Pembayaran Kurang", f"Total belanja Rp {total:,}, pembayaran Rp {jumlah_bayar:,}")
            return

        kembalian = jumlah_bayar - total
        self.label_kembalian.config(text=f"Kembalian: Rp {kembalian:,}")

        tanggal = datetime.date.today().isoformat()

        for item in self.keranjang:
            self.tm.tambah_transaksi(item["id"], item["nama"], item["jumlah"], item["subtotal"], tanggal)
            sukses, pesan = self.pm.kurangi_stok(item["nama"], item["jumlah"])
            if not sukses:
                messagebox.showwarning("Stok", pesan)
                return

        self.pm.simpan_data()
        self.tm.simpan_data()
        self.tampilkan_struk(total, jumlah_bayar, kembalian)
        self.reset_keranjang()
    def reset_keranjang(self):
        self.keranjang = []
        self.update_keranjang()
        self.ent_bayar.delete(0, 'end')
        self.label_kembalian.config(text="Kembalian: Rp 0")


    def tampilkan_struk(self, total, bayar, kembalian):
        struk_win = tk.Toplevel(self)
        struk_win.title("Receipt")

        receipt_text = f"Grocery POS\nTanggal: {datetime.date.today()}\n\n"
        receipt_text += f"{'Qty':<5}{'Nama':<15}{'Harga':<10}{'Total':<10}\n"
        receipt_text += "-" * 40 + "\n"

        for item in self.keranjang:
            receipt_text += f"{item['jumlah']:<5}{item['nama']:<15}{item['harga']:<10}{item['subtotal']:<10}\n"

        receipt_text += "-" * 40 + "\n"
        receipt_text += f"Total         : Rp {total:,}\n"
        receipt_text += f"Bayar         : Rp {bayar:,}\n"
        receipt_text += f"Kembalian     : Rp {kembalian:,}\n"

        text_box = tk.Text(struk_win, height=20, width=45)
        text_box.insert(tk.END, receipt_text)
        text_box.pack()

        tk.Button(struk_win, text="Export PDF", command=lambda: self.export_pdf(receipt_text)).pack(pady=10)

    def export_pdf(self, text):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if path:
            c = canvas.Canvas(path)
            y = 800
            for line in text.split("\n"):
                c.drawString(40, y, line)
                y -= 15
            c.save()
            messagebox.showinfo("Sukses", f"Struk disimpan sebagai PDF:\n{path}")
