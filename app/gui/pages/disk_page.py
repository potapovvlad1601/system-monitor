from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QProgressBar,
    QScrollArea
)


class DiskPage(QWidget):

    def __init__(self):
        super().__init__()

        self.disk_cards = {}

        self.create_ui()

    def create_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(22)

        title = QLabel("Disk")
        title.setObjectName("PageTitle")

        subtitle = QLabel("Storage utilization by mounted partitions")
        subtitle.setObjectName("Muted")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        overview_card = QFrame()
        overview_card.setObjectName("Card")

        overview_layout = QVBoxLayout(overview_card)
        overview_layout.setContentsMargins(20, 18, 20, 18)
        overview_layout.setSpacing(15)

        overview_title = QLabel("TOTAL STORAGE UTILIZATION")
        overview_title.setObjectName("CardTitle")

        self.total_usage_value = QLabel("-- %")
        self.total_usage_value.setObjectName("CardValue")

        self.total_usage_bar = QProgressBar()
        self.total_usage_bar.setRange(0, 100)
        self.total_usage_bar.setValue(0)
        self.total_usage_bar.setTextVisible(False)
        self.total_usage_bar.setFixedHeight(12)

        self.total_space = QLabel("Used: -- GB / Total: -- GB")
        self.total_space.setObjectName("Muted")

        overview_layout.addWidget(overview_title)
        overview_layout.addWidget(self.total_usage_value)
        overview_layout.addWidget(self.total_usage_bar)
        overview_layout.addWidget(self.total_space)

        main_layout.addWidget(overview_card)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.disks_container = QWidget()

        self.disks_layout = QVBoxLayout(self.disks_container)
        self.disks_layout.setContentsMargins(0, 0, 0, 0)
        self.disks_layout.setSpacing(15)
        self.disks_layout.addStretch()

        scroll_area.setWidget(self.disks_container)

        main_layout.addWidget(scroll_area)

    def create_disk_card(self, mountpoint: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title = QLabel(mountpoint)
        title.setObjectName("CardTitle")

        usage_value = QLabel("-- %")
        usage_value.setObjectName("CardValue")

        usage_bar = QProgressBar()
        usage_bar.setRange(0, 100)
        usage_bar.setValue(0)
        usage_bar.setTextVisible(False)
        usage_bar.setFixedHeight(10)

        details = QLabel("Used: -- GB / Total: -- GB")
        details.setObjectName("Muted")

        device = QLabel("Device: --")
        device.setObjectName("Muted")

        filesystem = QLabel("Filesystem: --")
        filesystem.setObjectName("Muted")

        layout.addWidget(title)
        layout.addWidget(usage_value)
        layout.addWidget(usage_bar)
        layout.addWidget(details)
        layout.addWidget(device)
        layout.addWidget(filesystem)

        card.usage_value = usage_value
        card.usage_bar = usage_bar
        card.details = details
        card.device = device
        card.filesystem = filesystem

        return card

    def get_or_create_disk_card(self, mountpoint: str) -> QFrame:
        if mountpoint not in self.disk_cards:
            card = self.create_disk_card(mountpoint)

            self.disks_layout.insertWidget(
                self.disks_layout.count() - 1,
                card
            )

            self.disk_cards[mountpoint] = card

        return self.disk_cards[mountpoint]

    @staticmethod
    def format_bytes(value: int | float | None) -> str:
        if value is None:
            return "N/A"

        return f"{value / (1024 ** 3):.2f} GB"

    def update_data(self, data: dict):
        disk_data = data["disk"]
        dynamic = disk_data["dynamic"]
        static = disk_data.get("static", {})

        total_space = 0
        used_space = 0

        for mountpoint, usage in dynamic.items():
            card = self.get_or_create_disk_card(mountpoint)

            if "error" in usage:
                card.usage_value.setText("Error")
                card.details.setText(usage["error"])
                card.usage_bar.setValue(0)
                continue

            total = usage.get("total", 0)
            used = usage.get("used", 0)
            percent = usage.get("percent", 0)

            total_space += total
            used_space += used

            card.usage_value.setText(f"{percent:.1f} %")
            card.usage_bar.setValue(int(percent))

            card.details.setText(
                f"Used: {self.format_bytes(used)} / "
                f"Total: {self.format_bytes(total)}"
            )

            partition_static = static.get(mountpoint, {})

            card.device.setText(
                f"Device: {partition_static.get('device', 'N/A')}"
            )

            card.filesystem.setText(
                f"Filesystem: {partition_static.get('filesystem', 'N/A')}"
            )

        if total_space:
            total_percent = used_space / total_space * 100

            self.total_usage_value.setText(f"{total_percent:.1f} %")
            self.total_usage_bar.setValue(int(total_percent))
            self.total_space.setText(
                f"Used: {self.format_bytes(used_space)} / "
                f"Total: {self.format_bytes(total_space)}"
            )
        else:
            self.total_usage_value.setText("-- %")
            self.total_usage_bar.setValue(0)
            self.total_space.setText("Used: -- GB / Total: -- GB")