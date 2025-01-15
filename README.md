# PingBot - Telegram Bot

PingBot adalah bot Telegram sederhana untuk memantau konektivitas jaringan. Anda dapat menggunakan bot ini untuk melakukan ping ke server dan mendapatkan laporan status secara langsung di Telegram.

## Cara Install

Ikuti langkah-langkah berikut untuk menginstal dan menjalankan PingBot di sistem Anda.

### 1. Persiapan Awal

Pastikan Anda sudah memiliki sistem operasi yang mendukung Python 3 (OS bebas, seperti Linux, macOS, atau Windows).

1. Update dan upgrade sistem Anda:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. Install dependensi utama:
   ```bash
   sudo apt install -y python3 python3-pip git
   ```

### 2. Clone Repository

Clone repository PingBot dari repository berikut:
```bash
git clone http://10.173.84.61:3000/ryan/pingbot.git
```

Masuk ke direktori proyek:
```bash
cd pingbot
```

### 3. Install Dependensi Python

Sebelum menjalankan bot, install semua dependensi yang dibutuhkan:
```bash
pip3 install -r requirements.txt
```

### 4. Konfigurasi Bot

Edit file `config.py` untuk memasukkan token bot Telegram Anda:
```python
API_TOKEN = 'Token_BOT'  # Ganti 'Token_BOT' dengan token bot Anda
PROXY_URL = ''           # Jika menggunakan proxy, masukkan URL proxy di sini
SHOW_PUBLIC_IP = True    # Set True jika ingin menampilkan IP publik
```

### 5. Menjalankan Bot

Setelah semua langkah selesai, Anda dapat menjalankan bot dengan perintah:
```bash
python3 bot.py
```

Jika bot berhasil dijalankan, Anda akan melihat pesan log di terminal.


## 6. Jalankan Dibackground - opsional

Jika ingin menjalankan proses bot tersebut dibackground bisa gunakan nohup dan (&)
```bash
nohup python3 main.py > bot_output.log 2>&1 &
```
Dan
```bash
python3 main.py &
```

## Catatan

- Pastikan Anda sudah memiliki akun bot Telegram. Anda dapat membuatnya dengan menggunakan [BotFather](https://core.telegram.org/bots#botfather).
- Jika Anda ingin menambahkan fitur atau memperbaiki bug, silakan kontribusi langsung ke repository ini.

---

Selamat menggunakan PingBot! 🎉