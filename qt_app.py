from os import getcwd, path
import sys
import winreg

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSettings
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from itertools import islice


matplotlib.use('Qt5Agg')


class MotionViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_file = os.path.join(os.getcwd(), "IMU", "drive_1.csv")
        self.read_from = 0
        self.read_to = 100000
        self.read_step = 1
        self.read_column1 = 1
        self.read_column2 = 0
        self.is_integrate = False

        self.initUI()
        self.settings = QSettings("MI", "MotionViewer")
        self.loadValues()

    def initUI(self):
        self.setWindowTitle("Motion viewer")
        self.setGeometry(100, 100, 1200, 600)

        # Create widgets
        self.canvas = PlotCanvas(self, width=10, height=6)
        self.file_path_edit = QLineEdit(self.init_file)
        self.select_file_btn = QPushButton("...", self)
        self.read_from_spin = QSpinBox(self)
        self.read_from_spin.setRange(1, 99_999_999)
        self.read_from_spin.setValue(self.read_from)
        self.read_to_spin = QSpinBox(self)
        self.read_to_spin.setRange(2, 99_999_999)
        self.read_to_spin.setValue(self.read_to)
        self.read_step_spin = QSpinBox(self)
        self.read_step_spin.setRange(1, 99_999_999)
        self.read_step_spin.setValue(self.read_step)
        self.read_column1_spin = QSpinBox(self)
        self.read_column1_spin.setRange(0, 99_999_999)
        self.read_column1_spin.setValue(self.read_column1)
        self.read_column2_spin = QSpinBox(self)
        self.read_column2_spin.setRange(0, 99_999_999)
        self.read_column2_spin.setValue(self.read_column2)
        self.integrate_check = QCheckBox("Integrate", self)
        self.read_btn = QPushButton("Read", self)

        # Create layout
        main_layout = QHBoxLayout()
        top_layout = QHBoxLayout()
        left_layout = QFormLayout()
        right_layout = QVBoxLayout()

        top_layout.addWidget(QLabel("File Path"))
        top_layout.addWidget(self.file_path_edit)
        top_layout.addWidget(self.select_file_btn)

        left_layout.addRow(self.read_btn)
        left_layout.addRow("First row",self.read_from_spin)
        left_layout.addRow("Last row", self.read_to_spin)
        left_layout.addRow("Step", self.read_step_spin)
        left_layout.addRow("Column 1", self.read_column1_spin)
        left_layout.addRow(self.integrate_check)
        left_layout.addRow("Column 2", self.read_column2_spin)
        left_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        right_layout.addLayout(top_layout)
        right_layout.addWidget(self.canvas)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        # Create central widget and set layout
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Connect signals to slots
        self.select_file_btn.clicked.connect(self.selectFile)
        self.read_btn.clicked.connect(self.readLines)

    def readLines(self):
        self.file_path = self.file_path_edit.text()
        self.read_from = self.read_from_spin.value()
        self.read_to = self.read_to_spin.value()
        self.read_step = self.read_step_spin.value()
        self.read_column1 = self.read_column1_spin.value()
        self.read_column2 = self.read_column2_spin.value()
        self.is_integrate = self.integrate_check.isChecked()

        with open(self.file_path, 'r') as f:
            data = list(zip(*map(lambda x: (float(x[self.read_column1 - 1]), float(x[self.read_column2 - 1])),
                                 map(lambda x: x[:-1].split(";"),
                                     islice(f, self.read_from, self.read_to, self.read_step)))))

        axisX = list(range(self.read_from, self.read_to, self.read_step))
        self.canvas.updateGraph(axisX, data, self.read_column1,self.read_column2, self.is_integrate)

    def selectFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "",
                                                   "CSV Files (*.csv);;TXT Files (*.txt);;All Files (*)")
        if file_path:
            self.file_path_edit.setText(file_path)

    def loadValues(self):
        self.file_path_edit.setText(self.settings.value('filePath', self.init_file))
        self.read_from_spin.setValue(int(self.settings.value('readFrom', self.read_from)))
        self.read_to_spin.setValue(int(self.settings.value('readTo', self.read_to)))
        self.read_step_spin.setValue(int(self.settings.value('readStep', self.read_step)))
        self.read_column1_spin.setValue(int(self.settings.value('column1', self.read_column1)))
        self.read_column2_spin.setValue(int(self.settings.value('column2', self.read_column2)))
        self.integrate_check.setChecked(self.settings.value('isIntegrate', self.is_integrate, type=bool))

    def closeEvent(self, event):
        matplotlib.pyplot.close()

        self.settings.setValue('filePath', self.file_path_edit.text())
        self.settings.setValue('readFrom', self.read_from_spin.value())
        self.settings.setValue('readTo', self.read_to_spin.value())
        self.settings.setValue('readStep', self.read_step_spin.value())
        self.settings.setValue('column1', self.read_column1_spin.value())
        self.settings.setValue('column2', self.read_column2_spin.value())
        self.settings.setValue('isIntegrate', self.integrate_check.isChecked())

        event.accept()


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4):
        self.fig = plt.figure(figsize=(width, height))
        self.fig.tight_layout()

        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def updateGraph(self, axisX, data, column1, column2, is_integrate):

        self.fig.clear()
        ax = self.fig.subplots()

        len_data = len(data[0])
        if column1:
            ax.plot(axisX[:len_data], data[0], color="tab:blue", label='Column 1')
            ax.tick_params(axis='y', labelcolor="tab:blue")

        if is_integrate:
            integrated_data = []
            integral = 0.0
            for i in range(len_data):
                integral += data[0][i]
                integrated_data.append(integral)

            ax2 = ax.twinx()
            ax2.plot(axisX[:len_data], integrated_data, label="Integrated Column 1", color="tab:orange")
            ax2.tick_params(axis='y', labelcolor="tab:orange")

        if column2:
            ax3 = ax.twinx()
            ax3.plot(axisX[:len_data], data[1], color="tab:red", label='Column 2')
            ax3.tick_params(axis='y', labelcolor="tab:red")

        # ax.legend()
        self.draw()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MotionViewerApp()
    window.show()
    sys.exit(app.exec_())
