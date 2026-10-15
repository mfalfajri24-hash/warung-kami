import json
import os
from datetime import datetime

# =========================
# 1. DAFTAR MENU
# =========================
menu = {
    "1": {"nama": "Nasi Goreng", "harga": 15000},
    "2": {"nama": "Mie Goreng", "harga": 12000},
    "3": {"nama": "Ayam Penyet", "harga": 18000},
    "4": {"nama": "Es Teh", "harga": 4000},
    "5": {"nama": "Es Jeruk", "harga": 5000}
}

FILE_RIWAYAT = "riwayat_pesanan.json"
keranjang = {}


def rupiah(nominal):
    """Format angka menjadi tampilan rupiah sederhana."""
    return f"Rp {nominal:,}".replace(",", ".")


# =========================
# 2. TAMPILKAN MENU
# =========================
def tampilkan_menu():
    print("\n========== MENU RESTORAN ==========")
    for kode, item in menu.items():
        print(f"{kode}. {item['nama']:<15} {rupiah(item['harga'])}")
    print("===================================")


# =========================
# 3. KERANJANG PESANAN
# =========================
def tambah_pesanan():
    tampilkan_menu()
    kode = input("Pilih nomor menu: ").strip()

    if kode not in menu:
        print("Menu tidak tersedia.")
        return

    jumlah_input = input("Jumlah porsi: ").strip()
    if not jumlah_input.isdigit() or int(jumlah_input) <= 0:
        print("Jumlah harus berupa angka lebih dari 0.")
        return

    jumlah = int(jumlah_input)
    if kode in keranjang:
        keranjang[kode]["jumlah"] += jumlah
    else:
        keranjang[kode] = {
            "nama": menu[kode]["nama"],
            "harga": menu[kode]["harga"],
            "jumlah": jumlah
        }

    print(f"{jumlah} {menu[kode]['nama']} berhasil ditambahkan.")


def tampilkan_keranjang():
    print("\n========== KERANJANG ==========")
    if not keranjang:
        print("Keranjang masih kosong.")
        return

    for kode, item in keranjang.items():
        subtotal = item["harga"] * item["jumlah"]
        print(
            f"{kode}. {item['nama']} | {item['jumlah']} porsi | "
            f"{rupiah(subtotal)}"
        )
    print(f"Subtotal: {rupiah(hitung_subtotal())}")


def hitung_subtotal():
    return sum(item["harga"] * item["jumlah"]
               for item in keranjang.values())


def ubah_jumlah():
    tampilkan_keranjang()
    if not keranjang:
        return

    kode = input("Nomor menu yang ingin diubah: ").strip()
    if kode not in keranjang:
        print("Menu tidak ada di keranjang.")
        return

    jumlah_input = input(
        "Jumlah baru (masukkan 0 untuk menghapus): "
    ).strip()

    if not jumlah_input.isdigit():
        print("Masukkan angka yang valid.")
        return

    jumlah = int(jumlah_input)
    if jumlah == 0:
        del keranjang[kode]
        print("Menu dihapus dari keranjang.")
    else:
        keranjang[kode]["jumlah"] = jumlah
        print("Jumlah pesanan berhasil diperbarui.")


def hapus_pesanan():
    tampilkan_keranjang()
    if not keranjang:
        return

    kode = input("Nomor menu yang ingin dihapus: ").strip()
    if kode in keranjang:
        del keranjang[kode]
        print("Menu berhasil dihapus.")
    else:
        print("Menu tidak ada di keranjang.")


# =========================
# 4. RIWAYAT PESANAN
# =========================
def simpan_riwayat(pesanan):
    if os.path.exists(FILE_RIWAYAT):
        try:
            with open(FILE_RIWAYAT, "r", encoding="utf-8") as file:
                riwayat = json.load(file)
        except (json.JSONDecodeError, OSError):
            riwayat = []
    else:
        riwayat = []

    riwayat.append(pesanan)
    with open(FILE_RIWAYAT, "w", encoding="utf-8") as file:
        json.dump(riwayat, file, ensure_ascii=False, indent=2)


def tampilkan_riwayat():
    if not os.path.exists(FILE_RIWAYAT):
        print("Belum ada riwayat pesanan.")
        return

    try:
        with open(FILE_RIWAYAT, "r", encoding="utf-8") as file:
            riwayat = json.load(file)
    except (json.JSONDecodeError, OSError):
        print("File riwayat tidak bisa dibaca.")
        return

    print("\n========== RIWAYAT PESANAN ==========")
    if not riwayat:
        print("Belum ada riwayat pesanan.")
        return

    for pesanan in riwayat:
        print(
            f"Pesanan {pesanan['id']} | {pesanan['waktu']} | "
            f"{pesanan['pelanggan']} | Meja {pesanan['meja']} | "
            f"Total {rupiah(pesanan['total'])}"
        )


# =========================
# 5. CHECKOUT, DISKON, BIAYA TAMBAHAN
# =========================
def checkout():
    if not keranjang:
        print("Keranjang kosong. Tambahkan pesanan dahulu.")
        return

    nama = input("Nama pelanggan: ").strip()
    if not nama:
        print("Nama pelanggan tidak boleh kosong.")
        return

    meja = input("Nomor meja: ").strip()
    if not meja:
        print("Nomor meja tidak boleh kosong.")
        return

    subtotal = hitung_subtotal()

    # Diskon contoh: 10% jika subtotal minimal Rp50.000
    diskon = int(subtotal * 0.10) if subtotal >= 50000 else 0

    # Biaya layanan contoh: 5% dari subtotal setelah diskon.
    # Ubah menjadi 0 jika restoran tidak mengenakan biaya layanan.
    biaya_layanan = int((subtotal - diskon) * 0.05)

    total = subtotal - diskon + biaya_layanan

    print("\n============= RINGKASAN =============")
    print(f"Pelanggan       : {nama}")
    print(f"Nomor meja      : {meja}")
    for item in keranjang.values():
        print(
            f"{item['nama']} x{item['jumlah']} = "
            f"{rupiah(item['harga'] * item['jumlah'])}"
        )
    print("-------------------------------------")
    print(f"Subtotal        : {rupiah(subtotal)}")
    print(f"Diskon          : -{rupiah(diskon)}")
    print(f"Biaya layanan   : {rupiah(biaya_layanan)}")
    print(f"TOTAL           : {rupiah(total)}")
    print("=====================================")

    bayar_input = input("Uang pembayaran (angka saja): ").strip()
    if not bayar_input.isdigit():
        print("Pembayaran harus berupa angka.")
        return

    bayar = int(bayar_input)
    if bayar < total:
        print(f"Uang kurang {rupiah(total - bayar)}. Pesanan belum disimpan.")
        return

    pesanan = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pelanggan": nama,
        "meja": meja,
        "items": list(keranjang.values()),
        "subtotal": subtotal,
        "diskon": diskon,
        "biaya_layanan": biaya_layanan,
        "total": total,
        "uang_bayar": bayar,
        "kembalian": bayar - total
    }

    simpan_riwayat(pesanan)
    print(f"Kembalian: {rupiah(bayar - total)}")
    print("Pesanan berhasil disimpan ke riwayat.")

    keranjang.clear()


# =========================
# 6. MENU UTAMA
# =========================
def main():
    while True:
        print("\n====== SISTEM ORDER RESTORAN ======")
        print("1. Tampilkan menu")
        print("2. Tambah pesanan")
        print("3. Lihat keranjang")
        print("4. Ubah jumlah pesanan")
        print("5. Hapus menu dari keranjang")
        print("6. Checkout dan bayar")
        print("7. Lihat riwayat pesanan")
        print("0. Keluar")

        pilihan = input("Pilih fitur: ").strip()

        if pilihan == "1":
            tampilkan_menu()
        elif pilihan == "2":
            tambah_pesanan()
        elif pilihan == "3":
            tampilkan_keranjang()
        elif pilihan == "4":
            ubah_jumlah()
        elif pilihan == "5":
            hapus_pesanan()
        elif pilihan == "6":
            checkout()
        elif pilihan == "7":
            tampilkan_riwayat()
        elif pilihan == "0":
            print("Terima kasih sudah memesan!")
            break
        else:
            print("Pilihan tidak valid. Coba lagi.")


if __name__ == "__main__":
    main()
