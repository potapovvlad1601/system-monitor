
DARK_STYLE = """
QMainWindow {
    background-color: #111827;
}

QWidget {
    color: #E5E7EB;
    font-family: "Segoe UI";
    font-size: 13px;
}

QFrame#Sidebar {
    background-color: #172033;
    border: none;
}

QLabel#Logo {
    font-size: 21px;
    font-weight: bold;
    color: #60A5FA;
    padding: 15px;
}

QPushButton#NavButton {
    background-color: transparent;
    color: #9CA3AF;
    border: none;
    text-align: left;
    padding: 13px 18px;
    border-radius: 7px;
    font-size: 14px;
}

QPushButton#NavButton:hover {
    background-color: #263449;
    color: white;
}

QPushButton#NavButton:checked {
    background-color: #2563EB;
    color: white;
}

QFrame#Card {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
}

QLabel#CardTitle {
    color: #9CA3AF;
    font-size: 14px;
}

QLabel#CardValue {
    font-size: 30px;
    font-weight: bold;
    color: #60A5FA;
}

QLabel#PageTitle {
    font-size: 25px;
    font-weight: bold;
    color: white;
}

QLabel#Muted {
    color: #9CA3AF;
}

QComboBox {
    background-color: #111827;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 180px;
}

QComboBox:hover, QComboBox:focus {
    border-color: #60A5FA;
}

QComboBox QAbstractItemView {
    background-color: #1E293B;
    selection-background-color: #2563EB;
}

QFrame#Content {
    background-color: #111827;
    border: none;
}

QProgressBar {
    background-color: #0F172A;
    border: none;
    border-radius: 5px;
}

QProgressBar::chunk {
    background-color: #2563EB;
    border-radius: 5px;
}
"""

LIGHT_STYLE = """
QMainWindow, QFrame#Content { background-color: #F1F5F9; }
QWidget { color: #1E293B; font-family: "Segoe UI"; font-size: 13px; }
QFrame#Sidebar { background-color: #FFFFFF; border: none; }
QLabel#Logo { font-size: 21px; font-weight: bold; color: #2563EB; padding: 15px; }
QPushButton#NavButton { background-color: transparent; color: #475569; border: none; text-align: left; padding: 13px 18px; border-radius: 7px; font-size: 14px; }
QPushButton#NavButton:hover { background-color: #E2E8F0; color: #0F172A; }
QPushButton#NavButton:checked { background-color: #2563EB; color: white; }
QFrame#Card { background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 12px; }
QLabel#CardTitle, QLabel#Muted { color: #64748B; }
QLabel#CardValue { font-size: 30px; font-weight: bold; color: #2563EB; }
QLabel#PageTitle { font-size: 25px; font-weight: bold; color: #0F172A; }
QComboBox { background-color: #FFFFFF; border: 1px solid #94A3B8; border-radius: 6px; padding: 8px 12px; min-width: 180px; }
QComboBox:hover, QComboBox:focus { border-color: #2563EB; }
QComboBox QAbstractItemView { background-color: #FFFFFF; selection-background-color: #2563EB; }
QProgressBar { background-color: #E2E8F0; border: none; border-radius: 5px; }
QProgressBar::chunk { background-color: #2563EB; border-radius: 5px; }
"""

MAIN_STYLE = DARK_STYLE


def get_style(theme: str) -> str:
    return LIGHT_STYLE if theme == "light" else DARK_STYLE
