import pandas as pd
import os
from datetime import datetime

class TransaksiManager:
    def __init__(self, path_file):
        self.path_file = path_file
        self.df = self._load_data()

    def _load_data(self):
        if os.path.exists(self.path_file):
            return pd.read_csv(self.path_file)
        else:
            return pd.DataFrame(columns=["tanggal","produk","jumlah","harga_satuan","total"])
    
    def simpan_data(self):
        self.df.to_csv(self.path_file, index=False)
    
    def tambah_transaksi(self,nama_produk,jumlah,harga,tanggal=None):
        if tanggal is None:
            tanggal = datetime.now().strftime("%Y-%m-%d")

        total = harga*jumlah
        new_row = {
            "tanggal":tanggal
            ,"produk":nama_produk
            ,"jumlah":jumlah
            ,"harga_satuan":harga
            ,"total":total
        }
        self.df.loc[len(self.df)]= new_row
        self.simpan_data()
        return True, f"Transaksi Berhasil. Total Belanja : Rp{total:,}"