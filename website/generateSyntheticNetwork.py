import random
import pandas as pd

def generate_normal_traffic(num_samples):
    data = []
    for _ in range(num_samples):
        packet_size = random.randint(64, 1500)  # bytes
        request_rate = random.uniform(0.1, 10)  # requests per second
        source_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        destination_ip = "192.168.1.1"
        protocol_type = random.choice(["TCP", "UDP", "ICMP"])
        data.append([packet_size, request_rate, source_ip, destination_ip, protocol_type, 'normal'])  # 'normal' indicates normal traffic
    return data

def generate_ddos_traffic(num_samples, num_attackers):
    data = []
    destination_ip = "192.168.1.1"
    for _ in range(num_samples):
        packet_size = random.randint(64, 1500)
        request_rate = random.uniform(100, 1000)  # Simulate high request rate for DDoS
        source_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, num_attackers)}"
        protocol_type = "TCP"
        data.append([packet_size, request_rate, source_ip, destination_ip, protocol_type, 'ddos'])  # 'ddos' indicates DDoS traffic
    return data

def generate_port_scan_traffic(num_samples):
    data = []
    destination_ip = "192.168.1.1"
    for _ in range(num_samples):
        packet_size = random.randint(40, 100)  # Smaller packet sizes for port scanning
        request_rate = random.uniform(0.1, 1)  # Lower request rate for port scanning
        source_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        protocol_type = random.choice(["TCP", "UDP"])
        data.append([packet_size, request_rate, source_ip, destination_ip, protocol_type, 'port_scan'])  # 'port_scan' indicates port scanning traffic
    return data

normal_traffic = generate_normal_traffic(1000)
ddos_traffic = generate_ddos_traffic(200, 50)
port_scan_traffic = generate_port_scan_traffic(200)

combined_data = normal_traffic + ddos_traffic + port_scan_traffic
random.shuffle(combined_data)

columns = ['packet_size', 'request_rate', 'source_ip', 'destination_ip', 'protocol_type', 'label']
df = pd.DataFrame(combined_data, columns=columns)
df.to_csv('network_traffic_data.csv', index=False)
