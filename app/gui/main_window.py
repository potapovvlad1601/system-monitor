
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QStackedWidget,
    QFileDialog
)
from PySide6.QtCore import QSettings

from app.gui.pages.dashboard import DashboardPage
from app.gui.pages.cpu_page import CPUPage
from app.gui.pages.memory_page import MemoryPage
from app.gui.pages.disk_page import DiskPage
from app.gui.pages.network_page import NetworkPage
from app.gui.pages.processes_page import ProcessesPage
from app.gui.pages.settings_page import SettingsPage

from PySide6.QtWidgets import QMessageBox
from app.gui.workers import SystemMonitorWorker
from app.settings import MonitorSettings

from app.gui.styles import get_style
from app.services.diagnostics_export import export_diagnostics


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.settings = self.load_settings()
        self._last_dashboard_data = None

        self.setWindowTitle("System Monitor")
        self.resize(1200, 750)
        self.setMinimumSize(900, 600)

        self.apply_theme(self.settings.theme)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.create_sidebar(main_layout)
        self.create_content(main_layout)
        self.apply_theme(self.settings.theme)

        self.worker = SystemMonitorWorker(self)

        self.worker.data_updated.connect(self.update_dashboard)
        self.worker.error_occurred.connect(self.show_error)
        self.settings_page.settings_changed.connect(self.apply_settings)
        self.dashboard_page.export_requested.connect(self.export_diagnostics)
        self.worker.set_settings(self.settings)

        self.worker.start()

    def create_sidebar(self, main_layout):

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 15, 12, 15)
        sidebar_layout.setSpacing(8)

        logo = QLabel("SYSTEM MONITOR")
        logo.setObjectName("Logo")

        sidebar_layout.addWidget(logo)

        self.navigation_buttons = []

        pages = [
            ("Dashboard", "dashboard", 0),
            ("CPU", "cpu", 1),
            ("Memory", "memory", 2),
            ("Disk", "disk", 3),
            ("Network", "network", 4),
            ("Processes", "processes", 5),
            ("Settings", "settings", 6)
        ]

        for name, page_name, index in pages:
            button = QPushButton(name)
            button.setObjectName("NavButton")
            button.setCheckable(True)

            button.clicked.connect(
                lambda checked=False, i=index, p=page_name: self.change_page(i, p)
            )

            sidebar_layout.addWidget(button)
            self.navigation_buttons.append(button)

        sidebar_layout.addStretch()

        version = QLabel("Version 1.3.1")
        version.setObjectName("Muted" )

        sidebar_layout.addWidget(version)

        main_layout.addWidget(sidebar)

    def create_content(self, main_layout):

        content = QFrame()
        content.setObjectName("Content")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.pages = QStackedWidget()

        # Dashboard
        self.dashboard_page = DashboardPage()
        self.pages.addWidget(self.dashboard_page)

        # CPU
        self.cpu_page = CPUPage()
        self.pages.addWidget(self.cpu_page)

        # Memory
        self.memory_page = MemoryPage()
        self.pages.addWidget(self.memory_page)

        # Disk
        self.disk_page = DiskPage()
        self.pages.addWidget(self.disk_page)

        # Network
        self.network_page = NetworkPage()
        self.pages.addWidget(self.network_page)

        # Processes
        self.processes_page = ProcessesPage()
        self.pages.addWidget(self.processes_page)

        self.settings_page = SettingsPage(self.settings)
        self.pages.addWidget(self.settings_page)

        content_layout.addWidget(self.pages)

        main_layout.addWidget(content, 1)

        self.change_page(0, "dashboard")

    def change_page(self, index, page_name):

        self.pages.setCurrentIndex(index)

        if hasattr(self, "worker"):
            self.worker.set_active_page(page_name)

        for i, button in enumerate(self.navigation_buttons):
            button.setChecked(i == index)

    def update_dashboard(self, page_name: str, data: dict):
        if page_name == "dashboard":
            self._last_dashboard_data = data
        page_updaters = {
            "dashboard": self.dashboard_page,
            "cpu": self.cpu_page,
            "memory": self.memory_page,
            "disk": self.disk_page,
            "network": self.network_page,
            "processes": self.processes_page
        }
        page = page_updaters.get(page_name)

        # A user may have changed the page while a collection was in progress.
        if page is not None and page is self.pages.currentWidget():
            page.update_data(data)

    def apply_settings(self, settings: MonitorSettings) -> None:
        self.settings = settings
        self.save_settings()
        self.apply_theme(settings.theme)
        self.processes_page.configure(
            settings.process_limit, settings.process_sort_by
        )
        self.worker.set_settings(settings)

    def load_settings(self) -> MonitorSettings:
        stored = QSettings("System Monitor", "System Monitor")
        return MonitorSettings(
            update_interval_ms=int(stored.value("update_interval_ms", 1000)),
            process_limit=int(stored.value("process_limit", 50)),
            process_sort_by=str(stored.value("process_sort_by", "cpu")),
            theme=str(stored.value("theme", "dark")),
        )

    def save_settings(self) -> None:
        stored = QSettings("System Monitor", "System Monitor")
        stored.setValue("update_interval_ms", self.settings.update_interval_ms)
        stored.setValue("process_limit", self.settings.process_limit)
        stored.setValue("process_sort_by", self.settings.process_sort_by)
        stored.setValue("theme", self.settings.theme)

    def apply_theme(self, theme: str) -> None:
        self.setStyleSheet(get_style(theme))
        if hasattr(self, "dashboard_page"):
            for card in (
                self.dashboard_page.cpu_chart,
                self.dashboard_page.memory_chart,
                self.dashboard_page.disk_chart,
                self.dashboard_page.network_chart,
            ):
                card.chart.set_theme(theme)

    def export_diagnostics(self) -> None:
        if not self._last_dashboard_data:
            QMessageBox.information(
                self, "Diagnostics", "Wait for the first dashboard update."
            )
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export diagnostics", "system-monitor-diagnostics.json",
            "JSON files (*.json)"
        )
        if not path:
            return
        try:
            export_diagnostics(path, self._last_dashboard_data, self.settings)
        except OSError as error:
            self.show_error(f"Could not export diagnostics: {error}")
            return
        QMessageBox.information(self, "Diagnostics", "Diagnostics exported successfully.")

    def show_error(self, message: str):
        QMessageBox.critical(
            self,
            "Monitoring Error",
            message
        )

    def closeEvent(self, event):
        if self.worker.isRunning():
            self.worker.requestInterruption()
            self.worker.wait()

        event.accept()

