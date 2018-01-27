import logging

from pathlib import Path
from PyQt5.QtCore import QObject


class Stylist(QObject):
    '''
    Loads and stores files that contain Qt Style Sheets

    Note:
        See DataBroker as somewhat similar class
    '''

    def __init__(self, path: Path=None, parent: QObject=None):

        super().__init__(parent)

        self.logger = logging.getLogger('tslot')
        self.logger.debug('Stylist logging works')

        self.styles = {}

        if path is None:
            path = Path(Path.cwd(), Path('css'), Path('tslot.css'))

        if not path.exists():
            self.logger.debug('Could not find {} in {}'.format(path.name(), path))

            return

        with open(path) as src:
            self.styles[path] = src.read()