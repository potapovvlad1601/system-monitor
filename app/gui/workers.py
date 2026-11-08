import time
from threading import Lock

from PySide6.QtCore import QThread, Signal

from app.services.system_info import (
    collect_static_info,
    collect_page_data
)
from app.collectors.network import NetworkCollector


class SystemMonitorWorker(QThread):

    data_updated = Signal(str, object)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_page = "dashboard"
        self._page_lock = Lock()

    def set_active_page(self, page_name: str) -> None:
        """Safely select which data the worker will collect next."""
        with self._page_lock:
            self._active_page = page_name

    def get_active_page(self) -> str:
        with self._page_lock:
            return self._active_page

    def run(self):
        try:
            # Статическую информацию собираем один раз.
            static_info = collect_static_info()

            previous_network_data = None
            previous_network_time = None
            previous_network_page = None

            while not self.isInterruptionRequested():
                start_time = time.perf_counter()
                page_name = self.get_active_page()
                data = collect_page_data(page_name, static_info)

                if data is not None:
                    current_time = time.perf_counter()
                    network_data = data.get("network")

                    if network_data is not None:
                        current_network_data = network_data["dynamic"]
                        if (
                            previous_network_data is not None
                            and previous_network_page == page_name
                        ):
                            network_data["speed"] = (
                                NetworkCollector.calculate_network_speed(
                                    previous_network_data,
                                    current_network_data,
                                    current_time - previous_network_time
                                )
                            )
                        else:
                            network_data["speed"] = {}

                        previous_network_data = current_network_data
                        previous_network_time = current_time
                        previous_network_page = page_name

                    # The GUI receives data only for the page that requested it.
                    self.data_updated.emit(page_name, data)

                elapsed_ms = (time.perf_counter() - start_time) * 1000
                self.msleep(max(0, int(1000 - elapsed_ms)))

        except Exception as error:
            self.error_occurred.emit(str(error))
