# SPDX-FileCopyrightText: qutebrowser-panes fork
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tab wrapping one or more Panes (AbstractTab) in a QSplitter."""

from typing import TYPE_CHECKING, Any, Optional

from qutebrowser.qt.core import pyqtSignal, QUrl, QSizeF, Qt, QEvent, QObject
from qutebrowser.qt.gui import QIcon
from qutebrowser.qt.widgets import QWidget, QSplitter, QVBoxLayout, QApplication

from qutebrowser.utils import usertypes

if TYPE_CHECKING:
    from qutebrowser.browser import browsertab


_FORWARDED_SIGNALS = (
    'window_close_requested',
    'link_hovered',
    'load_started',
    'load_progress',
    'load_finished',
    'icon_changed',
    'title_changed',
    'pinned_changed',
    'new_tab_requested',
    'url_changed',
    'contents_size_changed',
    'fullscreen_requested',
    'before_load_started',
    'load_status_changed',
    'shutting_down',
    'history_item_triggered',
    'renderer_process_terminated',
)


class Tab(QWidget):

    window_close_requested = pyqtSignal()
    link_hovered = pyqtSignal(str)
    load_started = pyqtSignal()
    load_progress = pyqtSignal(int)
    load_finished = pyqtSignal(bool)
    icon_changed = pyqtSignal(QIcon)
    title_changed = pyqtSignal(str)
    pinned_changed = pyqtSignal(bool)
    new_tab_requested = pyqtSignal(QUrl)
    url_changed = pyqtSignal(QUrl)
    contents_size_changed = pyqtSignal(QSizeF)
    fullscreen_requested = pyqtSignal(bool)
    before_load_started = pyqtSignal(QUrl)
    load_status_changed = pyqtSignal(usertypes.LoadStatus)
    shutting_down = pyqtSignal()
    history_item_triggered = pyqtSignal(QUrl, QUrl, str)
    renderer_process_terminated = pyqtSignal(object, int)

    def __init__(self, pane: 'browsertab.AbstractTab',
                 parent: QWidget = None) -> None:
        super().__init__(parent)
        self._win_id = pane.win_id
        self._panes: list['browsertab.AbstractTab'] = []
        self.active_pane: 'browsertab.AbstractTab' = pane

        self._splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self._splitter.setChildrenCollapsible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._splitter)

        self._attach_pane(pane, make_active=True)

        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    def _attach_pane(self, pane: 'browsertab.AbstractTab',
                     make_active: bool) -> None:
        self._panes.append(pane)
        self._splitter.addWidget(pane)
        pane.show()
        if make_active:
            self._forward_signals(pane)

    def _forward_signals(self, pane: 'browsertab.AbstractTab') -> None:
        for name in _FORWARDED_SIGNALS:
            getattr(pane, name).connect(getattr(self, name))

    def _unforward_signals(self, pane: 'browsertab.AbstractTab') -> None:
        for name in _FORWARDED_SIGNALS:
            try:
                getattr(pane, name).disconnect(getattr(self, name))
            except (TypeError, RuntimeError):
                pass

    def _set_active_pane(self, pane: 'browsertab.AbstractTab') -> None:
        if pane is self.active_pane or pane not in self._panes:
            return
        self._unforward_signals(self.active_pane)
        self.active_pane = pane
        self._forward_signals(pane)
        self.url_changed.emit(pane.url())
        self.title_changed.emit(pane.title())
        self.icon_changed.emit(pane.icon())

    def split(self, orientation: Qt.Orientation,
              url: QUrl = None) -> 'browsertab.AbstractTab':
        """Add a new pane as a sibling in the splitter."""
        from qutebrowser.browser import browsertab
        self._splitter.setOrientation(orientation)
        new_pane = browsertab.create(
            win_id=self._win_id,
            private=self.active_pane.is_private,
            parent=self._splitter,
        )
        self._attach_pane(new_pane, make_active=False)
        if url is not None:
            new_pane.load_url(url)
        self._equalize_sizes()
        self._set_active_pane(new_pane)
        new_pane.setFocus()
        return new_pane

    def close_active_pane(self) -> bool:
        """Close the active pane. False if it was the last pane in the tab."""
        if len(self._panes) <= 1:
            return False
        victim = self.active_pane
        idx = self._splitter.indexOf(victim)
        if idx + 1 < self._splitter.count():
            successor_idx = idx + 1
        else:
            successor_idx = idx - 1
        successor = self._splitter.widget(successor_idx)

        self._unforward_signals(victim)
        self._panes.remove(victim)
        victim.pending_removal = True
        try:
            victim.private_api.shutdown()
        except Exception:
            pass
        victim.setParent(None)
        victim.deleteLater()

        self.active_pane = successor
        self._forward_signals(successor)
        self.url_changed.emit(successor.url())
        self.title_changed.emit(successor.title())
        self.icon_changed.emit(successor.icon())
        successor.setFocus()
        self._equalize_sizes()
        return True

    def _equalize_sizes(self) -> None:
        # QSplitter.addWidget leaves new children at 0 size until setSizes().
        count = self._splitter.count()
        if count == 0:
            return
        if self._splitter.orientation() == Qt.Orientation.Horizontal:
            total = max(self._splitter.width(), 1)
        else:
            total = max(self._splitter.height(), 1)
        share = total // count
        self._splitter.setSizes([share] * count)

    def focus_direction(self, direction: str) -> bool:
        """direction: 'left' | 'right' | 'up' | 'down'."""
        is_horizontal = self._splitter.orientation() == Qt.Orientation.Horizontal
        if direction in ('left', 'right') and not is_horizontal:
            return False
        if direction in ('up', 'down') and is_horizontal:
            return False
        idx = self._splitter.indexOf(self.active_pane)
        if idx < 0:
            return False
        delta = -1 if direction in ('left', 'up') else 1
        new_idx = idx + delta
        if new_idx < 0 or new_idx >= self._splitter.count():
            return False
        target = self._splitter.widget(new_idx)
        if target is None:
            return False
        target.setFocus()
        return True

    def eventFilter(self, _obj: QObject, event: QEvent) -> bool:  # noqa: N802
        # Global mouse-press filter. QWebEngineView focuses through a
        # QWindow-backed render widget that's not in the QObject tree we see,
        # so focusChanged / parent() walks don't tell us which pane got
        # clicked. Screen geometry does.
        if event.type() == QEvent.Type.MouseButtonPress:
            gpos = getattr(event, 'globalPosition', None)
            if gpos is None:
                return False
            pane = self._pane_at_global_pos(gpos().toPoint())
            if pane is not None and pane is not self.active_pane:
                self._set_active_pane(pane)
        return False

    def _pane_at_global_pos(self, point
                            ) -> Optional['browsertab.AbstractTab']:
        for pane in self._panes:
            if not pane.isVisible():
                continue
            top_left = pane.mapToGlobal(pane.rect().topLeft())
            bottom_right = pane.mapToGlobal(pane.rect().bottomRight())
            if (top_left.x() <= point.x() < bottom_right.x() and
                    top_left.y() <= point.y() < bottom_right.y()):
                return pane
        return None

    def __getattr__(self, name: str) -> Any:
        try:
            active = self.__dict__['active_pane']
        except KeyError:
            raise AttributeError(name) from None
        return getattr(active, name)
