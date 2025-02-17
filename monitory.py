import time
import psutil
import GPUtil
import csv

LOG_FILE = "resource_monitor.log"
CSV_FILE = "resource_monitor.csv"

def get_gpu_info():
    gpus = GPUtil.getGPUs()
    gpu_info = []
    for gpu in gpus:
        info = {
            "GPU ID": gpu.id,
            "GPU Name": gpu.name,
            "GPU Load (%)": gpu.load * 100,  # Porcentaje
            "GPU Memory Used (MB)": gpu.memoryUsed,  # MB
            "GPU Memory Total (MB)": gpu.memoryTotal,  # MB
            "GPU Temperature (°C)": gpu.temperature  # °C
        }
        gpu_info.append(info)
    return gpu_info

def get_cpu_info():
    return {
        "CPU Usage (%)": psutil.cpu_percent(interval=1),
        "RAM Used (GB)": psutil.virtual_memory().used / (1024 ** 3),  # GB
        "RAM Total (GB)": psutil.virtual_memory().total / (1024 ** 3)  # GB
    }

def log_resources():
    with open(LOG_FILE, "w") as f:
        f.write("========== Resource Monitoring Log ==========" + "\n\n")
    
    with open(CSV_FILE, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "CPU Usage (%)", "RAM Used (GB)", "RAM Total (GB)", "GPU ID", "GPU Name", "GPU Load (%)", "GPU Memory Used (MB)", "GPU Memory Total (MB)", "GPU Temperature (°C)"])
    
    while True:
        cpu_info = get_cpu_info()
        gpu_info = get_gpu_info()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"\nTimestamp: {timestamp}\n"
        log_entry += f"CPU Usage (%): {cpu_info['CPU Usage (%)']}\n"
        log_entry += f"RAM Used (GB): {cpu_info['RAM Used (GB)']} / {cpu_info['RAM Total (GB)']}\n"
        
        with open(CSV_FILE, "a", newline='') as f:
            writer = csv.writer(f)
            
            for gpu in gpu_info:
                log_entry += f"\nGPU ID: {gpu['GPU ID']}\n"
                log_entry += f"GPU Name: {gpu['GPU Name']}\n"
                log_entry += f"GPU Load (%): {gpu['GPU Load (%)']}\n"
                log_entry += f"GPU Memory Used (MB): {gpu['GPU Memory Used (MB)']} / {gpu['GPU Memory Total (MB)']}\n"
                log_entry += f"GPU Temperature (°C): {gpu['GPU Temperature (°C)']}\n"
                log_entry += "------------------------------------\n"
                
                writer.writerow([timestamp, cpu_info['CPU Usage (%)'], cpu_info['RAM Used (GB)'], cpu_info['RAM Total (GB)'], gpu['GPU ID'], gpu['GPU Name'], gpu['GPU Load (%)'], gpu['GPU Memory Used (MB)'], gpu['GPU Memory Total (MB)'], gpu['GPU Temperature (°C)']])
        
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
        
        time.sleep(5)  # Ajusta el intervalo según necesidad

if __name__ == "__main__":
    log_resources()
