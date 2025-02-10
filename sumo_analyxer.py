import traci
import time
import traci.constants as tc
import pytz
import datetime
from random import randrange
import pandas as pd


# Функция для получения текущей даты и времени в часовом поясе Сингапура
def getdatetime():
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    currentDT = utc_now.astimezone(pytz.timezone("Asia/Singapore"))
    return currentDT.strftime("%Y-%m-%d %H:%M:%S")


# Функция для преобразования двумерного списка в одномерный
def flatten_list(_2d_list):
    flat_list = []
    for element in _2d_list:
        if isinstance(element, list):
            flat_list.extend(element)
        else:
            flat_list.append(element)
    return flat_list


# Запуск SUMO с указанной конфигурацией
sumoCmd = ["sumo", "-c", "osm.sumocfg"]
traci.start(sumoCmd)

# Списки для хранения данных о транспортных средствах, светофорах и всей симуляции
packVehicleData = []
packTLSData = []
packBigData = []

# Основной цикл симуляции, пока остаются ожидаемые транспортные средства
while traci.simulation.getMinExpectedNumber() > 0:

    traci.simulationStep()

    # Получаем список транспортных средств и светофоров
    vehicles = traci.vehicle.getIDList()
    trafficlights = traci.trafficlight.getIDList()

    for vehid in vehicles:
        # Получение данных о транспортном средстве
        x, y = traci.vehicle.getPosition(vehid)
        coord = [x, y]
        lon, lat = traci.simulation.convertGeo(x, y)
        gpscoord = [lon, lat]
        spd = round(traci.vehicle.getSpeed(vehid) * 3.6, 2)  # Скорость в км/ч
        edge = traci.vehicle.getRoadID(vehid)
        lane = traci.vehicle.getLaneID(vehid)
        displacement = round(traci.vehicle.getDistance(vehid), 2)
        turnAngle = round(traci.vehicle.getAngle(vehid), 2)
        nextTLS = traci.vehicle.getNextTLS(vehid)

        # Запись данных транспортного средства
        vehList = [getdatetime(), vehid, coord, gpscoord, spd, edge, lane, displacement, turnAngle, nextTLS]

        print(f"Vehicle: {vehid} at datetime: {getdatetime()}")
        print(f"{vehid} >>> Position: {coord} | GPS Position: {gpscoord} | Speed: {spd} km/h | "
              f"EdgeID: {edge} | LaneID: {lane} | Distance: {displacement}m | "
              f"Vehicle orientation: {turnAngle}° | Upcoming traffic lights: {nextTLS}")

        # Проверяем, управляется ли светофором полоса, на которой находится транспортное средство
        tlsList = []
        for tflight in trafficlights:
            if lane in traci.trafficlight.getControlledLanes(tflight):
                # Получаем данные о светофоре
                tl_state = traci.trafficlight.getRedYellowGreenState(tflight)
                tl_phase_duration = traci.trafficlight.getPhaseDuration(tflight)
                tl_lanes_controlled = traci.trafficlight.getControlledLanes(tflight)
                tl_program = traci.trafficlight.getCompleteRedYellowGreenDefinition(tflight)
                tl_next_switch = traci.trafficlight.getNextSwitch(tflight)

                tlsList = [tflight, tl_state, tl_phase_duration, tl_lanes_controlled, tl_program, tl_next_switch]

                print(f"{tflight} ---> TL state: {tl_state} | TLS phase duration: {tl_phase_duration} | "
                      f"Lanes controlled: {tl_lanes_controlled} | TLS Program: {tl_program} | "
                      f"Next TLS switch: {tl_next_switch}")

        # Сохранение данных о транспортных средствах и светофорах
        packBigDataLine = flatten_list([vehList, tlsList])
        packBigData.append(packBigDataLine)

        # Управление движением конкретного транспортного средства (veh2)
        NEWSPEED = 15  # 15 м/с = 54 км/ч
        if vehid == 'veh2':
            traci.vehicle.setSpeedMode('veh2', 0)
            traci.vehicle.setSpeed('veh2', NEWSPEED)

        # Управление светофором
        trafficlightduration = [5, 37, 5, 35, 6, 3]
        trafficsignal = ["rrrrrrGGGGgGGGrr", "yyyyyyyyrrrrrrrr", "rrrrrGGGGGGrrrrr", "rrrrryyyyyyrrrrr",
                         "GrrrrrrrrrrGGGGg", "yrrrrrrrrrryyyyy"]
        tfl = ("cluster_4260917315_5146794610_5146796923_5146796930_5704674780_5704674783_5704674784_"
               "5704674787_6589790747_8370171128_8370171143_8427766841_8427766842_8427766845")
        traci.trafficlight.setPhaseDuration(tfl, trafficlightduration[randrange(6)])
        traci.trafficlight.setRedYellowGreenState(tfl, trafficsignal[randrange(6)])

# Завершение симуляции
traci.close()

# Создание Excel-файла с результатами симуляции
columnnames = ['dateandtime', 'vehid', 'coord', 'gpscoord', 'spd', 'edge', 'lane', 'displacement', 'turnAngle',
               'nextTLS', 'tflight', 'tl_state', 'tl_phase_duration', 'tl_lanes_controlled', 'tl_program', 'tl_next_switch']
dataset = pd.DataFrame(packBigData, columns=columnnames)
dataset.to_excel("output.xlsx", index=False)

# Задержка перед завершением работы программы
time.sleep(5)
