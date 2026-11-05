from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QScrollArea
)


class NetworkPage(QWidget):

    def __init__(self):
        super().__init__()

        self.interface_cards = {}

        self.create_ui()

    def create_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(22)

        title = QLabel("Network")
        title.setObjectName("PageTitle")

        subtitle = QLabel("Network interfaces and real-time traffic")
        subtitle.setObjectName("Muted")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        summary_layout = QGridLayout()
        summary_layout.setSpacing(18)

        self.upload_card = self.create_summary_card(
            "TOTAL UPLOAD",
            "-- MB/s"
        )

        self.download_card = self.create_summary_card(
            "TOTAL DOWNLOAD",
            "-- MB/s"
        )

        self.interfaces_card = self.create_summary_card(
            "ACTIVE INTERFACES",
            "--"
        )

        self.total_traffic_card = self.create_summary_card(
            "TOTAL TRAFFIC",
            "-- MB/s"
        )

        summary_layout.addWidget(self.upload_card, 0, 0)
        summary_layout.addWidget(self.download_card, 0, 1)
        summary_layout.addWidget(self.interfaces_card, 1, 0)
        summary_layout.addWidget(self.total_traffic_card, 1, 1)

        main_layout.addLayout(summary_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.interfaces_container = QWidget()

        self.interfaces_layout = QVBoxLayout(self.interfaces_container)
        self.interfaces_layout.setContentsMargins(0, 0, 0, 0)
        self.interfaces_layout.setSpacing(15)
        self.interfaces_layout.addStretch()

        scroll_area.setWidget(self.interfaces_container)

        main_layout.addWidget(scroll_area)

    @staticmethod
    def create_summary_card(title: str, value: str) -> QFrame:
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

    def create_interface_card(self, interface: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        title = QLabel(interface)
        title.setObjectName("CardTitle")

        status = QLabel("Status: --")
        status.setObjectName("Muted")

        speed = QLabel("Interface speed: -- Mbps")
        speed.setObjectName("Muted")

        upload = QLabel("Upload: -- MB/s")
        upload.setObjectName("Muted")

        download = QLabel("Download: -- MB/s")
        download.setObjectName("Muted")

        sent = QLabel("Sent: --")
        sent.setObjectName("Muted")

        received = QLabel("Received: --")
        received.setObjectName("Muted")

        layout.addWidget(title)
        layout.addWidget(status)
        layout.addWidget(speed)
        layout.addWidget(upload)
        layout.addWidget(download)
        layout.addWidget(sent)
        layout.addWidget(received)

        card.status = status
        card.speed = speed
        card.upload = upload
        card.download = download
        card.sent = sent
        card.received = received

        return card

    def get_or_create_interface_card(self, interface: str) -> QFrame:
        if interface not in self.interface_cards:
            card = self.create_interface_card(interface)

            self.interfaces_layout.insertWidget(
                self.interfaces_layout.count() - 1,
                card
            )

            self.interface_cards[interface] = card

        return self.interface_cards[interface]

    @staticmethod
    def format_bytes(value: int | float | None) -> str:
        if value is None:
            return "N/A"

        if value >= 1024 ** 3:
            return f"{value / (1024 ** 3):.2f} GB"

        if value >= 1024 ** 2:
            return f"{value / (1024 ** 2):.2f} MB"

        if value >= 1024:
            return f"{value / 1024:.2f} KB"

        return f"{value:.0f} B"

    @staticmethod
    def format_speed(value: int | float | None) -> str:
        if value is None:
            return "N/A"

        return f"{value / 102:.2f} KB/s"

    def update_data(self, data: dict):
        network_data = data["network"]

        static = network_data.get("static", {})
        dynamic = network_data.get("dynamic", {})
        speed = network_data.get("speed", {})

        total_upload = 0
        total_download = 0
        active_interfaces = 0

        for interface, counters in dynamic.items():
            card = self.get_or_create_interface_card(interface)

            interface_static = static.get(interface, {})
            interface_speed = speed.get(interface, {})

            is_up = interface_static.get("is_up", False)

            if is_up:
                active_interfaces += 1

            upload_speed = interface_speed.get("upload_speed", 0)
            download_speed = interface_speed.get("download_speed", 0)

            if is_up:
                total_upload += upload_speed
                total_download += download_speed

            card.status.setText(
                f"Status: {'Up' if is_up else 'Down'}"
            )

            card.speed.setText(
                f"Interface speed: "
                f"{interface_static.get('speed_mbps', 'N/A')} Mbps"
            )

            card.upload.setText(
                f"Upload: {self.format_speed(upload_speed)}"
            )

            card.download.setText(
                f"Download: {self.format_speed(download_speed)}"
            )

            card.sent.setText(
                f"Sent: {self.format_bytes(counters.get('bytes_sent'))}"
            )

            card.received.setText(
                f"Received: {self.format_bytes(counters.get('bytes_recv'))}"
            )

        total_traffic = total_upload + total_download

        self.upload_card.value_label.setText(
            self.format_speed(total_upload)
        )

        self.download_card.value_label.setText(
            self.format_speed(total_download)
        )

        self.interfaces_card.value_label.setText(
            str(active_interfaces)
        )

        self.total_traffic_card.value_label.setText(
            self.format_speed(total_traffic)
        )