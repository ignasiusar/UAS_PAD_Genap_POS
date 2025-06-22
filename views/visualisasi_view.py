import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class VisualisasiPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#f5f5f5")
        tk.Label(self, text="📊 Visualisasi Data", font=("Segoe UI", 16, "bold"), bg="#f5f5f5").pack(pady=10)

        # Load & gabungkan data awal
        self.df_produk = pd.read_csv("Dataset/produk_kelontong.csv")
        self.df_transaksi = pd.read_csv("Dataset/transaksi.csv")
        self.df = pd.merge(self.df_transaksi, self.df_produk, on="id_produk")
        self.df["tanggal"] = pd.to_datetime(self.df["tanggal"])
        self.df["bulan"] = self.df["tanggal"].dt.to_period("M").astype(str)

        # Dropdown filter bulan
        filter_frame = tk.Frame(self, bg="#f5f5f5")
        filter_frame.pack(pady=(5, 0))

        tk.Label(filter_frame, text="Pilih Bulan:", bg="#f5f5f5").pack(side="left", padx=5)
        self.bulan_var = tk.StringVar()
        self.bulan_combo = ttk.Combobox(filter_frame, textvariable=self.bulan_var, state="readonly")
        self.bulan_combo["values"] = sorted(self.df["bulan"].unique(), reverse=True)
        self.bulan_combo.current(0)
        self.bulan_combo.pack(side="left", padx=5)
        self.bulan_combo.bind("<<ComboboxSelected>>", self.update_visualisasi)

        # Tombol export
        ttk.Button(filter_frame, text="📁 Export CSV + Grafik", command=self.export_data).pack(side="right", padx=10)

        # Frame laporan
        self.tree_frame = tk.Frame(self, bg="#f5f5f5")
        self.tree_frame.pack(pady=(5, 15), padx=10, fill="x")
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("Bulan", "Total Transaksi", "Pendapatan", "Produk Terlaris", "Kategori Terlaris"),
            show="headings",
            height=1
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150)
        self.tree.pack(fill="x")

        # Frame untuk grafik
        self.canvas_frame = tk.Frame(self, bg="#f5f5f5")
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas = None

        # Inisialisasi tampilan pertama
        self.update_visualisasi()

    def update_visualisasi(self, event=None):
        bulan_terpilih = self.bulan_var.get()
        df_bulan = self.df[self.df["bulan"] == bulan_terpilih]

        # Ringkasan bulanan
        total_transaksi = df_bulan.shape[0]
        total_pendapatan = df_bulan["total"].sum()
        produk_terlaris = df_bulan.groupby("nama_produk")["jumlah"].sum().idxmax()
        kategori_terlaris = df_bulan.groupby("kategori")["jumlah"].sum().idxmax()

        # Update Treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.tree.insert("", "end", values=(
            bulan_terpilih,
            total_transaksi,
            f"Rp {total_pendapatan:,.0f}",
            produk_terlaris,
            kategori_terlaris
        ))

        # Klasifikasi Produk Laku vs Tidak Laku (threshold >= 10 unit)
        produk_terjual = df_bulan.groupby("nama_produk")["jumlah"].sum()
        klasifikasi = produk_terjual.apply(lambda x: "Laku" if x >= 10 else "Tidak Laku")
        hasil_klasifikasi = pd.DataFrame({
            "Jumlah Terjual": produk_terjual,
            "Status": klasifikasi
        })

        # Siapkan figure dan subplots
        fig = Figure(figsize=(13, 24), dpi=100)
        fig.subplots_adjust(hspace=0.8)

        # Grafik 1: Penjualan per Kategori
        ax1 = fig.add_subplot(411)
        kategori_jual = df_bulan.groupby("kategori")["jumlah"].sum().sort_values()
        kategori_jual.plot(kind="barh", color="#3498db", ax=ax1)
        ax1.set_title("📦 Visualisasi 1: Jumlah Penjualan per Kategori")
        ax1.set_xlabel("Jumlah Terjual")

        # Grafik 2: Pendapatan Bulanan
        ax2 = fig.add_subplot(412)
        pendapatan_bulanan = self.df.groupby("bulan")["total"].sum().sort_index()
        pendapatan_bulanan.plot(marker='o', color="#2ecc71", ax=ax2)
        ax2.set_title("📈 Visualisasi 2: Pendapatan Bulanan (Semua Bulan)")
        ax2.set_ylabel("Pendapatan (Rp)")
        ax2.tick_params(axis='x', rotation=45)

        # Grafik 3: Produk Terlaris
        ax3 = fig.add_subplot(413)
        terlaris = df_bulan.groupby("nama_produk")["jumlah"].sum().sort_values(ascending=False).head(5)
        sns.barplot(x=terlaris.values, y=terlaris.index, palette="magma", ax=ax3)
        ax3.set_title("🔥 Visualisasi 3: Top 5 Produk Terlaris")
        ax3.set_xlabel("Jumlah Terjual")

        # Grafik 4: Klasifikasi Produk
        ax4 = fig.add_subplot(414)
        status_count = hasil_klasifikasi["Status"].value_counts()
        ax4.pie(status_count, labels=status_count.index, autopct="%1.1f%%", startangle=90, colors=["#2ecc71", "#e74c3c"])
        ax4.set_title("🧮 Visualisasi 4: Proporsi Produk Laku vs Tidak Laku")

        fig.tight_layout(pad=4.0)

        # Render grafik
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Simpan grafik untuk export
        self.last_fig = fig
        self.last_summary = {
            "Bulan": bulan_terpilih,
            "Total Transaksi": total_transaksi,
            "Pendapatan": total_pendapatan,
            "Produk Terlaris": produk_terlaris,
            "Kategori Terlaris": kategori_terlaris
        }

    def export_data(self):
        bulan = self.last_summary["Bulan"]
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"laporan_{bulan}.csv"
        )
        if path:
            df_export = pd.DataFrame([self.last_summary])
            df_export.to_csv(path, index=False)
            img_path = path.replace(".csv", ".png")
            self.last_fig.savefig(img_path)
            messagebox.showinfo("Export Berhasil", f"✅ CSV & grafik disimpan:\n{path}\n{img_path}")
