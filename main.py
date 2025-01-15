import logging
import subprocess
import socket
import requests
from shlex import quote
from aiogram import Bot, Dispatcher, executor, types

from config import API_TOKEN, PROXY_URL

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, proxy=PROXY_URL)
dp = Dispatcher(bot)

logger = logging.getLogger(__name__)

# Fungsi untuk ICMP Ping
def icmp_ping(ip):
    command = f"ping {quote(ip)} -c 5"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.read().decode()

# Fungsi untuk TCP Ping
def tcp_ping(ip, port):
    command = f"tcping {quote(ip)} -p {quote(port)} -c 4"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.read().decode()

# Fungsi untuk Traceroute
def run_traceroute(ip):
    command = f"traceroute -n {quote(ip)}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    
    output = process.stdout.read().decode()
    formatted_output = ""
    
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0].isdigit():  # Baris hop
            hop_number = parts[0]
            ip_address = parts[1]
            first_response = parts[2]
            if first_response == "*":
                formatted_output += f"{hop_number}. {ip_address} {first_response}\n"
            else:
                formatted_output += f"{hop_number}. {ip_address} {first_response} ms\n"
        else:
            formatted_output += line + "\n"  # Menyimpan header dan baris non-hop lainnya

    return formatted_output.strip()

# Fungsi untuk DNS Lookup
def dns_lookup(host, type):
    command = f"nslookup -type={quote(type)} {quote(host)}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.read().decode()

# Fungsi WHOIS dengan Format Code Block
def whois_lookup(ip):
    command = f"whois {quote(ip)}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    output = process.stdout.read().decode()
    
    # Filter hanya informasi yang diinginkan dan hindari duplikasi
    lines = output.splitlines()
    desired_keys = [
        "inetnum:", "netname:", "descr:", "country:", "admin-c:", "tech-c:", "abuse-c:", "status:", 
        "mnt-by:", "mnt-routes:", "mnt-irt:", "source:", "person:"
    ]
    
    unique_lines = set()
    filtered_output = ""
    for line in lines:
        if any(line.startswith(key) for key in desired_keys):
            if line not in unique_lines:
                filtered_output += line + "\n"
                unique_lines.add(line)
    
    return filtered_output.strip()

# Fungsi untuk melakukan reverse DNS lookup pada IP dan mengembalikan hasil traceroute
def reverse_dns_hops(ip):
    command = f"traceroute -n {quote(ip)}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    
    output = process.stdout.read().decode()
    formatted_output = ""

    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0].isdigit():  # Baris hop
            hop_number = parts[0]
            hop_ip_address = parts[1]

            # Lakukan reverse DNS lookup untuk IP
            try:
                hostname, _, _ = socket.gethostbyaddr(hop_ip_address)
                formatted_output += f"{hop_number}. {hop_ip_address} ({hostname})\n"
            except socket.herror:
                formatted_output += f"{hop_number}. {hop_ip_address} (hostname doesn't exists)\n"
            except socket.gaierror:
                formatted_output += f"{hop_number}. {hop_ip_address} (timeout)\n"
        else:
            formatted_output += line + "\n"  # Menyimpan header dan baris non-hop lainnya

    return formatted_output.strip()

# Fungsi untuk ping dari NTT Jakarta
async def ping_ntt(ip):
    url = "https://lg.wowrack.co.id/api/query/"
    payload = {
        "query_location": "jakarta-ntt",
        "query_target": ip,
        "query_type": "ping",
        "query_vrf": "global"
    }

    try:
        logger.debug(f"Sending request to {url} with payload: {payload}")
        response = requests.post(url, json=payload)

        # Log status dan hasil respons
        logger.debug(f"Received response status: {response.status_code}")
        response_json = response.json()
        logger.debug(f"Response JSON: {response_json}")

        # Memformat hasil ping
        formatted_result = format_ntt_ping_result(response_json)
        return formatted_result

    except Exception as e:
        logger.error(f"Error during ping request: {e}")
        return "Gagal mendapatkan hasil ping."

# Fungsi untuk memformat hasil ping dari NTT
def format_ntt_ping_result(data):
    if not data or 'output' not in data:
        return None

    try:
        output = data['output']  # Ambil hasil dari kunci 'output'
        lines = output.splitlines()

        # Mengambil hanya hasil yang relevan
        relevant_lines = []
        for line in lines:
            if "PING" in line or "bytes" in line or "icmp_seq" in line or "packets transmitted" in line:
                relevant_lines.append(line)

        formatted_output = "\n".join(relevant_lines)
        return formatted_output.strip()
    except Exception as e:
        logger.error(f"Error formatting ping result: {e}")
        return None

# Fungsi untuk ping dari Neucentrix Jakarta
async def ping_nc(ip):
    url = "https://lg.wowrack.co.id/api/query/"
    payload = {
        "query_location": "jakarta-neucentrix-karet",
        "query_target": ip,
        "query_type": "ping",
        "query_vrf": "global"
    }

    try:
        logger.debug(f"Sending request to {url} with payload: {payload}")
        response = requests.post(url, json=payload)

        # Log status dan hasil respons
        logger.debug(f"Received response status: {response.status_code}")
        response_json = response.json()
        logger.debug(f"Response JSON: {response_json}")

        # Memformat hasil ping
        formatted_result = format_nc_ping_result(response_json)
        return formatted_result

    except Exception as e:
        logger.error(f"Error during ping request: {e}")
        return "Gagal mendapatkan hasil ping dari Neucentrix Jakarta."

# Fungsi untuk memformat hasil ping dari Neucentrix
def format_nc_ping_result(data):
    if not data or 'output' not in data:
        logger.warning("Output not found in response data.")
        return "Tidak ada hasil ping yang tersedia."

    try:
        output = data['output']  # Ambil hasil dari kunci 'output'
        logger.debug(f"Raw output: {output}")

        # Menampilkan output secara penuh
        return output.strip()
    except Exception as e:
        logger.error(f"Error formatting ping result: {e}")
        return "Gagal memformat hasil ping."

# Handler untuk Command /start dan /help
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    content = '''
🌟 **Selamat Datang di Pingbot!** 🌟

Saya siap membantu Anda dengan berbagai fitur untuk memantau konektivitas jaringan.

**Fitur yang tersedia:**
- `/ping <ip>` - Lakukan ping ke alamat IP
- `/pingntt <ip>` - Lakukan ping dari NTT Jakarta
- `/pingnc <ip>` - Lakukan ping dari Neucentrix Jakarta
- `/trace <ip>` - Lakukan traceroute
- `/tracedns <ip>` - Lakukan traceroute dengan reverse DNS
- `/nslookup <host>` - Lakukan DNS lookup
- `/pingtcp <ip> <port>` - Lakukan ping TCP ke IP dan port
- `/whois <ip>` - Cek informasi WHOIS

🛠 *Silakan ketik perintah di atas untuk mulai!*
'''
    await message.reply(content.strip(), parse_mode="Markdown")

# Handler untuk Command /ping
@dp.message_handler(commands=['ping'])
async def ping(message: types.Message):
    ip = message.get_args()
    if not ip:
        await message.reply("Aku gak tau IP itu.")
        return
    waiting_message = await message.reply("Mohon ditunggu ya kak, lagi proses ping...")
    result = icmp_ping(ip)
    await waiting_message.edit_text(f"Hasil ping ke `{ip}`:\n\n```\n{result}\n```", parse_mode="Markdown")

# Handler untuk Command /pingntt
@dp.message_handler(commands=['pingntt'])
async def ping_ntt_command(message: types.Message):
    ip = message.get_args()
    if not ip:
        await message.reply("Aku gak tau IP itu.")
        return
    waiting_message = await message.reply("Mohon ditunggu ya kak, lagi proses ping dari NTT Jakarta...")
    result = await ping_ntt(ip)
    await waiting_message.edit_text(f"Hasil ping dari NTT Jakarta ke `{ip}`:\n\n```\n{result}\n```", parse_mode="Markdown")

# Handler untuk Command /pingnc
@dp.message_handler(commands=['pingnc'])
async def ping_nc_command(message: types.Message):
    ip = message.get_args()
    if not ip:
        await message.reply("Aku gak tau IP itu.")
        return
    waiting_message = await message.reply("Mohon ditunggu ya kak, lagi proses ping dari Neucentrix Jakarta...")
    result = await ping_nc(ip)
    await waiting_message.edit_text(f"Hasil ping dari Neucentrix Jakarta ke `{ip}`:\n\n```\n{result}\n```", parse_mode="Markdown")

# Handler untuk Command /trace
@dp.message_handler(commands=['trace'])
async def trace(message: types.Message):
    ip = message.get_args()
    if not ip:
        await message.reply("Aku gak tau IP itu.")
        return
    waiting_message = await message.reply("Mohon ditunggu ya kak, lagi proses traceroute...")
    result = run_traceroute(ip)
    await waiting_message.edit_text(f"Hasil traceroute ke `{ip}`:\n\n```\n{result}\n```", parse_mode="Markdown")

# Handler untuk Command /tracedns
@dp.message_handler(commands=['tracedns'])
async def tracedns(message: types.Message):
    ip = message.get_args()
    if not ip:
        await message.reply("Aku gak tau IP itu.")
        return
    waiting_message = await message.reply("Mohon ditunggu ya kak, lagi proses traceroute dan reverse DNS...")
    result = reverse_dns_hops(ip)
    await waiting_message.edit_text(f"Hasil traceroute dengan reverse DNS ke `{ip}`:\n\n```\n{result}\n```", parse_mode="Markdown")

# Handler untuk Command /nslookup
@dp.message_handler(commands=['nslookup'])
async def nslookup(message: types.Message):
    host = message.get_args()
    if not host:
        await message.reply("Aku gak tau host itu.")
        return
    waiting_message = await message.reply("Mohon ditunggu ya kak, lagi proses nslookup...")
    result = dns_lookup(host, "A")  # Menggunakan tipe A sebagai default
    await waiting_message.edit_text(f"Hasil nslookup untuk `{host}`:\n\n```\n{result}\n```", parse_mode="Markdown")

# Handler untuk Command /pingtcp
@dp.message_handler(commands=['pingtcp'])
async def pingtcp(message: types.Message):
    args = message.get_args().split()
    if len(args) != 2:
        await message.reply("Format yang benar: `/pingtcp <ip> <port>`")
        return
    
    ip, port = args
    waiting_message = await message.reply("Mohon ditunggu ya kak, lagi proses TCP ping...")
    result = tcp_ping(ip, port)
    await waiting_message.edit_text(f"Hasil TCP ping ke `{ip}` pada port `{port}`:\n\n```\n{result}\n```", parse_mode="Markdown")

# Handler untuk Command /whois
@dp.message_handler(commands=['whois'])
async def whois(message: types.Message):
    ip = message.get_args()
    if not ip:
        await message.reply("Aku gak tau IP itu.")
        return
    waiting_message = await message.reply("Mohon ditunggu ya kak, lagi proses WHOIS...")
    result = whois_lookup(ip)
    await waiting_message.edit_text(f"Hasil WHOIS untuk `{ip}`:\n\n```\n{result}\n```", parse_mode="Markdown")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)