import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QWidget, QFrame, QRadioButton, QVBoxLayout, QHBoxLayout
from PyQt5 import QtCore, QtGui

from calculation.utils import poly_function_maker
from widgets import InputWidget
from typing import Callable

sys.path.append('./calculation')
from calculation.de_fitting import DE



class DEProgram(QMainWindow):
    _ux: Callable = None
    _uhx: Callable = None
    _coeffs: tuple = None
    _coeff_bounds: tuple = None
    _noise_scale: int = None
    _running: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_ui_components()

        self._coeffs, self._coeff_bounds, self._noise_scale = (5, -20, 5, 50, -20, -40), [-50, 50], 2
        self._nr_points, self._CP, self._F, self._max_iters, self._popsize = 40, 0.8, 0.5, 300, 100
        self.coeffs_input_frame.input_field.setText(' '.join(map(str, self._coeffs)))
        self.coeff_bounds_input_frame.input_field.setText(' '.join(map(str, self._coeff_bounds)))
        self.noise_std_input_frame.input_field.setText(str(self._noise_scale))
        self.nr_points_input_frame.input_field.setText(str(self._nr_points))
        self.crossover_probability_input_frame.input_field.setText(str(self._CP))
        self.mutation_input_frame.input_field.setText(str(self._F))
        self.iters_input_frame.input_field.setText(str(self._max_iters))
        self.pop_size_input_frame.input_field.setText(str(self._popsize))

        self.xs = np.linspace(-3, 3, self._nr_points)
        self.draw_plots()

    def _draw_ux_graph(self):
        self.ux_graph.clear()
        self.ux_graph.showGrid(x=True, y=True)
        self.ux_graph.setTitle(f'Original polynomial u(x)', color=(255, 255, 255), size='18pt')
        
        if not self._ux:
            return

        self._ys_clean = self._ux(self.xs)
        self._ys_noisy = self._ys_clean + self._noise
        self.ux_graph.plot(self.xs, self._ys_clean)

        scatter = pg.ScatterPlotItem(size=10, brush=pg.mkBrush(255, 255, 255, 120))
        spots = [{'pos': (self.xs[i], self._ys_noisy[i]), 'data': 1} for i in range(len(self.xs))]
 
        # adding points to the scatter plot
        scatter.addPoints(spots)
        self.ux_graph.addItem(scatter)

    def _draw_ux_approx_graph(self):
        self.ux_approx_graph.clear()
        self.ux_approx_graph.showGrid(x=True, y=True)
        self.ux_approx_graph.setTitle(f'Polynomial u(x) fitted with DE', color=(255, 255, 255), size='18pt')
        if not self._uhx:
            return

        self.ux_approx_graph.plot(self.xs, list(map(self._uhx, self.xs)))

        scatter = pg.ScatterPlotItem(size=10, brush=pg.mkBrush(255, 255, 255, 120))
        spots = [{'pos': (self.xs[i], self._ys_noisy[i]), 'data': 1} for i in range(len(self.xs))]
 
        # adding points to the scatter plot
        scatter.addPoints(spots)
        self.ux_approx_graph.addItem(scatter)

    def draw_plots(self):
        self._draw_ux_graph()
        self._draw_ux_approx_graph()

    def validate_input_params(self):
        try:
            params = (
                self.nr_points_input_frame.input_field.text(),
                self.crossover_probability_input_frame.input_field.text(),
                self.mutation_input_frame.input_field.text(),
                self.iters_input_frame.input_field.text(),
                self.coeffs_input_frame.input_field.text(),
                self.coeff_bounds_input_frame.input_field.text(),
                self.pop_size_input_frame.input_field.text(),
                self.noise_std_input_frame.input_field.text(),
            )
            if self._running:
                return
            if not all(params):
                raise Exception('Please enter all required fields')
            
            nr_points, CP, F, max_iters, coeffs, coeff_bounds, popsize, noise_std = params
            self._nr_points, self._CP, self._F, self._max_iters, self._popsize = int(nr_points), float(CP), float(F), int(max_iters), int(popsize)

            self._coeffs, self._ux = poly_function_maker(coeffs)
            self._coeff_bounds = list(map(float, coeff_bounds.split(' ')))
            self.error_label.setText('')

            self.xs = np.linspace(-3, 3, self._nr_points)
            self._noise_scale = float(noise_std)
            self._noise = np.random.uniform(-self._noise_scale // 2, self._noise_scale // 2, size=len(self.xs))
        except Exception as ex:
            print(ex)
            self.error_label.setText(str(ex))

    def find_approx(self):
        try:
            self._running = True
            self._draw_ux_graph()
            for it, solution_coeffs, best_obj in DE(self._popsize, self._CP, self._F, self._max_iters, self._coeff_bounds, 
                                                      self.xs, self._ys_noisy, len(self._coeffs), verbose=True):
                self._solution_coeffs, self._uhx = poly_function_maker(solution_coeffs)
                self.error_frame.input_field.setText(str(round(best_obj, 4)))
                self.iters_frame.input_field.setText(str(it))
                self._draw_ux_approx_graph()
                QtCore.QCoreApplication.processEvents()
            self.iters_frame.input_field.setText(str(self._max_iters))
            self._draw_ux_approx_graph()
        except Exception as ex:
            self.error_label.setText(f'Unable to plot functions: {ex}')
        finally:
            self._running = False

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

        self.nr_points_input_frame = InputWidget(self.config_frame, 'Nr points:')
        self.nr_points_input_frame.input_field.textChanged.connect(self.validate_input_params)
        self.config_frame_layout.addWidget(self.nr_points_input_frame)

        self.coeffs_input_frame = InputWidget(self.config_frame, 'Poly coefficients:')
        self.coeffs_input_frame.input_field.textChanged.connect(self.validate_input_params)
        self.config_frame_layout.addWidget(self.coeffs_input_frame)

        self.coeff_bounds_input_frame = InputWidget(self.config_frame, 'Coeff bounds:')
        self.coeff_bounds_input_frame.input_field.textChanged.connect(self.validate_input_params)
        self.config_frame_layout.addWidget(self.coeff_bounds_input_frame)

        self.pop_size_input_frame = InputWidget(self.config_frame, 'Population size:')
        self.pop_size_input_frame.input_field.textChanged.connect(self.validate_input_params)
        self.config_frame_layout.addWidget(self.pop_size_input_frame)

        self.crossover_probability_input_frame = InputWidget(self.config_frame, 'Crossover probability:')
        self.crossover_probability_input_frame.input_field.textChanged.connect(self.validate_input_params)
        self.config_frame_layout.addWidget(self.crossover_probability_input_frame)

        self.mutation_input_frame = InputWidget(self.config_frame, 'Mutation:')
        self.mutation_input_frame.input_field.textChanged.connect(self.validate_input_params)
        self.config_frame_layout.addWidget(self.mutation_input_frame)

        self.iters_input_frame = InputWidget(self.config_frame, 'Nr iterations:')
        self.iters_input_frame.input_field.textChanged.connect(self.validate_input_params)
        self.config_frame_layout.addWidget(self.iters_input_frame)

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

        self.iters_frame = InputWidget(self.output_frame, 'Fitted coefficients', enabled=False)
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
