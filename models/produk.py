import pandas as pd
import os

class ProdukManager:
    def __init__(self, path_file):
        self.path_file = path_file
        self.df = self._load_data()
    
    def _load_data(self):
        if os.path.exists(self.path_file):
            return pd.read_csv(self.path_file)
        else:
            return pd.DataFrame(columns=["id_produk", "nama_produk", "kategori", "harga_satuan", "stok"])

    def simpan_data(self):
        self.df.to_csv(self.path_file, index=False)

    def cari_produk(self, keyword):
        hasil = self.df[
            self.df["nama_produk"].str.contains(keyword, case=False, na=False) |
            self.df["id_produk"].astype(str).str.contains(keyword)
        ]
        return hasil

    def tambah_produk(self, id_produk, nama_produk, kategori, harga_satuan, stok):
        if id_produk in self.df["id_produk"].astype(str).values:
            return False, "ID Produk sudah ada!"
        row = {
            "id_produk": id_produk,
            "nama_produk": nama_produk,
            "kategori": kategori,
            "harga_satuan": harga_satuan,
            "stok": stok
        }
        self.df.loc[len(self.df)] = row
        self.simpan_data()
        return True, "Produk Baru berhasil ditambahkan!"

    def tambah_stok(self, id_produk, stok_tambahan):
        if id_produk not in self.df["id_produk"].astype(str).values:
            return False, "Produk tidak ditemukan."
        idx = self.df[self.df["id_produk"] == id_produk].index[0]
        self.df.at[idx, "stok"] += stok_tambahan
        self.simpan_data()
        return True, "Stok berhasil diperbarui."

    def kurangi_stok_by_id(self, id_produk, jumlah):
        idx = self.df[self.df["id_produk"].astype(str) == str(id_produk)].index
        if idx.empty:
            return False, "❌ Produk tidak ditemukan."
        stok = self.df.at[idx[0], "stok"]
        if jumlah > stok:
            return False, f"⚠️ Stok tidak cukup. Sisa stok: {stok}"
        self.df.at[idx[0], "stok"] -= jumlah
        self.simpan_data()
        return True, "✅ Stok dikurangi."

    # Tambahkan ini agar bisa dipanggil dari POSView dengan nama produk
    def kurangi_stok(self, nama_produk, jumlah):
        idx = self.df[self.df["nama_produk"].str.lower() == nama_produk.lower()].index
        if idx.empty:
            return False, "❌ Produk tidak ditemukan."
        stok = self.df.at[idx[0], "stok"]
        if jumlah > stok:
            return False, f"⚠️ Stok tidak cukup. Sisa stok: {stok}"
        self.df.at[idx[0], "stok"] -= jumlah
        self.simpan_data()
        return True, "✅ Stok dikurangi."

    def update_produk(self, id_produk, nama, kategori, harga, stok):
        if id_produk not in self.df["id_produk"].values:
            return False, "ID produk tidak ditemukan"

        idx = self.df.index[self.df["id_produk"] == id_produk][0]
        self.df.at[idx, "nama_produk"] = nama
        self.df.at[idx, "kategori"] = kategori
        self.df.at[idx, "harga_satuan"] = harga
        self.df.at[idx, "stok"] = stok

        try:
            self.df.to_csv(self.path_file, index=False)
            return True, "Produk berhasil diperbarui"
        except Exception as e:
            return False, f"Gagal menyimpan: {e}"

