
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QStackedWidget
)

from app.gui.pages.dashboard import DashboardPage
from app.gui.pages.cpu_page import CPUPage
from app.gui.pages.memory_page import MemoryPage
from app.gui.pages.disk_page import DiskPage
from app.gui.pages.network_page import NetworkPage
from app.gui.pages.processes_page import ProcessesPage

from PySide6.QtWidgets import QMessageBox
from app.gui.workers import SystemMonitorWorker

from app.gui.styles import MAIN_STYLE


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("System Monitor")
        self.resize(1200, 750)
        self.setMinimumSize(900, 600)

        self.setStyleSheet(MAIN_STYLE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.create_sidebar(main_layout)
        self.create_content(main_layout)

        self.worker = SystemMonitorWorker(self)

        self.worker.data_updated.connect(self.update_dashboard)
        self.worker.error_occurred.connect(self.show_error)

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
            ("Dashboard", 0),
            ("CPU", 1),
            ("Memory", 2),
            ("Disk", 3),
            ("Network", 4),
            ("Processes", 5),
            ("Settings", 6)
        ]

        for name, index in pages:
            button = QPushButton(name)
            button.setObjectName("NavButton")
            button.setCheckable(True)

            button.clicked.connect(
                lambda checked=False, i=index: self.change_page(i)
            )

            sidebar_layout.addWidget(button)
            self.navigation_buttons.append(button)

        sidebar_layout.addStretch()

        version = QLabel("Version 1.2.0")
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

        # Placeholder pages
        page_names = [
            "Settings"
        ]

        for name in page_names:
            placeholder = QWidget()

            layout = QVBoxLayout(placeholder)

            label = QLabel(f"{name} page")
            label.setObjectName("PageTitle")

            layout.addWidget(label)
            layout.addStretch()

            self.pages.addWidget(placeholder)

        content_layout.addWidget(self.pages)

        main_layout.addWidget(content, 1)

        self.change_page(0)

    def change_page(self, index):

        self.pages.setCurrentIndex(index)

        for i, button in enumerate(self.navigation_buttons):
            button.setChecked(i == index)

    def update_dashboard(self, data: dict):
        self.dashboard_page.update_data(data)
        self.cpu_page.update_data(data)
        self.memory_page.update_data(data)
        self.disk_page.update_data(data)
        self.network_page.update_data(data)
        self.processes_page.update_data(data)

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

