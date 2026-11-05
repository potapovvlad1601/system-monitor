import time

from PySide6.QtCore import QThread, Signal

from app.services.system_info import (
    collect_static_info,
    collect_dynamic_info
)
from app.collectors.network import NetworkCollector


class SystemMonitorWorker(QThread):

    data_updated = Signal(object)
    error_occurred = Signal(str)

    def run(self):
        try:
            # Статическую информацию собираем один раз.
            static_info = collect_static_info()

            previous_network_data = None
            previous_network_time = None

            while not self.isInterruptionRequested():

                start_time = time.perf_counter()

                data = collect_dynamic_info(static_info)

                current_time = time.perf_counter()
                current_network_data = data["network"]["dynamic"]

                # Рассчитываем сетевую скорость.
                if previous_network_data is not None:
                    interval = current_time - previous_network_time

                    data["network"]["speed"] = (
                        NetworkCollector.calculate_network_speed(
                            previous_network_data,
                            current_network_data,
                            interval
                        )
                    )
                else:
                    data["network"]["speed"] = {}

                # Сохраняем данные для следующего измерения.
                previous_network_data = current_network_data
                previous_network_time = current_time

                # Передаём результат в GUI.
                self.data_updated.emit(data)

                # Интервал между циклами.
                self.msleep(100)

        except Exception as error:
            self.error_occurred.emit(str(error))