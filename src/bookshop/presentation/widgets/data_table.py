"""A reusable, sortable, searchable table bound to a list of objects/DTOs."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    QSortFilterProxyModel,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLineEdit,
    QTableView,
    QVBoxLayout,
    QWidget,
)

_Index = QModelIndex | QPersistentModelIndex
_SORT_ROLE = Qt.ItemDataRole.UserRole + 1
_OBJECT_ROLE = Qt.ItemDataRole.UserRole + 2
_DEFAULT_ALIGN = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter


@dataclass(frozen=True)
class Column:
    """Describes one table column over a row object."""

    header: str
    getter: Callable[[Any], Any]
    align: Qt.AlignmentFlag = _DEFAULT_ALIGN
    sort_key: Callable[[Any], Any] | None = None
    stretch: bool = False


class GenericTableModel(QAbstractTableModel):
    def __init__(self, columns: Sequence[Column], rows: Sequence[Any] | None = None) -> None:
        super().__init__()
        self._columns = list(columns)
        self._rows: list[Any] = list(rows or [])

    def set_rows(self, rows: Sequence[Any]) -> None:
        self.beginResetModel()
        self._rows = list(rows)
        self.endResetModel()

    def row_object(self, row: int) -> Any:
        return self._rows[row]

    def rowCount(self, parent: _Index = QModelIndex()) -> int:  # noqa: N802, B008
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: _Index = QModelIndex()) -> int:  # noqa: N802, B008
        return 0 if parent.isValid() else len(self._columns)

    def data(self, index: _Index, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        column = self._columns[index.column()]
        obj = self._rows[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            value = column.getter(obj)
            return "" if value is None else str(value)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(column.align)
        if role == _SORT_ROLE:
            key = column.sort_key or column.getter
            return key(obj)
        if role == _OBJECT_ROLE:
            return obj
        return None

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole
    ) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._columns[section].header
        return None


class DataTable(QWidget):
    """Search box + sortable table. Emits row objects, not indexes."""

    rowActivated = Signal(object)
    selectionChanged = Signal(object)

    def __init__(
        self,
        columns: Sequence[Column],
        parent: QWidget | None = None,
        *,
        searchable: bool = True,
        search_placeholder: str = "Search…",
    ) -> None:
        super().__init__(parent)
        self._columns = list(columns)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.search = QLineEdit()
        self.search.setPlaceholderText(search_placeholder)
        self.search.setClearButtonEnabled(True)
        self.search.setAccessibleName("Search table")
        self.search.setVisible(searchable)

        self._model = GenericTableModel(self._columns)
        self._proxy = QSortFilterProxyModel(self)
        self._proxy.setSourceModel(self._model)
        self._proxy.setSortRole(_SORT_ROLE)
        self._proxy.setFilterKeyColumn(-1)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search.textChanged.connect(self._proxy.setFilterFixedString)

        self.view = QTableView()
        self.view.setModel(self._proxy)
        self.view.setSortingEnabled(True)
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.view.setShowGrid(False)
        self.view.verticalHeader().setVisible(False)
        self.view.setAccessibleName("Data table")
        self.view.setTabKeyNavigation(True)

        header = self.view.horizontalHeader()
        header.setHighlightSections(False)
        for col_index, column in enumerate(self._columns):
            mode = (
                QHeaderView.ResizeMode.Stretch
                if column.stretch
                else QHeaderView.ResizeMode.ResizeToContents
            )
            header.setSectionResizeMode(col_index, mode)
        if not any(c.stretch for c in self._columns):
            header.setStretchLastSection(True)

        self.view.doubleClicked.connect(self._on_activated)
        sel = self.view.selectionModel()
        if sel is not None:
            sel.currentRowChanged.connect(self._on_current_changed)

        layout.addWidget(self.search)
        layout.addWidget(self.view, 1)

    def set_rows(self, rows: Sequence[Any]) -> None:
        self._model.set_rows(rows)
        # Re-bind selection model (reset model invalidates the previous one).
        sel = self.view.selectionModel()
        if sel is not None:
            sel.currentRowChanged.connect(self._on_current_changed)

    def current_object(self) -> Any | None:
        index = self.view.currentIndex()
        if not index.isValid():
            return None
        return self._proxy.data(index, _OBJECT_ROLE)

    def _on_activated(self, proxy_index: QModelIndex) -> None:
        obj = self._proxy.data(proxy_index, _OBJECT_ROLE)
        if obj is not None:
            self.rowActivated.emit(obj)

    def _on_current_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        obj = self._proxy.data(current, _OBJECT_ROLE) if current.isValid() else None
        self.selectionChanged.emit(obj)
