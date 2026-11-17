
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
    QPushButton,
    QScrollArea,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

from app.gui.history_chart import HistoryChart


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

    export_requested = Signal()

    def __init__(self):
        super().__init__()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("DashboardScroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        self.scroll_area.setWidget(content)
        root_layout.addWidget(self.scroll_area)

        main_layout = QVBoxLayout(content)
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

        self.cards_layout = cards_layout
        self.metric_cards = (
            self.cpu_card, self.memory_card, self.disk_card, self.network_card
        )

        main_layout.addLayout(cards_layout)

        history_title = QLabel("RECENT ACTIVITY")
        history_title.setObjectName("CardTitle")
        main_layout.addWidget(history_title)

        charts_layout = QGridLayout()
        charts_layout.setSpacing(18)
        self.cpu_chart = self.create_chart_card("CPU USAGE", "#60A5FA")
        self.memory_chart = self.create_chart_card("MEMORY USAGE", "#A78BFA")
        self.disk_chart = self.create_chart_card("DISK USAGE", "#34D399")
        self.network_chart = self.create_chart_card("NETWORK MB/s", "#F59E0B", 10.0)
        self.charts_layout = charts_layout
        self.chart_cards = (
            self.cpu_chart, self.memory_chart, self.disk_chart,
            self.network_chart
        )
        main_layout.addLayout(charts_layout)

        self.export_button = QPushButton("Export diagnostics…")
        self.export_button.clicked.connect(self.export_requested)
        main_layout.addWidget(self.export_button, 0)

        info = QLabel(
            "System Monitor | Data collection will be connected next"
        )
        info.setObjectName("Muted")

        main_layout.addWidget(info)
        self._grid_columns = None
        self.update_grid_layouts()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_grid_layouts()

    def update_grid_layouts(self) -> None:
        """Use one column when the content area can no longer fit two cards."""
        columns = 1 if self.width() < 850 else 2
        if columns == self._grid_columns:
            return
        self._grid_columns = columns
        self.populate_grid(self.cards_layout, self.metric_cards, columns)
        self.populate_grid(self.charts_layout, self.chart_cards, columns)

    @staticmethod
    def populate_grid(layout: QGridLayout, widgets: tuple, columns: int) -> None:
        while layout.count():
            layout.takeAt(0)
        for index, widget in enumerate(widgets):
            row, column = divmod(index, columns)
            layout.addWidget(widget, row, column)
        for column in range(2):
            layout.setColumnStretch(column, 1 if column < columns else 0)

    @staticmethod
    def create_chart_card(title: str, color: str, maximum: float = 100.0) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card.setMinimumHeight(160)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        label = QLabel(title)
        label.setObjectName("CardTitle")
        chart = HistoryChart(color, maximum)
        chart.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(label)
        layout.addWidget(chart)
        card.chart = chart
        return card

    def update_data(self, data: dict) -> None:

        # CPU
        cpu_usage = data["cpu"]["dynamic"]["percentage"]
        self.cpu_card.update_value(f"{cpu_usage:.1f} %")
        self.cpu_chart.chart.add_sample(cpu_usage)

        # MEMORY
        memory_usage = data["memory"]["dynamic"]["percent"]
        self.memory_card.update_value(f"{memory_usage:.1f} %")
        self.memory_chart.chart.add_sample(memory_usage)

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
            self.disk_chart.chart.add_sample(disk_usage)

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

        total_speed_mb = total_speed / (1024 ** 2)

        self.network_card.update_value(f"{total_speed_mb:.2f} MB/s")
        self.network_chart.chart.add_sample(total_speed_mb)
