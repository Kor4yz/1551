import carla
import time
import os

SERVER_IP = "127.0.0.1"

def spawn_vehicles(client, num_vehicles):
    """Создает машины на клиенте"""
    world = client.get_world()
    blueprint_library = world.get_blueprint_library()
    vehicle_bp = blueprint_library.filter("vehicle.*")

    spawn_points = world.get_map().get_spawn_points()
    for i in range(min(num_vehicles, len(spawn_points))):
        vehicle = world.try_spawn_actor(vehicle_bp[i % len(vehicle_bp)], spawn_points[i])
        if vehicle:
            print(f"🚗 Клиент успешно создал машину {i+1}")

client = carla.Client(SERVER_IP, 2000)
client.set_timeout(10.0)

print("🎧 Клиент запущен и слушает команды...")

while True:
    if os.path.exists("client_command.txt"):
        with open("client_command.txt", "r") as f:
            num_vehicles = int(f.read().strip())

        print(f"📩 Получена команда на создание {num_vehicles} машин")
        spawn_vehicles(client, num_vehicles)
        os.remove("client_command.txt")
    time.sleep(5)
