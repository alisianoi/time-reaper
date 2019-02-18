import logging
from pathlib import Path

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QWidget

import pendulum
from src.ai.model import TEntryModel, TSlotModel
from src.common.dto.base import TResponse
from src.common.dto.timer_fetch_request import TTimerFetchRequest, TTimerFetchResponse
from src.common.dto.timer import TTimerStashRequest
from src.ui.base import TWidget
from src.client.wgt_timer.widget.timer import TTimerWidget
from src.common.logger import logged


class TTimerControlsWidget(TWidget):
    """Add basic controls to start/stop time tracking for a task"""

    def __init__(self, parent: TWidget=None):

        super().__init__(parent)

        path_svgs_solid = Path('font', 'fontawesome', 'svgs', 'solid')

        self.play_icon = QIcon(str(Path(path_svgs_solid, 'play.svg')))
        self.stop_icon = QIcon(str(Path(path_svgs_solid, 'stop.svg')))
        self.nuke_icon = QIcon(str(Path(path_svgs_solid, 'trash-alt.svg')))

        self.task_ldt = QLineEdit()
        self.timer_wgt = TTimerWidget()
        self.push_btn = QPushButton()
        self.nuke_btn = QPushButton()

        self.push_btn.setObjectName('t_timer_controls_push_btn')
        self.nuke_btn.setObjectName('t_timer_controls_nuke_btn')
        self.push_btn.setIcon(self.play_icon)
        self.nuke_btn.setIcon(self.nuke_icon)

        self.nuke_btn.hide()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(10, 0, 10, 0)

        self.layout.addWidget(self.task_ldt)
        self.layout.addWidget(self.nuke_btn)
        self.layout.addWidget(self.push_btn)
        self.layout.addWidget(self.timer_wgt)

        self.setLayout(self.layout)

        self.task_ldt.setPlaceholderText('Type task/project')

        self.push_btn.clicked.connect(self.toggle_timer)

    @logged(logger=logging.getLogger('tslot-main'), disabled=True)
    def kickstart(self):
        self.requested.emit(TTimerFetchRequest())

    @pyqtSlot()
    def toggle_timer(self):
        self.push_btn.setDisabled(True)

        if not self.timer_wgt.isActive():
            self.start_timer()
        else:
            self.stop_timer()

        self.push_btn.setDisabled(False)

    @logged(logger=logging.getLogger("tslot-main"), disabled=True)
    def start_timer(self, item: TEntryModel=None, sleep: int=1000) -> None:
        """
        Start the timer

        Make sure that there is no other timer already running. When creating a
        brand new timer, make sure to save it to the database.
        """

        if self.timer_wgt.isActive():
            raise RuntimeError("Cannot start two timers at once")

        if item is None:
            value = self.start_new_timer()
        else:
            value = self.start_old_timer(item)

        self.timer_wgt.start_timer(value, sleep)

        self.push_btn.setIcon(self.stop_icon)
        self.nuke_btn.show()

    def start_new_timer(self) -> int:
        """Create a new timer, let the database know and return 0 seconds."""

        self.item = TEntryModel(slot=TSlotModel(fst=pendulum.now(tz='UTC')))

        self.requested.emit(TTimerStashRequest(self.item))

        return 0 # zero seconds of running new timer

    def start_old_timer(self, item: TEntryModel) -> int:
        """Launch an old timer, return its duration in seconds."""

        self.item = item

        self.logger.debug(f"Set task_ldt text: {item.task.name}")
        self.task_ldt.setText(self.item.task.name)

        period = pendulum.now(tz='UTC') - item.slot.fst

        # NOTE: .in_seconds() truncates microseconds
        return period.in_seconds()

    @logged(logger=logging.getLogger("tslot-main"), disabled=True)
    def stop_timer(self):
        """Stop the currently running timer and let the database know."""

        if not self.timer_wgt.isActive():
            raise RuntimeError('Cannot stop a stopped timer')

        # NOTE: ignore the actual value
        self.timer_wgt.stop_timer()

        self.item.slot.lst = pendulum.now(tz='UTC')
        self.item.task.name = self.task_ldt.text()

        self.requested.emit(TTimerStashRequest(self.item))

        self.task_ldt.clear()
        self.push_btn.setIcon(self.play_icon)
        self.nuke_btn.hide()

    @pyqtSlot(TResponse)
    def handle_responded(self, response: TResponse) -> None:

        if isinstance(response, TTimerFetchResponse):
            self.handle_timer_fetch_response(response)

    def handle_timer_fetch_response(self, response: TTimerFetchResponse):

        if response.timer is None:
            return # database stores no active timer, nothing to do

        if self.timer_wgt.isActive():
            raise RuntimeError('Two active timers: one from DB, one from GUI')

        self.task_ldt.setText(response.timer.task.name)

        self.push_btn.setDisabled(True)

        self.start_timer(response.timer)

        self.push_btn.setDisabled(False)