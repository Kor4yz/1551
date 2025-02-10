import psutil
import csv
import time
import pynvml
import socket
import subprocess
import os
import carla

LOG_FILE = "server_metrics.csv"
CLIENT_LOG = "client_metrics.csv"
ERROR_LOG = "server_errors.log"

pynvml.nvmlInit()
hostname = socket.gethostname()


def get_metrics():
    """ Получает метрики сервера """
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        net = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

        try:
            gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            gpu_usage = pynvml.nvmlDeviceGetUtilizationRates(gpu_handle).gpu
            gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(gpu_handle).used / (1024 * 1024)
        except pynvml.NVMLError as e:
            with open(ERROR_LOG, "a") as err_file:
                err_file.write(f"{time.ctime()} - GPU Error: {str(e)}\n")
            gpu_usage, gpu_mem = 0, 0

        return cpu, ram, net, gpu_usage, gpu_mem
    except Exception as e:
        with open(ERROR_LOG, "a") as err_file:
            err_file.write(f"{time.ctime()} - General Error: {str(e)}\n")
        return 0, 0, 0, 0, 0


def is_carla_running():
    """ Проверяет, запущен ли сервер CARLA """
    for process in psutil.process_iter(attrs=['name']):
        if 'CarlaUE4' in process.info['name']:
            return True
    return False


# Запись заголовков
with open(LOG_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Time", "Hostname", "CPU (%)", "RAM (%)", "Net (bytes)", "GPU (%)", "GPU Mem (MB)"])

CARLA_PATH = r"C:\WindowsNoEditor\CarlaUE4.exe"  # Полный путь к серверу
WORKING_DIR = r"C:\WindowsNoEditor"  # Указываем рабочую папку

server_process = None

if not is_carla_running():
    print("🚀 Запуск сервера CARLA...")
    server_process = subprocess.Popen([CARLA_PATH, "-opengl"], cwd=WORKING_DIR)
    time.sleep(10)

    if not is_carla_running():
        print("❌ Ошибка: CARLA не запустился!")
        with open(ERROR_LOG, "a") as err_file:
            err_file.write(f"{time.ctime()} - CARLA failed to start!\n")
        exit(1)

def check_clients_active():
    return os.path.exists(CLIENT_LOG) and os.path.getsize(CLIENT_LOG) > 0

print("📊 Начинаем сбор метрик сервера...")

while check_clients_active():
    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        cpu, ram, net, gpu, gpu_mem = get_metrics()
        writer.writerow([time.time(), hostname, cpu, ram, net, gpu, gpu_mem])
    time.sleep(1)

    SERVER_IP = "127.0.0.1"
    client = carla.Client(SERVER_IP, 2000)
    world = client.get_world()
    vehicles = world.get_actors().filter('vehicle.*')
    vehicles = list(vehicles)
    if  len(vehicles) == 0:
        print("⚠️ Сбор метрик завершен.")
        break

if server_process is not None:
    server_process.terminate()
    print("🛑 Сервер CARLA остановлен.")

