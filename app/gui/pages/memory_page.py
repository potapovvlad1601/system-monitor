from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QProgressBar
)


class MemoryPage(QWidget):

    def __init__(self):
        super().__init__()

        self.create_ui()

    def create_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(22)

        title = QLabel("Memory")
        title.setObjectName("PageTitle")

        subtitle = QLabel("RAM utilization and memory statistics")
        subtitle.setObjectName("Muted")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        usage_card = QFrame()
        usage_card.setObjectName("Card")

        usage_layout = QVBoxLayout(usage_card)
        usage_layout.setContentsMargins(20, 18, 20, 18)
        usage_layout.setSpacing(15)

        usage_title = QLabel("MEMORY UTILIZATION")
        usage_title.setObjectName("CardTitle")

        self.usage_value = QLabel("-- %")
        self.usage_value.setObjectName("CardValue")

        self.usage_bar = QProgressBar()
        self.usage_bar.setRange(0, 100)
        self.usage_bar.setValue(0)
        self.usage_bar.setTextVisible(False)
        self.usage_bar.setFixedHeight(12)

        usage_layout.addWidget(usage_title)
        usage_layout.addWidget(self.usage_value)
        usage_layout.addWidget(self.usage_bar)

        main_layout.addWidget(usage_card)

        info_layout = QGridLayout()
        info_layout.setSpacing(18)

        self.total_memory = self.create_info_card("TOTAL", "-- GB")
        self.used_memory = self.create_info_card("USED", "-- GB")
        self.available_memory = self.create_info_card("AVAILABLE", "-- GB")
        self.free_memory = self.create_info_card("FREE", "-- GB")

        info_layout.addWidget(self.total_memory, 0, 0)
        info_layout.addWidget(self.used_memory, 0, 1)
        info_layout.addWidget(self.available_memory, 1, 0)
        info_layout.addWidget(self.free_memory, 1, 1)

        main_layout.addLayout(info_layout)
        main_layout.addStretch()

    @staticmethod
    def create_info_card(title: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)

        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")

        value_label = QLabel(value)
        value_label.setObjectName("CardValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        card.value_label = value_label

        return card

    @staticmethod
    def format_bytes(value: int | float | None) -> str:
        if value is None:
            return "N/A"

        return f"{value / (1024 ** 3):.2f} GB"

    def update_data(self, data: dict):
        memory_data = data["memory"]["dynamic"]

        percent = memory_data.get("percent", 0)

        self.usage_value.setText(f"{percent:.1f} %")
        self.usage_bar.setValue(int(percent))

        self.total_memory.value_label.setText(
            self.format_bytes(memory_data.get("total"))
        )

        self.used_memory.value_label.setText(
            self.format_bytes(memory_data.get("used"))
        )

        self.available_memory.value_label.setText(
            self.format_bytes(memory_data.get("available"))
        )

        self.free_memory.value_label.setText(
            self.format_bytes(memory_data.get("free"))
        )