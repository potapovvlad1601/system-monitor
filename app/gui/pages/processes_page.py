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

    MAX_TABLE_ROWS = 100

    def __init__(self):
        super().__init__()
        self.process_limit = 50
        self.process_sort_by = "cpu"
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
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.processes_table.setColumnWidth(0, 80)
        self.processes_table.setColumnWidth(2, 150)
        self.processes_table.setColumnWidth(3, 100)
        self.processes_table.setColumnWidth(4, 80)
        self.processes_table.setColumnWidth(5, 90)
        self.processes_table.setColumnWidth(6, 110)
        self.create_table_items()

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

    def create_table_items(self) -> None:
        """Create table items once; later updates only replace their text."""
        alignments = (
            Qt.AlignmentFlag.AlignRight,
            Qt.AlignmentFlag.AlignLeft,
            Qt.AlignmentFlag.AlignLeft,
            Qt.AlignmentFlag.AlignLeft,
            Qt.AlignmentFlag.AlignRight,
            Qt.AlignmentFlag.AlignRight,
            Qt.AlignmentFlag.AlignRight
        )
        self.processes_table.setRowCount(self.MAX_TABLE_ROWS)

        for row in range(self.MAX_TABLE_ROWS):
            for column, alignment in enumerate(alignments):
                self.processes_table.setItem(
                    row, column, self.create_table_item("", alignment)
                )
            self.processes_table.setRowHidden(row, True)

    def configure(self, process_limit: int, process_sort_by: str) -> None:
        self.process_limit = process_limit
        self.process_sort_by = process_sort_by

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

        sort_keys = {
            "cpu": lambda row: (row["cpu_percent"], row["memory_percent"]),
            "memory": lambda row: (
                row["memory_percent"], row["cpu_percent"]
            ),
            "pid": lambda row: row["pid"]
        }
        rows.sort(
            key=sort_keys[self.process_sort_by],
            reverse=self.process_sort_by != "pid"
        )
        rows = rows[:self.process_limit]

        self.total_processes.value_label.setText(str(total_count))
        self.running_processes.value_label.setText(str(running_count))
        self.sleeping_processes.value_label.setText(str(sleeping_count))
        self.total_memory.value_label.setText(
            self.format_bytes(total_memory_rss)
        )

        self.processes_table.setUpdatesEnabled(False)
        try:
            for row_index in range(self.MAX_TABLE_ROWS):
                is_visible = row_index < len(rows)
                self.processes_table.setRowHidden(row_index, not is_visible)

                if not is_visible:
                    continue

                row = rows[row_index]
                values = (
                    str(row["pid"]),
                    str(row["name"]),
                    str(row["username"]),
                    str(row["status"]),
                    f"{row['cpu_percent']:.1f}",
                    f"{row['memory_percent']:.2f}",
                    self.format_bytes(row["memory_rss"])
                )

                for column, value in enumerate(values):
                    self.processes_table.item(row_index, column).setText(value)
        finally:
            self.processes_table.setUpdatesEnabled(True)
