def tampilkan_regresi_penjualan():
    df = load_penjualan()

    # Pastikan kolom tanggal bertipe datetime
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    df = df.sort_values("tanggal")

    # Ambil data penjualan terakhir per hari per produk
    df_harian = df.groupby("tanggal")["stok_terjual"].sum().reset_index()

    # Ubah tanggal ke ordinal (angka hari) untuk regresi
    df_harian["tanggal_angka"] = df_harian["tanggal"].map(datetime.toordinal)

    # X = tanggal, y = jumlah terjual
    X = df_harian["tanggal_angka"].values.reshape(-1, 1)
    y = df_harian["stok_terjual"].values

    model = LinearRegression()
    model.fit(X, y)

    prediksi = model.predict(X)

    # Visualisasi
    plt.figure(figsize=(10, 5))
    plt.bar(df_harian["tanggal"], df_harian["stok_terjual"], color="skyblue", label="Stok Terjual")
    plt.plot(df_harian["tanggal"], prediksi, color="red", linewidth=2, label="Regresi Linear")
    plt.title("Regresi Linear - Total Stok Terjual Harian")
    plt.xlabel("Tanggal")
    plt.ylabel("Stok Terjual")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()
