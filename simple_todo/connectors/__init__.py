from .connector_base import Connector
from .connector_sqlite import SqliteConnector

connectors = {
    "sqlite": SqliteConnector
}
