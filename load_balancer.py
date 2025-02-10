import pandas as pd
import carla
import time
import random
import os

SERVER_IP = "127.0.0.1"
THRESHOLD_CPU = 80  # Если CPU > 80%, переносим машины
THRESHOLD_RAM = 90  # Если RAM > 90%, тоже переносим
THRESHOLD_GPU = 95  # Если GPU > 95%, тоже переносим
CHECK_INTERVAL = 10
CLIENT_LOG = "client_metrics.csv"
SERVER_LOG = "server_metrics.csv"

def redistribute_vehicles(client, num_vehicles):
    """Перенос машин на клиентские ноутбуки"""
    world = client.get_world()
    vehicles = world.get_actors().filter('vehicle.*')
    vehicles = list(vehicles)

    vehicles = world.get_actors().filter('vehicle.*')
    print(f"📋 Найдено {len(vehicles)} машин на сервере")


    if len(vehicles) > num_vehicles:
        print(f"🔴 Переносим {num_vehicles} машин на клиентов...")
        for i in range(num_vehicles):
            if i < len(vehicles):
                vehicles[i].destroy()
                print(f"🚗 Машина {i+1} удалена")

        # Отправляем команду клиентам на спавн новых машин
        with open("client_command.txt", "w") as f:
            f.write(str(num_vehicles))

        print(f"✅ {num_vehicles} машин перенесены!")
    else:
        print("⚠️ Недостаточно машин для переноса")


# Подключаемся к серверу
client = carla.Client(SERVER_IP, 2000)
client.set_timeout(10.0)

print("🚀 Балансировщик запущен. Следим за сервером...")

while True:
    time.sleep(10)
    world = client.get_world()
    vehicles = world.get_actors().filter('vehicle.*')
    vehicles = list(vehicles)
    if  len(vehicles) == 0:
        print("⚠️ Нет активных клиентов, балансировщик завершает работу.")
        break

    if not os.path.exists("server_metrics.csv"):
        print("⏳ Ожидание данных от сервера...")
        time.sleep(CHECK_INTERVAL)
        continue

    df_server = pd.read_csv("server_metrics.csv")
    last_data = df_server.tail(5)
    avg_cpu = last_data["CPU (%)"].mean()
    avg_ram = last_data["RAM (%)"].mean()
    avg_gpu = last_data["GPU (%)"].mean()

    print(f"📊 CPU: {avg_cpu:.2f}% | RAM: {avg_ram:.2f}% | GPU: {avg_gpu:.2f}%")

    if avg_cpu > THRESHOLD_CPU or avg_ram > THRESHOLD_RAM or avg_gpu > THRESHOLD_GPU:
        num_to_move = random.randint(5, 10)
        redistribute_vehicles(client, num_to_move)
    else:
        print("✅ Сервер работает нормально, балансировка не требуется.")

    time.sleep(CHECK_INTERVAL)