import subprocess
import time

NUM_CLIENTS = 5
processes = []

for i in range(NUM_CLIENTS):
    p = subprocess.Popen("python client_monitor.py", shell=True)
    processes.append(p)
    time.sleep(2)

# Ждем завершения всех клиентов
for p in processes:
    p.wait()

print("✅ Все клиенты завершили работу")
