import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QWidget, QFrame, QRadioButton, QVBoxLayout, QHBoxLayout
from PyQt5 import QtCore, QtGui

from utils import poly_function_maker
from widgets import InputWidget
from typing import Callable
from calculation import * 


class DEProgram(QMainWindow):
    _n: int = None
    _coeffs: tuple = None
    _coeff_bounds: tuple = None
    _noise_scale: int = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_ui_components()

        self._coeffs, self._coeff_bounds, self._noise_scale = (5, -20, 5, 50, -20, -40), [[-10, 10] for _ in range(5)], 2
        self._n = len(self._coeffs) - 1
        # self.degree_input_frame.input_field.setText(str(self._n))
        self.coeffs_input_frame.input_field.setText(' '.join(map(str, self._coeffs)))
        self.coeff_bounds_input_frame.input_field.setText(' '.join('/'.join(map(str, item)) for item in self._coeff_bounds))
        self.noise_std_input_frame.input_field.setText(str(self._noise_scale))

        self.xs = np.linspace(-3, 3, 100)
        self.draw_plots()

    def _draw_ux_graph(self):
        self.ux_graph.clear()
        self.ux_graph.showGrid(x=True, y=True)
        self.ux_graph.setTitle(f'Original polynomial u_x', color=(255, 255, 255, 0), size='18pt')
        
        if not self._ux:
            return

        self._ys_clean = np.array(list(map(self._ux, self.xs)))
        self._ys_noisy = self._ys_clean + np.random.uniform(-self._noise_scale // 2, self._noise_scale // 2, size=len(self.xs))
        self.ux_graph.plot(self.xs, self._ys_clean)

        scatter = pg.ScatterPlotItem(size=10, brush=pg.mkBrush(255, 255, 255, 120))
        spots = [{'pos': (self.xs[i], self._ys_noisy[i]), 'data': 1} for i in range(len(self.xs))]
 
        # adding points to the scatter plot
        scatter.addPoints(spots)
        self.ux_graph.addItem(scatter)
        # print(self.ux_graph.getPlotItem())

        # pen = pg.mkPen(color=(255, 0, 0))
        # self.ux_graph.plot(self.xs, list(map(fx, self.xs)), pen=pen)

    def _draw_ux_approx_graph(self):
        return NotImplemented
        self.ux_approx_graph.clear()
        self.ux_approx_graph.showGrid(x=True, y=True)
        self.ux_approx_graph.setTitle(f'Approximation of u_h', color=(255, 255, 255, 0), size='18pt')
        if not (self._n and self._uhx):
            return

        self.ux_approx_graph.plot(self.xs, list(map(self._uhx, self.xs)))

    def draw_plots(self):
        self._draw_ux_graph()
        # self._draw_ux_approx_graph()

    def validate_input_params(self):
        try:
            params = (
                # self.degree_input_frame.input_field.text(),
                self.coeffs_input_frame.input_field.text(),
                self.coeff_bounds_input_frame.input_field.text(),
                self.noise_std_input_frame.input_field.text(),
            )

            if not all(params):
                raise Exception('Please enter all required fields')
            
            coeffs, coeff_bounds, noise_std = params
            self._coeffs, self._ux = poly_function_maker(coeffs)
            self._coeff_bounds = [list(map(float, item.split('/')) for item in coeff_bounds.split(' '))]
            self._noise_scale = float(noise_std)
            self.error_label.setText('')
        except Exception as ex:
            print(ex)
            self.error_label.setText(str(ex))

    def find_approx(self):
        try:
            # self.error_frame.input_field.setText(str(round(uhx_norm1, 5)))
            # self.iters_frame.input_field.setText(str(round(uhx_norm2, 5)))
            # self.err_norm_frame.input_field.setText(str(round(e_norm, 5)))
            self.draw_plots()
        except Exception as ex:
            self.error_label.setText(f'Unable to plot functions: {ex}')

    def setup_ui_components(self):
        self.setWindowTitle('Approximating Polynomials Using Differential Evolution')

        self.setFixedHeight(960)
        self.setFixedWidth(1280)

        self.main_frame = QFrame(self)
        
        # main layout
        self.vertial_layout = QVBoxLayout(self.main_frame)
        self.vertial_layout.setContentsMargins(0, 0, 0, 0)
        self.vertial_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.header_frame = QFrame(self.main_frame)
        self.header_layout = QHBoxLayout(self.header_frame)
        
        # config frame 
        self.config_frame = QFrame(self.main_frame)
        self.config_frame.setMaximumWidth(500)

        self.config_frame_layout = QVBoxLayout(self.config_frame)
        self.config_frame_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.config_frame_layout.setContentsMargins(0, 0, 0, 0)

        self.coeffs_input_frame = InputWidget(self.config_frame, 'Poly coefficients:')
        self.coeffs_input_frame.input_field.textChanged.connect(self.validate_input_params)
        self.config_frame_layout.addWidget(self.coeffs_input_frame)

        self.coeff_bounds_input_frame = InputWidget(self.config_frame, 'Coeff bounds:')
        self.coeff_bounds_input_frame.input_field.textChanged.connect(self.validate_input_params)
        self.config_frame_layout.addWidget(self.coeff_bounds_input_frame)

        self.noise_std_input_frame = InputWidget(self.config_frame, 'Noise std:')
        self.noise_std_input_frame.input_field.textChanged.connect(self.validate_input_params)
        self.config_frame_layout.addWidget(self.noise_std_input_frame)

        # self.ux_input_frame = InputWidget(self.config_frame, 'u(x):')
        # self.ux_input_frame.input_field.textChanged.connect(self.validate_input_params)
        # self.config_frame_layout.addWidget(self.ux_input_frame)

        # self.degree_input_frame = InputWidget(self.config_frame, 'N')
        # self.degree_input_frame.input_field.textChanged.connect(self.validate_input_params)
        # self.config_frame_layout.addWidget(self.degree_input_frame)

        self.config_frame.setLayout(self.config_frame_layout)

        # output/trigger frame
        self.output_frame = QFrame(self.main_frame)
        self.output_frame_layout = QVBoxLayout(self.output_frame)

        self.calc_button = QPushButton('Approximate', self)
        self.calc_button.clicked.connect(self.find_approx)
        self.output_frame_layout.addWidget(self.calc_button)
        
        self.error_frame = InputWidget(self.output_frame, 'Error', enabled=False)
        self.error_frame.setFixedHeight(30)
        self.output_frame_layout.addWidget(self.error_frame)

        self.iters_frame = InputWidget(self.output_frame, 'Number of iters', enabled=False)
        self.iters_frame.setFixedHeight(30)
        self.output_frame_layout.addWidget(self.iters_frame)

        # self.err_norm_frame = InputWidget(self.output_frame, 'Норма функції похибки', enabled=False)
        # self.err_norm_frame.setFixedHeight(30)
        # self.output_frame_layout.addWidget(self.err_norm_frame)

        self.error_label = QLabel(self.output_frame)
        self.error_label.setText('remove err') 
        self.error_label.setStyleSheet('color:red')
        self.output_frame_layout.addWidget(self.error_label)

        # header frame
        self.header_frame.setFixedHeight(200)
        
        self.header_layout.addWidget(self.config_frame)
        self.header_layout.addWidget(self.output_frame)
        self.header_frame.setLayout(self.header_layout)

        self.vertial_layout.addWidget(self.header_frame)

        self.plot_frame = QFrame(self)
        self.plot_layout = QHBoxLayout(self.plot_frame)

        self.ux_graph = pg.PlotWidget()
        self.plot_layout.addWidget(self.ux_graph)
        
        self.ux_approx_graph = pg.PlotWidget()
        self.plot_layout.addWidget(self.ux_approx_graph)
        self.plot_frame.setLayout(self.plot_layout)

        self.vertial_layout.addWidget(self.plot_frame)

        self.main_frame.setLayout(self.vertial_layout)
        self.setCentralWidget(self.main_frame)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu_window = DEProgram()
    menu_window.show()
    sys.exit(app.exec_())
