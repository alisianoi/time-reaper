#!/usr/bin/env python

import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from broker import DataBroker

from timetable import TrTimeTableModel
from timetable import TrTimeTableView

class TrTimerWidget(QWidget):

    def __init__(
            self
            , parent: QObject=None
            , timer_value: QTime=QTime(0, 0, 0, 0)
            , timer_sleep: int=1000
            , timer_format: str='hh:mm:ss'
    ):

        super().__init__(parent)

        self.timer = QTimer(self)
        self.timer_value = timer_value
        self.timer_sleep = timer_sleep
        self.timer_format = timer_format

        self.timer_lcd = QLCDNumber(self)
        self.timer_lcd.setDigitCount(len(timer_format))
        self.timer_lcd.display(timer_value.toString(timer_format))

        self.layout = QHBoxLayout(self)

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.timer_lcd)

        self.setLayout(self.layout)

        self.implement_ai()

    def implement_ai(self):
        self.timer.timeout.connect(self.update_timer)

    @pyqtSlot()
    def update_timer(self):
        self.timer_value = self.timer_value.addSecs(1)

        self.timer_lcd.display(
            self.timer_value.toString(self.timer_format)
        )

    @pyqtSlot()
    def start_timer(self):
        self.timer.setInterval(self.timer_sleep)

        self.timer.start()

    @pyqtSlot()
    def stop_timer(self):
        self.timer.stop()

        self.timer_value = QTime(0, 0, 0, 0)

        self.timer_lcd.display(
            self.timer_value.toString(self.timer_format)
        )


class TrMainControlsWidget(QWidget):

    started = pyqtSignal()
    stopped = pyqtSignal()

    def __init__(self, parent: QObject=None):

        super().__init__(parent)

        self.ticking = False

        self.task_ldt = QLineEdit(self)
        self.timer_wdgt = TrTimerWidget(self)
        self.push_btn = QPushButton(self)

        self.layout = QHBoxLayout(self)

        self.layout.addWidget(self.task_ldt, 85)
        self.layout.addWidget(self.timer_wdgt, 10)
        self.layout.addWidget(self.push_btn, 5)

        self.setLayout(self.layout)

        self.translate_ui()
        self.implement_ai()

    def translate_ui(self):
        self.task_ldt.setPlaceholderText('Type task/project')
        self.push_btn.setText('Start')

    def implement_ai(self):
        self.push_btn.clicked.connect(self.toggle_timer)

    @pyqtSlot()
    def toggle_timer(self):
        self.push_btn.setDisabled(True)

        if self.ticking:
            self.stop_timer()
        else:
            self.start_timer()

        self.push_btn.setDisabled(False)

    def start_timer(self):
        if self.ticking:
            return

        self.timer_wdgt.start_timer()
        self.push_btn.setText('Stop')
        self.ticking = True

        self.started.emit()

    def stop_timer(self):
        if not self.ticking:
            return

        self.timer_wdgt.stop_timer()
        self.push_btn.setText('Start')
        self.ticking = False

        self.stopped.emit()


class TrCentralWidget(QWidget):

    def __init__(self, parent: QObject=None):

        super().__init__(parent)

        self.main_controls = TrMainControlsWidget(self)
        self.time_table_view = TrTimeTableView(self)
        self.time_table_model = TrTimeTableModel()

        self.time_table_view.setModel(self.time_table_model)

        self.layout = QVBoxLayout(self)

        self.layout.addWidget(self.main_controls)
        self.layout.addWidget(self.time_table_view)

        self.setLayout(self.layout)


class TrMainWindow(QMainWindow):

    def __init__(self, parent: QObject=None):

        super().__init__(parent)

        self.central_widget = TrCentralWidget(self)

        self.setCentralWidget(self.central_widget)

        self.broker = DataBroker(self)

        self.broker.load_slots(
            lambda: print('started'), lambda: print('stopped')
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = TrMainWindow()
    main_window.show()

    sys.exit(app.exec())
