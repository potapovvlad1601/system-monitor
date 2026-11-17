import time
from threading import Lock

from PySide6.QtCore import QThread, Signal

from app.services.system_info import (
    collect_static_info,
    collect_page_data
)
from app.collectors.network import NetworkCollector
from app.settings import MonitorSettings


class SystemMonitorWorker(QThread):

    data_updated = Signal(str, object)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_page = "dashboard"
        self._page_lock = Lock()
        self._settings = MonitorSettings()
        self._settings_lock = Lock()

    def set_active_page(self, page_name: str) -> None:
        """Safely select which data the worker will collect next."""
        with self._page_lock:
            self._active_page = page_name

    def get_active_page(self) -> str:
        with self._page_lock:
            return self._active_page

    def set_settings(self, settings: MonitorSettings) -> None:
        with self._settings_lock:
            self._settings = settings

    def get_settings(self) -> MonitorSettings:
        with self._settings_lock:
            return self._settings

    def wait_for_next_cycle(
        self,
        page_name: str,
        settings: MonitorSettings,
        elapsed_ms: float
    ) -> None:
        """Sleep in small chunks so page/settings changes take effect quickly."""
        remaining_ms = max(0, int(settings.update_interval_ms - elapsed_ms))
        while remaining_ms and not self.isInterruptionRequested():
            if (
                self.get_active_page() != page_name
                or self.get_settings() != settings
            ):
                return
            sleep_ms = min(100, remaining_ms)
            self.msleep(sleep_ms)
            remaining_ms -= sleep_ms

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
                settings = self.get_settings()
                data = collect_page_data(
                    page_name,
                    static_info,
                    settings.process_limit,
                    settings.process_sort_by
                )

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
                self.wait_for_next_cycle(page_name, settings, elapsed_ms)

        except Exception as error:
            self.error_occurred.emit(str(error))
