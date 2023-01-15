from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QSizePolicy, QLabel, QTextEdit, QLineEdit, QRadioButton, QBoxLayout, QLayout, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5 import QtCore


class InputWidget(QWidget):
    def __init__(self, parent, label_text, enabled=True, horizontal_layout=True):
        super().__init__(parent)
        self.layout = QHBoxLayout(self) if horizontal_layout else QVBoxLayout(self)

        self.label = QLabel(self)
        self.label.setText(label_text)
        self.label.setFont(QFont('Times New Roman', 14, 1))
        self.layout.addWidget(self.label)

        self.input_field = QLineEdit(self)
        self.layout.addWidget(self.input_field)
        self.input_field.setFont(QFont('Times New Roman', 12, 1))

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.input_field.setReadOnly(not enabled)

    def changeEvent(self, a0: QtCore.QEvent):
        a0.text