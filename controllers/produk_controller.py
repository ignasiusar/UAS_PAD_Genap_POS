from models.produk import ProdukManager

class ProdukController:
    def __init__(self,path_file):
        self.model = ProdukManager(path_file)

    def tamnbah_produk(self,id_produk,nama_produk,katgeori,harga_satuan,stok):
        return self.model.tambah_produk(id_produk,nama_produk,katgeori,harga_satuan,stok)
    
    def cari_produk(self, keyword):
        return self.model.cari_produk(keyword)  
    
    def tambah_stok(self,id_produk, jumlah):
        return self.model.tambah_stok(id_produk,jumlah)
    
    def get_all_produk(self):
        return self.model.df