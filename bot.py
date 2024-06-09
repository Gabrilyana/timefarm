import requests
import urllib.parse
import json
import time
import subprocess
import datetime
from colorama import Fore, Style  # Mengimpor warna dari colorama

# URL dan headers
url = "https://api.service.gameeapp.com/"
headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://tg-tap-miniapp.laborx.io',
    'priority': 'u=1, i',
    'referer': 'https://tg-tap-miniapp.laborx.io/',
    'content-type': 'text/plain;charset=UTF-8',
    'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24", "Microsoft Edge WebView2";v="125"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'Referer': 'https://tg-tap-miniapp.laborx.io/',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
}

# Fungsi untuk membaca initData dari file
def read_initdata_from_file(filename):
    initdata_list = []
    with open(filename, 'r') as file:
        for line in file:
            initdata_list.append(line.strip())
    return initdata_list

# Fungsi untuk mendapatkan nama dari initData
def get_nama_from_init_data(init_data):
    parsed_data = urllib.parse.parse_qs(init_data)
    if 'user' in parsed_data:
        user_data = parsed_data['user'][0]
        data = ""
        user_data_json = urllib.parse.unquote(user_data)
        user_data_dict = json.loads(user_data_json)
        if 'first_name' in user_data_dict:
            data = user_data_dict['first_name']
        if 'last_name' in user_data_dict:
            data = data + " " + user_data_dict['last_name']
        if 'username' in user_data_dict:
            data = data + " " + f"({user_data_dict['username']})"
        return data
    return None

# Fungsi untuk melakukan autentikasi
def auth(initdata):
    response = requests.post('https://tg-bot-tap.laborx.io/api/v1/auth/validate-init', data=initdata, headers=headers)
    if response.status_code == 200:
        return response.json().get("token")
    return None

# Fungsi untuk memulai sesi
def start_session(token):
    headers["authorization"] = f'Bearer {token}'
    response = requests.post('https://tg-bot-tap.laborx.io/api/v1/farming/start', {}, headers=headers)
    return response

# Fungsi untuk mengklaim sesi
def claim_session(token):
    headers["authorization"] = f'Bearer {token}'
    response = requests.post('https://tg-bot-tap.laborx.io/api/v1/farming/finish', {}, headers=headers)
    return response

# Fungsi untuk memproses initData
def process_initdata(init_data, balance):
    # Login
    nama = get_nama_from_init_data(init_data)
    token = auth(init_data)

    if token:
        start_response = start_session(token)
        daily_response = claim_session(token)
        
        # Pesan status
        status_message = ""
        if start_response.status_code == 200:
            status_message = "Mine Started"
        else:
            status_message = f"Error: {start_response.text}" if start_response.text else "Unknown Error"

        if daily_response.status_code == 200:
            status_message = "Sudah Claim"
        elif daily_response.status_code == 400:
            status_message = "Gagal untuk claim. Sudah diklaim sebelumnya."
        else:
            status_message = "Belum Waktunya Claim"

        # Tampilkan informasi
        print(f"Username: {nama}")
        print(f"Pesan Status: {status_message}")
        if balance is not None:
            print(f"Saldo: {balance}")

    else:
        print("Gagal untuk autentikasi")

# Program Utama
def main():
    initdata_file = "initdata.txt"
    
    # Header
    print(Fore.YELLOW + "\033[1mBOT AUTO CLAIM TIME FARM\033[0m")  # Teks bold menggunakan \033[1m dan \033[0m untuk mengembalikan ke format normal
    print(Fore.GREEN + "\033[1mBy : Gabril\033[0m")
    print(Fore.BLUE + "\033[1mGrup : @airdropsoltraman\033[0m")
    print(Style.RESET_ALL)  # Mengatur warna kembali ke default
    
    while True:
        initdata_list = read_initdata_from_file(initdata_file)
        balance = None  # Inisialisasi balance
        
        # Mendapatkan saldo sebelum memproses initData
        token = auth(initdata_list[0])  # Hanya memeriksa saldo pada salah satu initData saja
        if token:
            balance_response = requests.get('https://tg-bot-tap.laborx.io/api/v1/balance', headers={"authorization": f'Bearer {token}'})
            if balance_response.status_code == 200:
                balance_info = balance_response.json()
                balance = balance_info.get("balance")
        
        for init_data in initdata_list:
            process_initdata(init_data.strip(), balance)
            print("\n")

        # Deskripsi waktu sleep
        countdown = 60  # Waktu sleep diatur 60 detik
        print(Fore.MAGENTA + "\033[1mMulai waktu sleep selama 60 detik...\033[0m")  # Teks bold menggunakan \033[1m dan \033[0m untuk mengembalikan ke format normal
        print(Style.RESET_ALL)  # Mengatur warna kembali ke default
        
        while countdown > 0:
            print(Fore.CYAN + f"\033[1mSisa waktu sleep: {countdown} detik\033[0m", end="\r")  # Teks bold menggunakan \033[1m dan \033[0m untuk mengembalikan ke format>
            time.sleep(1)  # Mengurangi 1 detik setiap kali melintasi loop
            countdown -= 1
        
        # Deskripsi waktu sleep selesai
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(Fore.MAGENTA + f"\033[1mWaktu sleep selesai. Mulai membaca ulang file initData pada: {current_time}\033[0m")  # Teks bold menggunakan \033[1m dan \033[0m >
        print(Style.RESET_ALL)  # Mengatur warna kembali ke default

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        subprocess.run(["python3.10", "bot.py"])

