import pandas as pd
import matplotlib.pyplot as plt

# Загружаем данные
df_server = pd.read_csv("server_metrics.csv")
df_clients = pd.read_csv("client_metrics.csv")

# Создаем 4 графика для CPU, RAM, сети и GPU
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# CPU
axes[0, 0].plot(df_server["Time"], df_server["CPU (%)"], label="CPU (Server)", color="red")
axes[0, 0].plot(df_clients["Time"], df_clients["CPU (%)"], label="CPU (Clients)", color="blue")
axes[0, 0].set_title("Загрузка CPU (%)")
axes[0, 0].set_xlabel("Время")  # Подпись оси X
axes[0, 0].set_ylabel("CPU (%)")  # Подпись оси Y
axes[0, 0].legend()
axes[0, 0].grid()

# RAM
axes[0, 1].plot(df_server["Time"], df_server["RAM (%)"], label="RAM (Server)", color="red")
axes[0, 1].plot(df_clients["Time"], df_clients["RAM (%)"], label="RAM (Clients)", color="blue")
axes[0, 1].set_title("Загрузка RAM (%)")
axes[0, 1].set_xlabel("Время")  # Подпись оси X
axes[0, 1].set_ylabel("RAM (%)")  # Подпись оси Y
axes[0, 1].legend()
axes[0, 1].grid()

# Сеть
axes[1, 0].plot(df_server["Time"], df_server["Net (bytes)"], label="Net (Server)", color="red")
axes[1, 0].plot(df_clients["Time"], df_clients["Net (bytes)"], label="Net (Clients)", color="blue")
axes[1, 0].set_title("Сетевой трафик (байты)")
axes[1, 0].set_xlabel("Время")  # Подпись оси X
axes[1, 0].set_ylabel("Сетевой трафик (байты)")  # Подпись оси Y
axes[1, 0].legend()
axes[1, 0].grid()

# GPU
axes[1, 1].plot(df_server["Time"], df_server["GPU (%)"], label="GPU (Server)", color="red")
axes[1, 1].plot(df_clients["Time"], df_clients["GPU (%)"], label="GPU (Clients)", color="blue")
axes[1, 1].set_title("Загрузка GPU (%)")
axes[1, 1].set_xlabel("Время")  # Подпись оси X
axes[1, 1].set_ylabel("GPU (%)")  # Подпись оси Y
axes[1, 1].legend()
axes[1, 1].grid()

plt.tight_layout()
plt.show()


fig2, axes2 = plt.subplots(3, 1, figsize=(8, 8))

# CPU от количества машин
axes2[0].scatter(df_clients["Vehicles"], df_clients["CPU (%)"], label="CPU (Clients)", color="blue", marker='x')
axes2[0].set_title("Загрузка CPU (%) - от количества машин (Clients)")
axes2[0].set_xlabel("Количество машин")
axes2[0].set_ylabel("CPU (%)")
axes2[0].legend()
axes2[0].grid()

# RAM от количества машин
axes2[1].scatter(df_clients["Vehicles"], df_clients["RAM (%)"], label="RAM (Clients)", color="blue", marker='x')
axes2[1].set_title("Загрузка RAM (%) - от количества машин (Clients)")
axes2[1].set_xlabel("Количество машин")
axes2[1].set_ylabel("RAM (%)")
axes2[1].legend()
axes2[1].grid()

# RAM от количества машин
axes2[2].scatter(df_clients["Vehicles"], df_clients["GPU (%)"], label="GPU (Clients)", color="blue", marker='x')
axes2[2].set_title("Загрузка GPU (%) - от количества машин (Clients)")
axes2[2].set_xlabel("Количество машин")
axes2[2].set_ylabel("GPU (%)")
axes2[2].legend()
axes2[2].grid()

plt.tight_layout()
plt.show()