import logging

from datetime import datetime
from operator import itemgetter

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.model import Tag, Task, Slot
from src.utils import orient2str, role2str, logged


class TTableModel(QAbstractTableModel):

    def __init__(self, parent: QObject=None):

        super().__init__(parent)

        self.logger = logging.getLogger('tslot')
        self.logger.debug(self.__class__.__name__ + ' has a logger')

        self.entries = []

    @logged
    def headerData(
        self
        , section    : int
        , orientation: Qt.Orientation
        , role       : Qt.ItemDataRole=Qt.DisplayRole
    ):
        if orientation == Qt.Vertical:
            return super().headerData(section, orientation, role)
        if role == Qt.DisplayRole:
            return self.headerDataDisplayRole(section)

        return super().headerData(section, orientation, role)

    @logged
    def headerDataDisplayRole(self, section: int):
        if section == 0:
            return 'Task'
        elif section == 1:
            return 'Tag'
        elif section == 2:
            return 'Started'
        elif section == 3:
            return 'Stopped'
        elif section == 4:
            return 'Elapsed'

        return 'Fix Header'

    def rowCount(self, parent: QModelIndex=QModelIndex()):
        return len(self.entries)

    def columnCount(self, parent: QModelIndex=QModelIndex()):
        return 5

    @logged
    def data(
        self
        , index: QModelIndex=QModelIndex()
        , role : Qt.ItemDataRole=Qt.DisplayRole
    ):
        if not index.isValid():
            self.logger.debug('Requested index is not valid')
            return QVariant()

        if not 0 <= index.row() < self.rowCount():
            self.logger.debug('Requested row is outside range')
            return QVariant()

        if not 0 <= index.column() <= self.columnCount():
            self.logger.debug('Requested column is outside range')
            return QVariant()

        if role == Qt.DisplayRole:
            return self.dataDisplayRole(index)
        if role == Qt.TextAlignmentRole:
            return self.dataTextAlignmentRole(index)

        self.logger.debug('Defaulting to QVariant')
        return QVariant()

    def dataDisplayRole(self, index: QModelIndex=QModelIndex()):

        row, column = index.row(), index.column()

        tag, task, slot = self.entries[row]

        if column == 0:
            return task.name

        if column == 1:
            return tag.name

        if column == 2:
            return str(slot.fst)

        if column == 3:
            return str(slot.lst)

        if column == 4:
            return str(slot.lst - slot.fst)

        self.logger.debug('Defaulting to QVariant')
        return QVariant()

    def dataTextAlignmentRole(self, index: QModelIndex=QModelIndex()):

        if index.column() == 4:
            return Qt.AlignVCenter | Qt.AlignRight

        self.logger.debug('Defaulting to QVariant')
        return QVariant()

    @logged
    def find_lft_index(self, entry, key=itemgetter(2)):
        '''
        Find the *very first* entry which is >= the given entry.

        This gives the leftmost index at which it would be possible to
        insert the given entry and maintain the list in sorted order.

        Args:
            entry: the potentially new entry
            key  : the standard key function, see [1]

        Returns:
            An index from [0, len(self.entries)] suitable for insertion

        [1] https://docs.python.org/3/howto/sorting.html#key-functions
        '''

        slot0 = key(entry)
        lo, hi = 0, len(self.entries) - 1

        while lo <= hi:
            mid = lo + (hi - lo) // 2

            slot1 = key(self.entries[mid])

            if slot0 <= slot1:
                hi = mid - 1
            else:
                lo = mid + 1

        return lo


class THeaderView(QHeaderView):
    '''
    Control size/resize of headers for the SlotTableView

    Note:
        https://stackoverflow.com/q/48361795/1269892
    '''

    def __init__(
            self
            , orientation: Qt.Orientation=Qt.Horizontal
            , parent     : QWidget=None
    ):
        super().__init__(orientation, parent)

        self.logger = logging.getLogger('tslot')
        self.logger.debug('TSlotHorizontalHeaderView has a logger')

        Stretch, Fixed = QHeaderView.Stretch, QHeaderView.Fixed

        self.section_resize_modes = [
            Stretch, Stretch, Fixed, Fixed, Fixed
        ]

    @logged
    def setModel(self, model: QAbstractItemModel=None):
        '''
        Set the underlying data model

        Fine-grained resizing of individual sections requires calling
        setSectionResizeMode which works only when you've set the model.
        '''
        if model is None:
            raise RuntimeError('model must be not None')

        super().setModel(model)

        if model.columnCount() != self.count():
            raise RuntimeError('model.columnCount() != self.count()')

        # The loop below is the only reason why this method exists
        for i, mode in enumerate(self.section_resize_modes):
            self.setSectionResizeMode(i, mode)


class TTableView(QTableView):

    def __init__(self, parent: QObject=None):

        super().__init__(parent)

        self.verticalHeader().hide()

        # Horizontal size can grow/shrink as parent widget sees fit
        # Vertical size must be at least the size of vertical size hint
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        # Since we're demanding that all vertical size be allocated to
        # the table view, let's disable the vertical scrollbar
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setFont(QFont('Quicksand-Medium', 12))

        self.setShowGrid(False)

    def sizeHint(self):

        model = self.model()

        if model is None:
            return super().sizeHint()

        height = self.horizontalHeader().height()
        for i in range(model.rowCount()):
            height += self.rowHeight(i)

        return QSize(super().sizeHint().width(), height)

    def setModel(self, model: QAbstractItemModel):

        super().setModel(model)

        # The code below is the reason why this method is overwritten
        # It creates a brand new header view, installs and triggers it
        self.header_view = THeaderView(
            orientation=Qt.Horizontal, parent=self
        )

        self.setHorizontalHeader(self.header_view)

        self.header_view.setModel(model)
