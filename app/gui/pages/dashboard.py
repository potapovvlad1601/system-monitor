
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout
)


class MetricCard(QFrame):

    def __init__(self, title: str, value: str, description: str):
        super().__init__()

        self.setObjectName("Card")
        self.setMinimumHeight(140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)

        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")

        self.value_label = QLabel(value)
        self.value_label.setObjectName("CardValue")

        description_label = QLabel(description)
        description_label.setObjectName("Muted")

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(description_label)
        layout.addStretch()

    def update_value(self, value: str):
        self.value_label.setText(value)


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(22)

        title = QLabel("System Overview")
        title.setObjectName("PageTitle")

        subtitle = QLabel(
            "Monitor your system performance in real time"
        )
        subtitle.setObjectName("Muted")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        cards_layout = QGridLayout()
        cards_layout.setSpacing(18)

        self.cpu_card = MetricCard(
            "CPU USAGE",
            "-- %",
            "Processor utilization"
        )

        self.memory_card = MetricCard(
            "MEMORY",
            "-- %",
            "RAM utilization"
        )

        self.disk_card = MetricCard(
            "DISK",
            "-- %",
            "Storage utilization"
        )

        self.network_card = MetricCard(
            "NETWORK",
            "-- MB/s",
            "Network activity"
        )

        cards_layout.addWidget(self.cpu_card, 0, 0)
        cards_layout.addWidget(self.memory_card, 0, 1)
        cards_layout.addWidget(self.disk_card, 1, 0)
        cards_layout.addWidget(self.network_card, 1, 1)

        main_layout.addLayout(cards_layout)

        main_layout.addStretch()

        info = QLabel(
            "System Monitor | Data collection will be connected next"
        )
        info.setObjectName("Muted")

        main_layout.addWidget(info)

    def update_data(self, data: dict) -> None:

        # CPU
        cpu_usage = data["cpu"]["dynamic"]["percentage"]
        self.cpu_card.update_value(f"{cpu_usage:.1f} %")

        # MEMORY
        memory_usage = data["memory"]["dynamic"]["percent"]
        self.memory_card.update_value(f"{memory_usage:.1f} %")

        # DISK
        disks = data["disk"]["dynamic"]

        total_space = sum(
            disk["total"]
            for disk in disks.values()
            if "total" in disk
        )

        used_space = sum(
            disk["used"]
            for disk in disks.values()
            if "used" in disk
        )

        if total_space:
            disk_usage = used_space / total_space * 100
            self.disk_card.update_value(f"{disk_usage:.1f} %")

        # NETWORK
        network_speed = data["network"].get("speed", {})
        network_static = data["network"]["static"]

        total_speed = 0

        for interface, speed in network_speed.items():

            # Учитываем только подключённые интерфейсы.
            if network_static.get(interface, {}).get("is_up"):
                total_speed += (
                        speed["upload_speed"] + speed["download_speed"]
                )

        total_speed_mb = total_speed / 1024

        self.network_card.update_value(f"{total_speed_mb:.2f} MB/s")
