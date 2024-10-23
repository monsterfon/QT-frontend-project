from PyQt6.QtWidgets import QApplication, QSpinBox, QDoubleSpinBox, QVBoxLayout, QWidget

app = QApplication([])

window = QWidget()
layout = QVBoxLayout()


spin_box.setRange(0, 100)  # Set range from 0 to 100
layout.addWidget(spin_box)

double_spin_box = QDoubleSpinBox()
double_spin_box.setRange(0.0, 100.0)  # Set range from 0.0 to 100.0
double_spin_box.setDecimals(2)  # Set precision to 2 decimal places
layout.addWidget(double_spin_box)

window.setLayout(layout)
window.show()

app.exec()
