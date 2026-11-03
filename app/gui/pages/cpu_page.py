from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QProgressBar
)


class CPUPage(QWidget):

    def __init__(self):
        super().__init__()

        self.create_ui()

    def create_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(22)

        title = QLabel("CPU Performance")
        title.setObjectName("PageTitle")

        subtitle = QLabel(
            "Processor utilization and hardware information"
        )
        subtitle.setObjectName("Muted")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # CPU Usage
        usage_card = QFrame()
        usage_card.setObjectName("Card")

        usage_layout = QVBoxLayout(usage_card)
        usage_layout.setContentsMargins(20, 18, 20, 18)
        usage_layout.setSpacing(15)

        usage_title = QLabel("CPU UTILIZATION")
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

        # CPU Information
        info_layout = QGridLayout()
        info_layout.setSpacing(18)

        self.physical_cores = self.create_info_card(
            "PHYSICAL CORES", "--"
        )

        self.logical_cores = self.create_info_card(
            "LOGICAL CORES", "--"
        )

        self.frequency = self.create_info_card(
            "FREQUENCY", "-- MHz"
        )

        self.temperature = self.create_info_card(
            "TEMPERATURE", "-- °C"
        )

        info_layout.addWidget(self.physical_cores, 0, 0)
        info_layout.addWidget(self.logical_cores, 0, 1)
        info_layout.addWidget(self.frequency, 1, 0)
        info_layout.addWidget(self.temperature, 1, 1)

        main_layout.addLayout(info_layout)

        # Load Average
        load_card = QFrame()
        load_card.setObjectName("Card")

        load_layout = QVBoxLayout(load_card)
        load_layout.setContentsMargins(20, 18, 20, 18)

        load_title = QLabel("LOAD AVERAGE")
        load_title.setObjectName("CardTitle")

        self.load_average = QLabel(
            "1 min: --    5 min: --    15 min: --"
        )
        self.load_average.setObjectName("Muted")

        load_layout.addWidget(load_title)
        load_layout.addWidget(self.load_average)

        main_layout.addWidget(load_card)

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

    def update_data(self, data: dict):
        cpu_data = data["cpu"]

        static = cpu_data["static"]
        dynamic = cpu_data["dynamic"]

        # CPU utilization
        usage = dynamic.get("percentage", 0)

        self.usage_value.setText(f"{usage:.1f} %")
        self.usage_bar.setValue(int(usage))

        # Static information
        self.physical_cores.value_label.setText(
            str(static.get("physical_cores", "N/A"))
        )

        self.logical_cores.value_label.setText(
            str(static.get("logical_cores", "N/A"))
        )

        # Dynamic information
        frequency = dynamic.get("frequency_mhz")

        if frequency is not None:
            self.frequency.value_label.setText(
                f"{frequency:.0f} MHz"
            )

        temperature = dynamic.get("temperature_c")

        if temperature is not None:
            self.temperature.value_label.setText(
                f"{temperature:.1f} °C"
            )

        # Load average
        load = dynamic.get("load_average")

        if load:
            self.load_average.setText(
                f"1 min: {load.get('1_min', 0):.2f}    "
                f"5 min: {load.get('5_min', 0):.2f}    "
                f"15 min: {load.get('15_min', 0):.2f}"
            )
        else:
            self.load_average.setText("Not available")