from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)
from PySide6.QtCore import Qt


class ProcessesPage(QWidget):

    def __init__(self):
        super().__init__()

        self.create_ui()

    def create_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(22)

        title = QLabel("Processes")
        title.setObjectName("PageTitle")

        subtitle = QLabel("Running processes and resource usage")
        subtitle.setObjectName("Muted")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        summary_layout = QGridLayout()
        summary_layout.setSpacing(18)

        self.total_processes = self.create_summary_card(
            "TOTAL PROCESSES",
            "--"
        )

        self.running_processes = self.create_summary_card(
            "RUNNING",
            "--"
        )

        self.sleeping_processes = self.create_summary_card(
            "SLEEPING",
            "--"
        )

        self.total_memory = self.create_summary_card(
            "PROCESS MEMORY",
            "-- MB"
        )

        summary_layout.addWidget(self.total_processes, 0, 0)
        summary_layout.addWidget(self.running_processes, 0, 1)
        summary_layout.addWidget(self.sleeping_processes, 1, 0)
        summary_layout.addWidget(self.total_memory, 1, 1)

        main_layout.addLayout(summary_layout)

        table_card = QFrame()
        table_card.setObjectName("Card")

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 18, 20, 18)
        table_layout.setSpacing(12)

        table_title = QLabel("TOP PROCESSES")
        table_title.setObjectName("CardTitle")

        self.processes_table = QTableWidget()
        self.processes_table.setColumnCount(7)
        self.processes_table.setHorizontalHeaderLabels([
            "PID",
            "Name",
            "User",
            "Status",
            "CPU %",
            "Memory %",
            "RSS"
        ])

        self.processes_table.verticalHeader().setVisible(False)
        self.processes_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.processes_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.processes_table.setAlternatingRowColors(True)
        self.processes_table.setSortingEnabled(False)

        header = self.processes_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        table_layout.addWidget(table_title)
        table_layout.addWidget(self.processes_table)

        main_layout.addWidget(table_card)

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
    def create_table_item(value: str, alignment=Qt.AlignmentFlag.AlignLeft):
        item = QTableWidgetItem(value)
        item.setTextAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)

        return item

    def update_data(self, data: dict):
        processes_data = data["processes"]

        static = processes_data.get("static", {})
        dynamic = processes_data.get("dynamic", {})

        total_count = len(dynamic)
        running_count = 0
        sleeping_count = 0
        total_memory_rss = 0

        rows = []

        for pid, process_dynamic in dynamic.items():
            process_static = static.get(pid, {})

            status = process_dynamic.get("status", "N/A")

            if status == "running":
                running_count += 1

            if status == "sleeping":
                sleeping_count += 1

            memory_rss = process_dynamic.get("memory_rss") or 0
            total_memory_rss += memory_rss

            rows.append({
                "pid": pid,
                "name": process_static.get("name", "N/A"),
                "username": process_static.get("username", "N/A"),
                "status": status,
                "cpu_percent": process_dynamic.get("cpu_percent", 0),
                "memory_percent": process_dynamic.get("memory_percent", 0),
                "memory_rss": memory_rss
            })

        rows.sort(
            key=lambda row: (
                row["cpu_percent"],
                row["memory_percent"]
            ),
            reverse=True
        )

        rows = rows[:100]

        self.total_processes.value_label.setText(str(total_count))
        self.running_processes.value_label.setText(str(running_count))
        self.sleeping_processes.value_label.setText(str(sleeping_count))
        self.total_memory.value_label.setText(
            self.format_bytes(total_memory_rss)
        )

        self.processes_table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            self.processes_table.setItem(
                row_index,
                0,
                self.create_table_item(
                    str(row["pid"]),
                    Qt.AlignmentFlag.AlignRight
                )
            )

            self.processes_table.setItem(
                row_index,
                1,
                self.create_table_item(str(row["name"]))
            )

            self.processes_table.setItem(
                row_index,
                2,
                self.create_table_item(str(row["username"]))
            )

            self.processes_table.setItem(
                row_index,
                3,
                self.create_table_item(str(row["status"]))
            )

            self.processes_table.setItem(
                row_index,
                4,
                self.create_table_item(
                    f"{row['cpu_percent']:.1f}",
                    Qt.AlignmentFlag.AlignRight
                )
            )

            self.processes_table.setItem(
                row_index,
                5,
                self.create_table_item(
                    f"{row['memory_percent']:.2f}",
                    Qt.AlignmentFlag.AlignRight
                )
            )

            self.processes_table.setItem(
                row_index,
                6,
                self.create_table_item(
                    self.format_bytes(row["memory_rss"]),
                    Qt.AlignmentFlag.AlignRight
                )
            )