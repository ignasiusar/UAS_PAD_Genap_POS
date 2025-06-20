import tkinter as tk
from tkinter import ttk

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("POS - Toko Kelontong")
        self.geometry("1000x600")
        self.configure(bg="#e8f0f2")
        self.frames = {}

        # Frame Sidebar
        sidebar = tk.Frame(self, width=200, bg="#2c3e50")
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="POS Kelontong", fg="white", bg="#2c3e50",
                 font=("Segoe UI", 14, "bold")).pack(pady=20)

        btn_home = tk.Button(sidebar, text="Home", command=lambda: self.show_frame(HomePage),
                             bg="#27ae60", fg="white", width=15)
        btn_home.pack(pady=10)

        btn_produk = tk.Button(sidebar, text="Product List", command=lambda: self.show_frame(ProductPage),
                               bg="#27ae60", fg="white", width=15)
        btn_produk.pack(pady=10)

        btn_pos = tk.Button(sidebar, text="POS", command=lambda: self.show_frame(POSPage),
                            bg="#27ae60", fg="white", width=15)
        btn_pos.pack(pady=10)

        # Frame Utama
        container = tk.Frame(self, bg="#e8f0f2")
        container.pack(side="right", fill="both", expand=True)

        for F in (HomePage, ProductPage, POSPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e8f0f2")
        label = tk.Label(self, text="Selamat Datang di Aplikasi POS Toko Kelontong",
                         font=("Segoe UI", 16, "bold"), bg="#e8f0f2")
        label.pack(pady=50)
        desc = tk.Label(self, text="Gunakan menu di sebelah kiri untuk navigasi.",
                        font=("Segoe UI", 11), bg="#e8f0f2")
        desc.pack()


class ProductPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e8f0f2")
        label = tk.Label(self, text="📦 Daftar Produk", font=("Segoe UI", 14, "bold"), bg="#e8f0f2")
        label.pack(pady=20)


class POSPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e8f0f2")
        label = tk.Label(self, text="🛒 Point of Sales (POS)", font=("Segoe UI", 14, "bold"), bg="#e8f0f2")
        label.pack(pady=20)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
