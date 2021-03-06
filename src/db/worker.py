import logging
from pathlib import Path

from PyQt5.QtCore import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.common.failure import TFailure
from src.common.logger import logged
from src.common.request.fetch import TFetchRequest
from src.common.request.stash import TStashRequest
from src.common.response.fetch import TFetchResponse
from src.common.response.stash import TStashResponse


class TWorker(QObject):
    """
    Provide the base class for all workers (readers and writers)

    Open a brand new database session every time because the SQLAlchemy session
    object should be opened and used in the same thread.
    """

    started = pyqtSignal()
    stopped = pyqtSignal()
    alerted = pyqtSignal(TFailure)

    def __init__(self, path: Path = None, parent: QObject = None) -> None:
        """
        Initialize a database worker

        Args:
            path  : path to the SQLite database file
            parent: parent object if Qt ownership is required
        """

        super().__init__(parent)

        self.logger = logging.getLogger("tslot-data")

        self.path = path
        self.query = None

        self.session = None

    @logged(logger=logging.getLogger("tslot-data"), disabled=True)
    def work(self) -> None:
        """
        Provide the default work method which subclasses should overwrite

        Some signal (either a common one like started/stopped or a
        worker-specific one) should be emitted when the work is done.
        """

        return self.alerted.emit(
            TFailure("Failed to load anything: default work method")
        )

    @logged(logger=logging.getLogger("tslot-data"), disabled=True)
    def create_session(self):
        """Open a brand new SQLite/SQLAlchemy database session"""

        if not isinstance(self.path, Path) or not self.path.exists():
            return self.alerted.emit(TFailure(f"Path to database is gone {self.path}"))

        self.logger.debug(f"Will create db session to {self.path}")

        engine = create_engine(f"sqlite:///{self.path}")
        SessionMaker = sessionmaker(bind=engine)

        return SessionMaker()


class TReader(TWorker):
    """Provide base class for all different database readers"""

    fetched = pyqtSignal(TFetchResponse)

    def __init__(
            self, request: TFetchRequest, path: Path = None, parent: QObject = None
    ) -> None:
        """
        Initialize a database reader

        Args:
            request: a fetch request for some data from the database
            path   : the path to the database
            parent : parent object if Qt ownership is required
        """

        super().__init__(path, parent)

        self.request = request


class TWriter(TWorker):
    """Provides the base class for all different database writers"""

    stashed = pyqtSignal(TStashResponse)

    def __init__(
            self, request: TStashRequest, path: Path = None, parent: QObject = None
    ):
        super().__init__(path, parent)

        self.request = request
