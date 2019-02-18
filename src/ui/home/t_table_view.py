import logging

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.client.common.widget.table_view import TTableView
from src.ui.home.t_table_header_view import THeaderView
from src.utils import style_option_as_str
from src.common.logger import logged, logmain


class THomeTableStyleDelegate(QStyledItemDelegate):
    """Draw a push button instead of a table cell."""

    def __init__(self, parent: QWidget=None) -> None:

        super().__init__(parent)

    @logged(logger=logging.getLogger("tslot-main"), disabled=True)
    def createEditor(
        self
        , parent: QWidget
        , option: QStyleOptionViewItem
        , index: QModelIndex
    ) -> QWidget:

        if index.column() not in [0, 1, 2, 3]:
            raise RuntimeError(f'Editor for column {index.column()}')

        # alternative: return QLineEdit(parent)
        return super().createEditor(parent, option, index)

    @logged(disabled=False)
    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:

        editor.setText(index.data())

    @logged(disabled=False)
    def setModelData(
        self
        , editor: QWidget
        , model: QAbstractItemModel
        , index: QModelIndex
    ) -> None:

        if not isinstance(editor, QLineEdit):
            raise RuntimeError('Expected editor to be QLineEdit')

        model.setData(index, editor.text())

    @logged(disabled=True)
    def paint(
        self
        , painter: QPainter
        , option : QStyleOptionViewItem
        , index  : QModelIndex
    ) -> None:

        logmain.debug(f'paint: {index}')

        if index.column() != 5:
            return super().paint(painter, option, index)

        painter.save()

        so_button = QStyleOptionButton()
        so_button.rect = QRect(option.rect)
        so_button.text = 'trash'
        so_button.state = QStyle.State_Enabled

        QApplication.style().drawControl(QStyle.CE_PushButton, so_button, painter)

        painter.restore()

    @logged(logger=logging.getLogger('tslot-main'), disabled=True)
    def sizeHint(self, item: QStyleOptionViewItem, index: QModelIndex) -> QSize:

        size = super().sizeHint(item, index)

        logmain.debug(style_option_as_str(item.type))
        logmain.debug(f'row: {item.index.row()}, col: {item.index.column()}')
        logmain.debug(f'{index.data()}')
        logmain.debug(item.text)

        if index in [2, 3, 4]:
            return size

        # TODO: +20 is the spacing between columns 2, 3 and 4
        return QSize(size.width() + 20, size.height())


class THomeTableView(TTableView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.delegate = THomeTableStyleDelegate()
        self.setItemDelegate(self.delegate)

        self.verticalHeader().hide()
        self.horizontalHeader().hide()

        # Horizontal size can grow/shrink as parent widget sees fit
        # Vertical size must be at least the size of vertical size hint
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        # Since we're demanding that all vertical size be allocated to
        # the table view, let's disable the vertical scrollbar
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

    @logged(logger=logging.getLogger('tslot-main'), disabled=True)
    def sizeHint(self):
        """Compute the exact required size for the table"""

        size_hint = super().sizeHint()

        h, w = 0, size_hint.width()

        vheader = self.verticalHeader()
        hheader = self.horizontalHeader()

        if not vheader.isHidden():
            logmain.warning('Expecting vertical header to be hidden')
        if not hheader.isHidden():
            h += hheader.height()

        for i in range(vheader.count()):
            if not vheader.isSectionHidden(i):
                h += vheader.sectionSize(i)

        return QSize(w, h)

    @logged(logger=logging.getLogger('tslot-main'), disabled=True)
    def minimumSizeHint(self):
        return self.sizeHint()

    @logged(logger=logging.getLogger('tslot-main'), disabled=True)
    def setModel(self, model: QAbstractItemModel):

        super().setModel(model)

        # The code below is the reason why this method is overwritten
        # It creates a brand new header view, installs and triggers it
        self.header_view = THeaderView(Qt.Horizontal, self)

        self.setHorizontalHeader(self.header_view)

    @logged(logger=logging.getLogger('tslot-main'), disabled=True)
    def enterEvent(self, event: QEvent) -> None:

        super().enterEvent(event)

    @logged(logger=logging.getLogger('tslot-main'), disabled=True)
    def leaveEvent(self, event: QEvent) -> None:

        super().leaveEvent(event)
