import carla
import psutil
import csv
import time
import pynvml
import socket
import random

SERVER_IP = "127.0.0.1"
NUM_VEHICLES = random.randint(10, 30)  # Количество машин
LOG_FILE = "client_metrics.csv"
pynvml.nvmlInit()
hostname = socket.gethostname()

def get_metrics():
    """ Получает метрики клиента """
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    net = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
    gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    gpu_usage = pynvml.nvmlDeviceGetUtilizationRates(gpu_handle).gpu
    gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(gpu_handle).used / (1024 * 1024)
    return cpu, ram, net, gpu_usage, gpu_mem

# Подключение к серверу
client = carla.Client(SERVER_IP, 2000)
client.set_timeout(10.0)

# Читаем команду от load_balancer.py
try:
    with open("client_command.txt", "r") as f:
        extra_vehicles = int(f.read().strip())
        NUM_VEHICLES += extra_vehicles
except:
    pass

NUM_VEHICLES = min(NUM_VEHICLES, 30)


# Спавн машин
world = client.get_world()
blueprint_library = world.get_blueprint_library()
spawn_points = world.get_map().get_spawn_points()

vehicles = []
for i in range(NUM_VEHICLES):
    vehicle_bp = random.choice(blueprint_library.filter('vehicle.*'))
    spawn_point = random.choice(spawn_points)
    vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
    if vehicle:
        vehicle.set_autopilot(True)
        vehicles.append(vehicle)

print(f"🚗 Запущено {len(vehicles)} машин")

# Запись заголовков
with open(LOG_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Time", "Hostname", "Vehicles", "CPU (%)", "RAM (%)", "Net (bytes)", "GPU (%)", "GPU Mem (MB)"])

# Сбор метрик
for _ in range(60):
    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        cpu, ram, net, gpu, gpu_mem = get_metrics()
        writer.writerow([time.time(), hostname, len(vehicles), cpu, ram, net, gpu, gpu_mem])
    time.sleep(1)

# Завершение
print("🛑 Завершаем работу, удаляем транспорт...")
for vehicle in vehicles:
    if vehicle.is_alive:
        vehicle.destroy()
        print(f"❌ Удалена машина {vehicle.id}")

# Дополнительная проверка: если какие-то машины остались
spawned_vehicles = world.get_actors().filter('vehicle.*')
for vehicle in spawned_vehicles:
    vehicle.destroy()
    print(f"🔄 Повторное удаление машины {vehicle.id}")

print("✅ Клиент завершил работу")