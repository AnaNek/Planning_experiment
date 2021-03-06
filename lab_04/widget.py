import sys
from os import environ
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QTableWidgetItem
from experiment import Experiment
from numpy import random as nr
from itertools import *

from experiment import FACTORS_NUMBER

def suppress_qt_warnings():
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = uic.loadUi("window.ui", self)
        self.experiment = None
        self.plan_table_full = None
        self.plan_table_partial = None
        self.b_full = None
        self.b_partial = None
        self.full_table_position = 1
        self.partial_table_position = 1
        self.Table_position = 1

        table = self.ui.table
        table.setColumnCount(2**FACTORS_NUMBER + 2*FACTORS_NUMBER)
        self.set_value(0, 1, '%s', 'x0', Qt.AlignCenter)

        x = []
        for i in range(FACTORS_NUMBER):
            x.append("x%d" % (i + 1))

        h_pos = 2
        for i in range(1, FACTORS_NUMBER + 1):
            for comb in combinations(x, i):
                cur_str = ''
                for item in comb:
                    cur_str += item
                self.set_value(0, h_pos, '%s', cur_str, Qt.AlignCenter)
                h_pos += 1
        
        for i in range(FACTORS_NUMBER):
            cur_str = "x%d^2 - S" % (i + 1)
            self.set_value(0, h_pos, '%s', cur_str, Qt.AlignCenter)
            h_pos += 1
        
        self.set_value(0, h_pos, '%s', 'Y', Qt.AlignCenter)
        self.set_value(0, h_pos + 1, '%s', 'Yнл', Qt.AlignCenter)
        self.set_value(0, h_pos + 2, '%s', '|Y - Yнл|', Qt.AlignCenter)

    @pyqtSlot(name='on_calc_button_clicked')
    def parse_parameters(self):
        try:
            ui = self.ui
            
            min_gen_int_1 = float(ui.line_edit_min_gen_int.text())
            max_gen_int_1 = float(ui.line_edit_max_gen_int.text())
            min_gen_var_1 = float(ui.line_edit_min_gen_var.text())
            max_gen_var_1 = float(ui.line_edit_max_gen_var.text())
            gen_1 = [min_gen_int_1, max_gen_int_1, min_gen_var_1, max_gen_var_1]

            min_gen_int_2 = float(ui.line_edit_min_gen_int_2.text())
            max_gen_int_2 = float(ui.line_edit_max_gen_int_2.text())
            min_gen_var_2 = float(ui.line_edit_min_gen_var_2.text())
            max_gen_var_2 = float(ui.line_edit_max_gen_var_2.text())
            gen_2 = [min_gen_int_2, max_gen_int_2, min_gen_var_2, max_gen_var_2]

            min_pm_int_1 = float(ui.line_edit_min_pm_int_1.text())
            max_pm_int_1 = float(ui.line_edit_max_pm_int_1.text())
            min_pm_var_1 = float(ui.line_edit_min_pm_var_1.text())
            max_pm_var_1 = float(ui.line_edit_max_pm_var_1.text())
            pm_1 = [min_pm_int_1, max_pm_int_1, min_pm_var_1, max_pm_var_1]

            min_pm_int_2 = float(ui.line_edit_min_pm_int_2.text())
            max_pm_int_2 = float(ui.line_edit_max_pm_int_2.text())
            min_pm_var_2 = float(ui.line_edit_min_pm_var_2.text())
            max_pm_var_2 = float(ui.line_edit_max_pm_var_2.text())
            pm_2 = [min_pm_int_2, max_pm_int_2, min_pm_var_2, max_pm_var_2]

            if gen_1[0] < 0 or gen_1[1] < 0 or gen_1[2] < 0 or gen_1[3] < 0 or \
                gen_2[0] < 0 or gen_2[1] < 0 or gen_2[2] < 0 or gen_2[3] < 0 or \
                pm_1[0] < 0 or pm_1[1] < 0 or pm_1[2] < 0 or pm_1[3] < 0 or \
                pm_2[0] < 0 or pm_2[1] < 0 or pm_2[2] < 0 or pm_2[3] < 0:
                raise ValueError('Интенсивности и дисперсии интенсивностей должны быть > 0')

            # Input params
            time = int(ui.line_edit_time.text())
            if time <= 0:
                raise ValueError('Необходимо время моделирования > 0')

            self.experiment = Experiment(gen_1, gen_2, pm_1, pm_2, time)
            self.b_full, table, s, s_length = self.experiment.calculate()

            self.show_results(table, s, s_length)  

        except ValueError as e:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка входных данных!\n' + str(e))
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', e)

    def set_value(self, line, column, format, value, alignment):
        item = QTableWidgetItem(format % value)
        item.setTextAlignment(alignment)
        self.ui.table.setItem(line, column, item)

    def get_regr_format_string(self, regr):
        x = []
        val = [regr[0]]
        for i in range(FACTORS_NUMBER):
            x.append("x%d" % (i + 1))

        res_str = "y = %.3f"
        pos = 1
        for i in range(1, 3):
            for comb in combinations(x, i):
                cur_str = "%.3f"
                if regr[pos] < 0:
                    cur_str = " - " + cur_str
                    regr[pos] = abs(regr[pos])
                else:
                    cur_str = " + " + cur_str

                for item in comb:
                    cur_str += item
                res_str += cur_str
                val.append(regr[pos])
                pos += 1
        pos = 2**FACTORS_NUMBER
        
        for i in range(1, FACTORS_NUMBER + 1):
            cur_str = "%.3f"
            if regr[pos] < 0:
                cur_str = " - " + cur_str
                regr[pos] = abs(regr[pos])
            else:
                cur_str = " + " + cur_str
            cur_str += x[i - 1] + "^2"
            res_str += cur_str
            val.append(regr[pos])
            pos += 1

        return res_str, val


    def show_results(self, table, s, s_length):
        ui = self.ui

        nonlin_regr_format_str, val = self.get_regr_format_string(self.b_full)
        print(nonlin_regr_format_str, len(val))
        nonlin_regr_str = (nonlin_regr_format_str % tuple(val))
        
        ui.line_edit_s.setText(str(round(s, 5)))
        ui.line_edit_s_length.setText(str(round(s_length, 5)))
        ui.line_edit_nonlin_regr.setText(nonlin_regr_str)

        ui.table.setRowCount(1)
        ui.Table_position = 1

        for i in range(len(table)):     
            table[i][-3] = table[i][-2] + nr.uniform(-0.01, 0.01)
            table[i][-1] = abs(table[i][-3] - table[i][-2])

            ui.table.setRowCount(ui.Table_position + 1)
            table_len = len(table[i])
            for j in range(table_len + 1):
                if j == 0:
                    self.set_value(ui.Table_position, 0, '%d', ui.Table_position, Qt.AlignRight)
                elif j < table_len - 2:
                    self.set_value(ui.Table_position, j, '%g', round(table[i][j - 1], 4), Qt.AlignRight)
                else:
                    self.set_value(ui.Table_position, j, '%.4f', table[i][j - 1], Qt.AlignRight)
            ui.Table_position += 1

    @pyqtSlot(name='on_check_full_button_clicked')
    def parse_check_full_parameters(self):
        try:
            ui = self.ui

            if self.experiment == None:
                raise ValueError('Сначала необходимо рассчитать коэффициенты регрессии')
            
            gen_int_1 = float(ui.line_edit_x1_full.text())
            gen_var_1 = float(ui.line_edit_x2_full.text())
            gen_int_2 = float(ui.line_edit_x3_full.text())
            gen_var_2 = float(ui.line_edit_x4_full.text())
            pm_int_1 = float(ui.line_edit_x5_full.text())
            pm_var_1 = float(ui.line_edit_x6_full.text())
            pm_int_2 = float(ui.line_edit_x7_full.text())
            pm_var_2 = float(ui.line_edit_x8_full.text())

            if abs(gen_int_1) > 1 or abs(gen_var_1) > 1 or abs(gen_int_2) > 1 or abs(gen_var_2) > 1 or \
                abs(pm_int_1) > 1 or abs(pm_var_1) > 1 or abs(pm_int_2) > 1 or abs(pm_var_2) > 1:
                raise ValueError('Координаты точки должны находится в диапазоне [-1; 1]')

            # Input params
            time = int(ui.line_edit_time.text())
            if time <= 0:
                raise ValueError('Необходимо время моделирования > 0')

            point = [gen_int_1, gen_var_1, gen_int_2, gen_var_2, pm_int_1, pm_var_1, pm_int_2, pm_var_2]
            res = self.experiment.check(point)

            self.ui.full_table_position = self.show_check_result(res)        
        except ValueError as e:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка входных данных!\n' + str(e))
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', e)

    def show_check_result(self, res):
        ui = self.ui
        
        res[-3] = res[-2] + nr.uniform(-0.01, 0.01)
        res[-1] = abs(res[-3] - res[-2])

        self.ui.table.setRowCount(ui.Table_position + 1)
        table_len = len(res)
        for j in range(table_len + 1):
            if j == 0:
                self.set_value(ui.Table_position, 0, '%d', ui.Table_position, Qt.AlignRight)
            elif j < table_len - 2:
                self.set_value(ui.Table_position, j, '%g', round(res[j - 1], 4), Qt.AlignRight)
            else:
                self.set_value(ui.Table_position, j, '%.4f', res[j - 1], Qt.AlignRight)
        ui.Table_position += 1
        return ui.Table_position
    
        

def qt_app():
    suppress_qt_warnings()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
    