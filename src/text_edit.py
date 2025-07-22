import os
import re

from src import actions
from src import app
from src import find_replace_windows
from src import menus
from src import messages
from src import settings
from src import utils
from src.qt import *


class TextEdit(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.text_edits = main_window.text_edits
        self.text_edits.add(self)
        self.text_edit = _TextEdit(main_window)
        self.text_edit.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
        )
        self.text_edit.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
        )
        self.scrollbar_signaler = ScrollbarSignaler(
            Qt.Orientation.Vertical,
            self,
        )
        self.scrollbar_signaler.valueChanged.connect(self.on_view_changed)
        self.scrollbar_signalers = main_window.scrollbar_signalers
        self.scrollbar_signalers.add(self.scrollbar_signaler)
        self.text_edit.setVerticalScrollBar(self.scrollbar_signaler)
        self.scrollbar = Scrollbar(self, self.scrollbar_signaler)
        self.text_edit.scrollbar = self.scrollbar
        self.scrollbar_signaler_h = ScrollbarSignaler(
            Qt.Orientation.Horizontal,
            self,
        )
        self.text_edit.setHorizontalScrollBar(self.scrollbar_signaler_h)
        self.scrollbar_h = ScrollbarH(self, self.scrollbar_signaler_h)
        self.text_edit.scrollbar_h = self.scrollbar_h
        self.scrollbar_signaler_h.linked_scrollbars = {
            self.scrollbar_signaler_h
        }
        self.scrollbar_signaler_h.valueChanged.connect(self.on_view_changed)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.text_edit)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.scrollbar.raise_()
        self.scrollbar_h.raise_()
        self.font_size = settings.text_editor_font_size
        self.pre_on_update_state = None
        self.wheel_control_fn = lambda x: None
        self.wheel_shift_fn = lambda x: None
        self.on_update_settings()
        self.text_edit.clear_undo_stack()

        text = (
            """[1] Gallia est omnis divisa in partes tres, quarum unam incolunt Belgae, aliam Aquitani, tertiam qui ipsorum lingua Celtae, nostra Galli appellantur. Hi omnes lingua, institutis, legibus inter se differunt. Gallos ab Aquitanis Garumna flumen, a Belgis Matrona et Sequana dividit. Horum omnium fortissimi sunt Belgae, propterea quod a cultu atque humanitate provinciae longissime absunt, minimeque ad eos mercatores saepe commeant atque ea quae ad effeminandos animos pertinent important, proximique sunt Germanis, qui trans Rhenum incolunt, quibuscum continenter bellum gerunt. Qua de causa Helvetii quoque reliquos Gallos virtute praecedunt, quod fere cotidianis proeliis cum Germanis contendunt, cum aut suis finibus eos prohibent aut ipsi in eorum finibus bellum gerunt. Eorum una, pars, quam Gallos obtinere dictum est, initium capit a flumine Rhodano, continetur Garumna flumine, Oceano, finibus Belgarum, attingit etiam ab Sequanis et Helvetiis flumen Rhenum, vergit ad septentriones. Belgae ab extremis Galliae finibus oriuntur, pertinent ad inferiorem partem fluminis Rheni, spectant in septentrionem et orientem solem. Aquitania a Garumna flumine ad Pyrenaeos montes et eam partem Oceani quae est ad Hispaniam pertinet; spectat inter occasum solis et septentriones.

    [2] Apud Helvetios longe nobilissimus fuit et ditissimus Orgetorix. Is M. Messala, [et P.] M. Pisone consulibus regni cupiditate inductus coniurationem nobilitatis fecit et civitati persuasit ut de finibus suis cum omnibus copiis exirent: perfacile esse, cum virtute omnibus praestarent, totius Galliae imperio potiri. Id hoc facilius iis persuasit, quod undique loci natura Helvetii continentur: una ex parte flumine Rheno latissimo atque altissimo, qui agrum Helvetium a Germanis dividit; altera ex parte monte Iura altissimo, qui est inter Sequanos et Helvetios; tertia lacu Lemanno et flumine Rhodano, qui provinciam nostram ab Helvetiis dividit. His rebus fiebat ut et minus late vagarentur et minus facile finitimis bellum inferre possent; qua ex parte homines bellandi cupidi magno dolore adficiebantur. Pro multitudine autem hominum et pro gloria belli atque fortitudinis angustos se fines habere arbitrabantur, qui in longitudinem milia passuum CCXL, in latitudinem CLXXX patebant.

    [3] His rebus adducti et auctoritate Orgetorigis permoti constituerunt ea quae ad proficiscendum pertinerent comparare, iumentorum et carrorum quam maximum numerum coemere, sementes quam maximas facere, ut in itinere copia frumenti suppeteret, cum proximis civitatibus pacem et amicitiam confirmare. Ad eas res conficiendas biennium sibi satis esse duxerunt; in tertium annum profectionem lege confirmant. Ad eas res conficiendas Orgetorix deligitur. Is sibi legationem ad civitates suscipit. In eo itinere persuadet Castico, Catamantaloedis filio, Sequano, cuius pater regnum in Sequanis multos annos obtinuerat et a senatu populi Romani amicus appellatus erat, ut regnum in civitate sua occuparet, quod pater ante habuerit; itemque Dumnorigi Haeduo, fratri Diviciaci, qui eo tempore principatum in civitate obtinebat ac maxime plebi acceptus erat, ut idem conaretur persuadet eique filiam suam in matrimonium dat. Perfacile factu esse illis probat conata perficere, propterea quod ipse suae civitatis imperium obtenturus esset: non esse dubium quin totius Galliae plurimum Helvetii possent; se suis copiis suoque exercitu illis regna conciliaturum confirmat. Hac oratione adducti inter se fidem et ius iurandum dant et regno occupato per tres potentissimos ac firmissimos populos totius Galliae sese potiri posse sperant.

    [4] Ea res est Helvetiis per indicium enuntiata. Moribus suis Orgetoricem ex vinculis causam dicere coegerunt; damnatum poenam sequi oportebat, ut igni cremaretur. Die constituta causae dictionis Orgetorix ad iudicium omnem suam familiam, ad hominum milia decem, undique coegit, et omnes clientes obaeratosque suos, quorum magnum numerum habebat, eodem conduxit; per eos ne causam diceret se eripuit. Cum civitas ob eam rem incitata armis ius suum exequi conaretur multitudinemque hominum ex agris magistratus cogerent, Orgetorix mortuus est; neque abest suspicio, ut Helvetii arbitrantur, quin ipse sibi mortem consciverit.

    [5] Post eius mortem nihilo minus Helvetii id quod constituerant facere conantur, ut e finibus suis exeant. Ubi iam se ad eam rem paratos esse arbitrati sunt, oppida sua omnia, numero ad duodecim, vicos ad quadringentos, reliqua privata aedificia incendunt; frumentum omne, praeter quod secum portaturi erant, comburunt, ut domum reditionis spe sublata paratiores ad omnia pericula subeunda essent; trium mensum molita cibaria sibi quemque domo efferre iubent. Persuadent Rauracis et Tulingis et Latobrigis finitimis, uti eodem usi consilio oppidis suis vicisque exustis una cum iis proficiscantur, Boiosque, qui trans Rhenum incoluerant et in agrum Noricum transierant Noreiamque oppugnabant, receptos ad se socios sibi adsciscunt.

    [6] Erant omnino itinera duo, quibus itineribus domo exire possent: unum per Sequanos, angustum et difficile, inter montem Iuram et flumen Rhodanum, vix qua singuli carri ducerentur, mons autem altissimus impendebat, ut facile perpauci prohibere possent; alterum per provinciam nostram, multo facilius atque expeditius, propterea quod inter fines Helvetiorum et Allobrogum, qui nuper pacati erant, Rhodanus fluit isque non nullis locis vado transitur. Extremum oppidum Allobrogum est proximumque Helvetiorum finibus Genava. Ex eo oppido pons ad Helvetios pertinet. Allobrogibus sese vel persuasuros, quod nondum bono animo in populum Romanum viderentur, existimabant vel vi coacturos ut per suos fines eos ire paterentur. Omnibus rebus ad profectionem comparatis diem dicunt, qua die ad ripam Rhodani omnes conveniant. Is dies erat a. d. V. Kal. Apr. L. Pisone, A. Gabinio consulibus.

    [7] Caesari cum id nuntiatum esset, eos per provinciam nostram iter facere conari, maturat ab urbe proficisci et quam maximis potest itineribus in Galliam ulteriorem contendit et ad Genavam pervenit. Provinciae toti quam maximum potest militum numerum imperat (erat omnino in Gallia ulteriore legio una), pontem, qui erat ad Genavam, iubet rescindi. Ubi de eius adventu Helvetii certiores facti sunt, legatos ad eum mittunt nobilissimos civitatis, cuius legationis Nammeius et Verucloetius principem locum obtinebant, qui dicerent sibi esse in animo sine ullo maleficio iter per provinciam facere, propterea quod aliud iter haberent nullum: rogare ut eius voluntate id sibi facere liceat. Caesar, quod memoria tenebat L. Cassium consulem occisum exercitumque eius ab Helvetiis pulsum et sub iugum missum, concedendum non putabat; neque homines inimico animo, data facultate per provinciam itineris faciundi, temperaturos ab iniuria et maleficio existimabat. Tamen, ut spatium intercedere posset dum milites quos imperaverat convenirent, legatis respondit diem se ad deliberandum sumpturum: si quid vellent, ad Id. April. reverterentur.
    """
            * 10
        )
        self.text_edit.insertPlainText(text)  # !!!

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, font_size):
        self._font_size = font_size
        self.on_update_font()

    @staticmethod
    def wheel_event_to_sign_x_y(event):
        delta_x = event.angleDelta().x()
        delta_y = event.angleDelta().y()
        if abs(delta_x) > abs(delta_y):
            delta_y = 0
        else:
            delta_x = 0
        sign_x = utils.sign(delta_x)
        sign_y = utils.sign(delta_y)
        return sign_x, sign_y

    def event(self, event):
        if (
            event.type() == QEvent.Type.NativeGesture
            and event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture
        ):
            sign = utils.sign(event.value())
            self.on_zoom_(sign)
        return super().event(event)

    def resizeEvent(self, event):
        size = event.size()
        width = size.width()
        height = size.height()
        scrollbar_width = self.scrollbar.width()
        self.scrollbar.setGeometry(
            width - scrollbar_width - 2,
            2,
            scrollbar_width,
            height - 4,
        )
        scrollbar_h_height = self.scrollbar_h.height()
        self.scrollbar_h.setGeometry(
            2,
            height - scrollbar_h_height - 2,
            width - 4,
            scrollbar_h_height,
        )

    def wheelEvent(self, event):
        modifiers = app.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            self.zoom_fn(event)
        else:
            self.scroll_fn(
                event,
                modifiers == Qt.KeyboardModifier.ShiftModifier,
            )
        utils.run_after_current_event(self.text_edit.setFocus)

    def scroll_fn(self, event, swap_x_y):
        delta_x = event.angleDelta().x()
        delta_y = event.angleDelta().y()
        if abs(delta_x) > abs(delta_y):
            delta_y = 0
        else:
            delta_x = 0
        if swap_x_y:
            delta_x, delta_y = delta_y, delta_x
        event.accept()
        event = QWheelEvent(
            event.position(),
            event.globalPosition(),
            event.pixelDelta(),
            QPoint(delta_x, delta_y),
            event.buttons(),
            event.modifiers(),
            event.phase(),
            event.inverted(),
        )
        self.text_edit.wheel_event(event)

    def zoom_fn(self, event):
        self.on_zoom_(utils.sign(event.angleDelta().y()))
        self.text_edit.pop_refresh()

    def selection(self):
        return (
            self.text_edit.textCursor().position(),
            self.text_edit.textCursor().selectionStart(),
            self.text_edit.textCursor().selectionEnd(),
        )

    def set_selection(self, selection):
        position, start, end = selection
        text_cursor = self.text_edit.textCursor()
        max_end = len(self.text_edit.toPlainText())
        position = min(position, max_end)
        start = min(start, max_end)
        end = min(end, max_end)
        selection_length = abs(end - start)
        if position == end > 0:
            text_cursor.setPosition(start)
            text_cursor.movePosition(
                QTextCursor.MoveOperation.NextCharacter,
                QTextCursor.MoveMode.KeepAnchor,
                n=selection_length,
            )
        else:
            text_cursor.setPosition(end)
            text_cursor.movePosition(
                QTextCursor.MoveOperation.PreviousCharacter,
                QTextCursor.MoveMode.KeepAnchor,
                n=selection_length,
            )
        self.text_edit.setTextCursor(text_cursor)
        self.text_edit.ensureCursorVisible()

    def scroll_value(self):
        return self.scrollbar_signaler.value()

    def set_scroll_value(self, value):
        utils.run_after_current_event(
            lambda: self.scrollbar_signaler.set_value(value)
        )

    def pre_on_update(self):
        self.pre_on_update_state = (
            self.selection(),
            self.scroll_value(),
            self.font_size,
        )

    def post_on_update(self):
        selection, scroll_value, font_size = self.pre_on_update_state
        self.set_selection(selection)
        if font_size == self.font_size:
            self.set_scroll_value(scroll_value)

    def on_view_changed(self):
        self.text_edit.pop_refresh()

    def on_zoom_(self, sign):
        self.text_edit.setFocus()
        if settings.text_editor_sync_zooming:
            new_font_size = (
                self.font_size
                + self.font_size * settings.text_editor_zoom_factor * sign
            )
            for text_edit in self.text_edits:
                text_edit.font_size = new_font_size
            self.font_size = self.font_size
        else:
            self.font_size = (
                self.font_size
                + self.font_size * settings.text_editor_zoom_factor * sign
            )

    def on_zoom_in(self):
        self.on_zoom_(1)

    def on_zoom_out(self):
        self.on_zoom_(-1)

    def on_zoom_default(self):
        self.font_size = settings.text_editor_font_size

    def on_update_font(self):
        pre_y = self.text_edit.cursorRect().y()
        self.setStyleSheet(
            "_TextEdit {" f"    font-size: {self.font_size}pt;" "}"
        )
        space_width = self.text_edit.fontMetrics().horizontalAdvance(" ")
        self.text_edit.setTabStopDistance(
            settings.text_editor_num_spaces_per_tab * space_width,
        )
        line_height = self.text_edit.fontMetrics().height()
        frame_format = self.text_edit.document().rootFrame().frameFormat()
        frame_format.setBottomMargin(
            settings.text_editor_look_ahead_lines * line_height
        )
        self.scrollbar.line_height = line_height
        post_y = self.text_edit.cursorRect().y()
        diff_y = post_y - pre_y
        scrollbar = self.scrollbar_signaler
        scrollbar.set_value(scrollbar.value() + diff_y)
        self.text_edit.ensureCursorVisible()

    def on_update_settings(self):
        text_cursor = self.text_edit.textCursor()
        text_cursor.joinPreviousEditBlock()
        self.scrollbar.setVisible(settings.app_scroll_bar_visible)
        self.scrollbar_h.setVisible(
            settings.app_scroll_bar_visible
            and not settings.text_editor_wrap_long_lines
        )
        if settings.text_editor_sync_scrolling:
            self.scrollbar_signaler.linked_scrollbars = (
                self.scrollbar_signalers
            )
        else:
            self.scrollbar_signaler.linked_scrollbars = {
                self.scrollbar_signaler
            }
        self.scrollbar.setFixedWidth(
            int(round(settings.app_scroll_trough_thickness * self.dpi))
        )
        self.scrollbar_h.setFixedHeight(
            int(round(settings.app_scroll_trough_thickness * self.dpi))
        )
        frame_format = self.text_edit.document().rootFrame().frameFormat()
        frame_format.setLeftMargin(
            settings.text_editor_margin_left * self.dpi,
        )
        frame_format.setRightMargin(
            settings.text_editor_margin_right * self.dpi,
        )
        frame_format.setTopMargin(
            settings.text_editor_margin_top * self.dpi,
        )
        self._font_size = settings.text_editor_font_size
        self.setStyleSheet(
            "QTextEdit {" f"    font-size: {self.font_size}pt;" "}"
        )
        space_width = self.text_edit.fontMetrics().horizontalAdvance(" ")
        self.text_edit.setTabStopDistance(
            settings.text_editor_num_spaces_per_tab * space_width,
        )
        line_height = self.text_edit.fontMetrics().height()
        frame_format.setBottomMargin(
            settings.text_editor_look_ahead_lines * line_height
        )
        self.scrollbar.line_height = line_height
        self.text_edit.document().rootFrame().setFrameFormat(frame_format)
        self.text_edit.setAlignment(
            settings.Alignment.qt(settings.text_editor_alignment)
        )
        text = self.text_edit.toPlainText()
        text_cursor.select(QTextCursor.SelectionType.Document)
        text_cursor.insertText(text)
        self.text_edit.setWordWrapMode(
            (
                QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere
                if settings.text_editor_wrap_long_lines
                else QTextOption.WrapMode.NoWrap
            ),
        )
        text_cursor.endEditBlock()
        self.update()


class _TextEdit(QTextEdit):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.context_menu = menus.EditMenu(main_window)
        self.on_focus_in = lambda: None
        self.on_focus_out = lambda: None
        self.on_text_modified = lambda: None
        self.scrollbar = None
        self.scrollbar_h = None
        self.popup = None
        self.find_window = None
        self.find_text = ""
        self.replace_window = None
        self.replace_text = ""
        self.find_replace_window_geometry = None
        self.prev_scrollbar_value = 0
        self.prev_popup_cursor = None
        self.ignored_key_sequences = set()
        self.pop_forward = lambda: None
        self.pop_backward = lambda: None
        self.cursorPositionChanged.connect(self.on_cursor_position_changed)
        self.textChanged.connect(self.text_modified)
        self.on_update_settings()

    @staticmethod
    def maybe_match_case_str_eq(str1, str2, match_case):
        if match_case:
            return str1 == str2
        else:
            return str1.lower() == str2.lower()

    def contextMenuEvent(self, event):
        self.context_menu.move(event.globalPos())
        self.context_menu.show()

    def dragEnterEvent(self, event):
        event.accept()

    def event(self, event):
        if event.type() == QEvent.Type.ShortcutOverride:
            event.ignore()
            return False
        return super().event(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.on_focus_in()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.on_focus_out()

    def insertFromMimeData(self, source):
        is_file = False
        for url in source.urls():
            path = url.path()[1:]
            if os.path.exists(path):
                is_file = True
                self.main_window.handle_dropped_file(
                    os.path.normpath(path),
                    self.parent().parent(),
                )
        if is_file:
            return
        data = QMimeData()
        data.setText(source.text())
        super().insertFromMimeData(data)

    def keyPressEvent(self, event):
        key_sequence = QKeySequence(event.keyCombination()).toString().lower()
        if key_sequence in self.ignored_key_sequences:
            return
        key = event.key()
        if key == Qt.Key.Key_Escape:
            if settings.dict_popup_hide_on == settings.DictPopupHideOn.ESCAPE:
                if self.popup is not None and self.popup.isVisible():
                    self.pop_down()
                else:
                    self.clearFocus()
            else:
                self.clearFocus()
            return
        if self.isReadOnly():
            if key in {
                Qt.Key.Key_Shift,
                Qt.Key.Key_Control,
                Qt.Key.Key_Alt,
                Qt.Key.Key_Meta,
            }:
                return
            messages.TextLockedWarningMessage(
                self.parent().parent().file_name,
                lambda: self.setReadOnly(False),
            ).show()
            return
        elif key == Qt.Key.Key_Return:
            self.insertHtml("<br/>")
            return
        elif key == Qt.Key.Key_Tab:
            if settings.text_editor_use_spaces_for_tab:
                self.insertPlainText(
                    " " * settings.text_editor_num_spaces_per_tab
                )
                return
        if Qt.KeyboardModifier.ControlModifier in event.modifiers():
            return
        super().keyPressEvent(event)

    def enterEvent(self, event):
        app.mouse_event_widget = self
        super().enterEvent(event)

    def leaveEvent(self, event):
        app.mouse_event_widget = None
        if settings.dict_popup_hide_on == settings.DictPopupHideOn.LEAVE:
            self.pop_down()
        super().leaveEvent(event)

    def is_global_position_within_popup(self, global_position):
        if self.popup is None or not self.popup.isVisible():
            return False
        text_edit = self.popup.dict_view.text_edit
        return text_edit.rect().contains(
            text_edit.mapFromGlobal(global_position)
        )

    def global_mouse_move_event(self, event):
        if settings.dict_popup_show_on != settings.DictPopupShowOn.HOVER:
            return
        if settings.dict_popup_hover_delay:
            QTimer.singleShot(
                settings.dict_popup_hover_delay,
                lambda x=event.globalPos(): self.pop_delayed(x),
            )
            return
        self.pop_up(self.mapFromGlobal(event.globalPos()))

    def global_mouse_press_event(self, event):
        if event.button() != Qt.MouseButton.LeftButton or (
            settings.dict_popup_blocks_clicks
            and self.is_global_position_within_popup(event.globalPos())
        ):
            return
        if (
            settings.dict_popup_show_on == settings.DictPopupShowOn.CLICK
            and settings.dict_popup_hide_on == settings.DictPopupHideOn.CLICK
        ):
            self.pop_opposite(self.mapFromGlobal(event.globalPos()))
        else:
            if settings.dict_popup_show_on == settings.DictPopupShowOn.CLICK:
                self.pop_up(self.mapFromGlobal(event.globalPos()))
            if settings.dict_popup_hide_on == settings.DictPopupHideOn.CLICK:
                self.pop_down()
            elif settings.dict_popup_show_on == settings.DictPopupShowOn.HOVER:
                self.pop_up(self.mapFromGlobal(event.globalPos()))

    def global_mouse_double_click_event(self, event):
        if event.button() != Qt.MouseButton.LeftButton or (
            settings.dict_popup_blocks_clicks
            and self.is_global_position_within_popup(event.globalPos())
        ):
            return
        if (
            settings.dict_popup_show_on
            == settings.DictPopupShowOn.DOUBLE_CLICK
            and settings.dict_popup_hide_on
            == settings.DictPopupHideOn.DOUBLE_CLICK
        ):
            self.pop_opposite(self.mapFromGlobal(event.globalPos()))
        else:
            if (
                settings.dict_popup_show_on
                == settings.DictPopupShowOn.DOUBLE_CLICK
            ):
                self.pop_up(self.mapFromGlobal(event.globalPos()))
            if (
                settings.dict_popup_hide_on
                == settings.DictPopupHideOn.DOUBLE_CLICK
            ):
                self.pop_down()
            elif settings.dict_popup_show_on == settings.DictPopupShowOn.HOVER:
                self.pop_up(self.mapFromGlobal(event.globalPos()))

    def undo(self):
        if self.isReadOnly():
            messages.TextLockedWarningMessage(
                self.parent().parent().file_name,
                lambda: self.setReadOnly(False),
            ).show()
            return
        super().undo()

    def redo(self):
        if self.isReadOnly():
            messages.TextLockedWarningMessage(
                self.parent().parent().file_name,
                lambda: self.setReadOnly(False),
            ).show()
            return
        super().redo()

    def cut(self):
        if self.isReadOnly():
            messages.TextLockedWarningMessage(
                self.parent().parent().file_name,
                lambda: self.setReadOnly(False),
            ).show()
            return
        super().cut()

    def paste(self):
        if self.isReadOnly():
            messages.TextLockedWarningMessage(
                self.parent().parent().file_name,
                lambda: self.setReadOnly(False),
            ).show()
            return
        super().paste()

    def wheelEvent(self, event):
        self.parent().wheelEvent(event)

    def wheel_event(self, event):
        super().wheelEvent(event)

    def clear_undo_stack(self):
        self.setUndoRedoEnabled(False)
        self.setUndoRedoEnabled(True)

    def line_min_max(self, cursor):
        start_cursor = QTextCursor(cursor)
        start_cursor.movePosition(
            QTextCursor.MoveOperation.StartOfLine,
            QTextCursor.MoveMode.MoveAnchor,
            n=1,
        )
        start_cursor_rect = self.cursorRect(start_cursor)
        line_x_start = start_cursor_rect.x()
        start_cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        line_length = self.fontMetrics().horizontalAdvance(
            start_cursor.selectedText()
        )
        if cursor.block().textDirection() == Qt.LayoutDirection.LeftToRight:
            line_x_min = line_x_start
            line_x_max = line_x_start + line_length
        else:
            line_x_max = line_x_start
            line_x_min = line_x_start - line_length
        line_y_min = start_cursor_rect.y()
        line_y_max = line_y_min + start_cursor_rect.height()
        return (
            line_x_min,
            line_x_max,
            line_y_min,
            line_y_max,
        )

    def pop_up(self, position=None, cursor=None, skip_check=False):
        if self.popup is None:
            return
        if cursor is None:
            cursor = self.cursorForPosition(position)
        else:
            cursor = QTextCursor(cursor)
            cursor_rect = self.cursorRect(cursor)
            position = QPoint(
                cursor_rect.x() + cursor_rect.width() // 2,
                cursor_rect.y() + cursor_rect.height() // 2,
            )
        self.prev_popup_cursor = QTextCursor(cursor)
        (
            line_x_min,
            line_x_max,
            line_y_min,
            line_y_max,
        ) = self.line_min_max(cursor)
        x = position.x()
        y = position.y()
        index = cursor.positionInBlock()
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        text = cursor.selectedText().replace(" ", "")
        if skip_check or (
            line_x_min - 2 < x < line_x_max + 2
            and line_y_min - 1 < y < line_y_max + 1
        ):
            self.popup.pop_up(
                x,
                line_y_min,
                line_y_max,
                self.width(),
                self.height(),
                text,
                index,
            )
        else:
            self.popup.hide()

    def pop_down(self):
        if self.popup is not None:
            self.popup.hide()

    def pop_opposite(self, position):
        if self.popup is not None:
            if self.popup.isVisible():
                self.popup.hide()
            else:
                self.pop_up(position)

    def pop_refresh(self):
        if (
            self.popup is not None
            and self.popup.isVisible()
            and self.prev_popup_cursor is not None
        ):
            self.pop_up(cursor=self.prev_popup_cursor)

    def pop_delayed(self, global_position):
        if (
            self.is_global_position_within_popup(global_position)
            and self.popup.dict_view.text_edit.hasFocus()
        ):
            return
        if global_position != QCursor.pos():
            return
        if self.popup is not None:
            self.popup.dict_view.text_edit.clearFocus()
            if (
                settings.text_editor_set_focus_on_hover
                and self.rect().contains(self.mapFromGlobal(global_position))
            ):
                self.setFocus()
        self.pop_up(self.mapFromGlobal(global_position))

    def pop_forward_char(self):
        if self.popup is None:
            return
        if self.prev_popup_cursor is not None and self.popup.isVisible():
            start_cursor = self.prev_popup_cursor
        else:
            start_cursor = self.textCursor()
        start_cursor.movePosition(
            QTextCursor.MoveOperation.NextCharacter,
            QTextCursor.MoveMode.MoveAnchor,
            n=1,
        )
        start_cursor_rect = self.cursorRect(start_cursor)
        end_cursor = QTextCursor(start_cursor)
        end_cursor.movePosition(
            QTextCursor.MoveOperation.NextCharacter,
            QTextCursor.MoveMode.KeepAnchor,
            n=1,
        )
        text = end_cursor.selectedText()
        char_length = self.fontMetrics().horizontalAdvance(text)
        if (
            start_cursor.block().textDirection()
            == Qt.LayoutDirection.LeftToRight
        ):
            plus_or_minus_1 = 1
        else:
            plus_or_minus_1 = -1
        centered_position = QPoint(
            start_cursor_rect.x() + plus_or_minus_1 * (char_length // 2),
            start_cursor_rect.y() + start_cursor_rect.height() // 2,
        )
        self.pop_up(
            position=centered_position,
            skip_check=True,
        )
        if settings.dict_popup_on_shortcut_move_cursor:
            self.setTextCursor(self.prev_popup_cursor)
            self.ensureCursorVisible()
        self.prev_popup_cursor = start_cursor

    def pop_backward_char(self):
        if self.popup is None:
            return
        if self.prev_popup_cursor is not None and self.popup.isVisible():
            start_cursor = self.prev_popup_cursor
        else:
            start_cursor = self.textCursor()
        start_cursor.movePosition(
            QTextCursor.MoveOperation.PreviousCharacter,
            QTextCursor.MoveMode.MoveAnchor,
            n=1,
        )
        start_cursor_rect = self.cursorRect(start_cursor)
        end_cursor = QTextCursor(start_cursor)
        end_cursor.movePosition(
            QTextCursor.MoveOperation.NextCharacter,
            QTextCursor.MoveMode.KeepAnchor,
            n=1,
        )
        text = end_cursor.selectedText()
        char_length = self.fontMetrics().horizontalAdvance(text)
        if (
            start_cursor.block().textDirection()
            == Qt.LayoutDirection.LeftToRight
        ):
            plus_or_minus_1 = 1
        else:
            plus_or_minus_1 = -1
        centered_position = QPoint(
            start_cursor_rect.x() + plus_or_minus_1 * (char_length // 2),
            start_cursor_rect.y() + start_cursor_rect.height() // 2,
        )
        self.pop_up(
            position=centered_position,
            skip_check=True,
        )
        if settings.dict_popup_on_shortcut_move_cursor:
            self.setTextCursor(self.prev_popup_cursor)
            self.ensureCursorVisible()
        self.prev_popup_cursor = start_cursor

    def pop_forward_word(self):
        if self.popup is None:
            return
        if self.prev_popup_cursor is not None and self.popup.isVisible():
            start_cursor = self.prev_popup_cursor
        else:
            start_cursor = self.textCursor()
        start_cursor.movePosition(
            QTextCursor.MoveOperation.NextWord,
            QTextCursor.MoveMode.MoveAnchor,
            n=1,
        )
        end_cursor = QTextCursor(start_cursor)
        end_cursor.movePosition(
            QTextCursor.MoveOperation.EndOfWord,
            QTextCursor.MoveMode.KeepAnchor,
            n=1,
        )
        selected_text = end_cursor.selectedText()
        if (
            len(selected_text) == 1
            and not selected_text.isalnum()
            and start_cursor.position() != end_cursor.position()
        ):
            utils.run_after_current_event(self.pop_forward_word)
        start_cursor_rect = self.cursorRect(start_cursor)
        end_cursor_rect = self.cursorRect(end_cursor)
        centered_position = QPoint(
            (start_cursor_rect.x() + end_cursor_rect.x()) // 2,
            start_cursor_rect.y() + start_cursor_rect.height() // 2,
        )
        self.pop_up(
            position=centered_position,
            skip_check=True,
        )
        if settings.dict_popup_on_shortcut_move_cursor:
            self.setTextCursor(self.prev_popup_cursor)
            self.ensureCursorVisible()

    def pop_backward_word(self):
        if self.popup is None:
            return
        if self.prev_popup_cursor is not None and self.popup.isVisible():
            start_cursor = self.prev_popup_cursor
        else:
            start_cursor = self.textCursor()
        start_cursor.movePosition(
            QTextCursor.MoveOperation.PreviousWord,
            QTextCursor.MoveMode.MoveAnchor,
            n=2,
        )
        end_cursor = QTextCursor(start_cursor)
        end_cursor.movePosition(
            QTextCursor.MoveOperation.EndOfWord,
            QTextCursor.MoveMode.KeepAnchor,
            n=1,
        )
        selected_text = end_cursor.selectedText()
        if (
            len(selected_text) == 1
            and not selected_text.isalnum()
            and start_cursor.position() != 0
        ):
            utils.run_after_current_event(self.pop_backward_word)
        start_cursor_rect = self.cursorRect(start_cursor)
        end_cursor_rect = self.cursorRect(end_cursor)
        if (
            self.textCursor().block().textDirection()
            == Qt.LayoutDirection.LeftToRight
        ):
            offset = 1
        else:
            offset = -1
        centered_position = QPoint(
            (start_cursor_rect.x() + end_cursor_rect.x()) // 2 + offset,
            start_cursor_rect.y() + start_cursor_rect.height() // 2,
        )
        self.pop_up(
            position=centered_position,
            skip_check=True,
        )
        if settings.dict_popup_on_shortcut_move_cursor:
            self.setTextCursor(self.prev_popup_cursor)
            self.ensureCursorVisible()

    def text_modified(self):
        self.pop_refresh()
        self.on_text_modified()

    def on_undo(self):
        self.undo()

    def on_redo(self):
        self.redo()

    def on_cut(self):
        self.cut()

    def on_copy(self):
        self.copy()

    def on_paste(self):
        self.paste()

    def on_select_all(self):
        self.selectAll()

    def on_find(self):
        try:
            self.replace_window.close()
        except (AttributeError, RuntimeError):
            pass
        self.replace_window = None
        try:
            self.find_window.find_line_edit.selectAll()
        except (AttributeError, RuntimeError):
            self.find_window = find_replace_windows.FindWindow(
                self.on_find_replace_window_close,
                self.on_find_next,
                self.on_find_prev,
                self.on_find_text_edited,
            )
            self.find_window.find_line_edit.setText(self.find_text)
            try:
                self.find_window.setGeometry(self.find_replace_window_geometry)
            except TypeError:
                self.find_window.move_to_text_editor_center(self)
        self.main_window.add_child_window(self.find_window)
        self.find_window.activateWindow()
        self.find_window.show()

    def on_replace(self):
        try:
            self.find_window.close()
        except (AttributeError, RuntimeError):
            pass
        self.find_window = None
        try:
            self.replace_window.find_line_edit.selectAll()
        except (AttributeError, RuntimeError):
            self.replace_window = find_replace_windows.ReplaceWindow(
                self.on_find_replace_window_close,
                self.on_find_next,
                self.on_find_prev,
                self.on_find_text_edited,
                self.on_replace_next,
                self.on_replace_prev,
                self.on_replace_all,
                self.on_replace_text_edited,
            )
            self.replace_window.find_line_edit.setText(self.find_text)
            self.replace_window.replace_line_edit.setText(self.replace_text)
            try:
                self.replace_window.setGeometry(
                    self.find_replace_window_geometry
                )
            except TypeError:
                self.replace_window.move_to_text_editor_center(self)
        self.main_window.add_child_window(self.replace_window)
        self.replace_window.activateWindow()
        self.replace_window.show()

    def on_find_(
        self,
        find_text,
        match_case,
        wrap_around,
        show_message,
        initial_flag,
        start_or_end,
    ):
        flags = initial_flag
        if match_case:
            flags = flags | QTextDocument.FindFlag.FindCaseSensitively
        if not self.find(find_text, flags):
            if wrap_around:
                selection = self.parent().selection()
                text_cursor = self.textCursor()
                text_cursor.movePosition(start_or_end)
                self.setTextCursor(text_cursor)
                if not self.find(find_text, flags):
                    self.parent().set_selection(selection)
                    if show_message:
                        messages.TextNotFoundInfoMessage(find_text).show()
                    return False
            else:
                if show_message:
                    messages.TextNotFoundInfoMessage(find_text).show()
                return False
        return True

    def on_find_next(
        self,
        find_text,
        match_case,
        wrap_around,
        show_message=True,
    ):
        return self.on_find_(
            find_text,
            match_case,
            wrap_around,
            show_message,
            initial_flag=QTextDocument.FindFlag(0),
            start_or_end=QTextCursor.MoveOperation.Start,
        )

    def on_find_prev(
        self,
        find_text,
        match_case,
        wrap_around,
        show_message=True,
    ):
        return self.on_find_(
            find_text,
            match_case,
            wrap_around,
            show_message,
            initial_flag=QTextDocument.FindFlag.FindBackward,
            start_or_end=QTextCursor.MoveOperation.End,
        )

    def on_find_text_edited(self, text):
        self.find_text = text

    def on_replace_(
        self,
        find_text,
        replace_text,
        match_case,
        wrap_around,
        find_next_or_prev,
    ):
        selected_text = self.textCursor().selectedText()
        selection_matches = self.maybe_match_case_str_eq(
            find_text,
            selected_text,
            match_case,
        )
        if selection_matches:
            self.insertPlainText(replace_text)
        if (
            not find_next_or_prev(find_text, match_case, wrap_around, False)
            and not selection_matches
        ):
            messages.TextNotFoundInfoMessage(find_text).show()

    def on_replace_next(
        self,
        find_text,
        replace_text,
        match_case,
        wrap_around,
    ):
        self.on_replace_(
            find_text,
            replace_text,
            match_case,
            wrap_around,
            find_next_or_prev=self.on_find_next,
        )

    def on_replace_prev(
        self,
        find_text,
        replace_text,
        match_case,
        wrap_around,
    ):
        self.on_replace_(
            find_text,
            replace_text,
            match_case,
            wrap_around,
            find_next_or_prev=self.on_find_prev,
        )

    def on_replace_all(
        self,
        find_text,
        replace_text,
        match_case,
    ):
        parent = self.parent()
        selection = parent.selection()
        text_in = self.toPlainText()
        pattern = re.compile(
            re.escape(find_text), re.NOFLAG if match_case else re.IGNORECASE
        )
        text_out = pattern.sub(replace_text, text_in)
        text_cursor = self.textCursor()
        text_cursor.beginEditBlock()
        text_cursor.select(QTextCursor.SelectionType.Document)
        text_cursor.insertText(text_out)
        text_cursor.endEditBlock()
        parent.set_selection(selection)

    def on_replace_text_edited(self, text):
        self.replace_text = text

    def on_find_replace_window_close(self, geometry):
        self.find_replace_window_geometry = geometry

    def on_cursor_position_changed(self):
        if not settings.text_editor_look_ahead_lines:
            return
        text_cursor = self.textCursor()
        block = text_cursor.block()
        last_block = self.document().lastBlock()
        if block != last_block:
            return
        position_in_block = text_cursor.positionInBlock()
        line = last_block.layout().lineForTextPosition(position_in_block)
        line.lineNumber()
        if line.lineNumber() == last_block.layout().lineCount() - 1:
            scrollbar = self.scrollbar.scrollbar
            scrollbar.set_value(scrollbar.maximum())

    def on_update_settings(self):
        keys_with_priority_over_shortcuts = {
            "up",
            "down",
            "left",
            "right",
            "return",
        }
        if (
            actions.MovePopupForward.on_action
            not in app.shortcut_to_action_fn["tab"]
        ):
            keys_with_priority_over_shortcuts.add("tab")
        self.ignored_key_sequences = (
            set(app.shortcut_to_action_fn) - keys_with_priority_over_shortcuts
        )
        if (
            settings.dict_popup_on_shortcut_move_by
            == settings.DictPopupMoveBy.CHAR
        ):
            self.pop_forward = self.pop_forward_char
            self.pop_backward = self.pop_backward_char
        elif (
            settings.dict_popup_on_shortcut_move_by
            == settings.DictPopupMoveBy.WORD
        ):
            self.pop_forward = self.pop_forward_word
            self.pop_backward = self.pop_backward_word
        else:
            self.pop_forward = lambda: None
            self.pop_backward = lambda: None
        self.update()


class ScrollbarSignaler(QScrollBar):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.on_slider_change = lambda x: None
        self.linked_scrollbars = set()

    def sliderChange(self, change):
        self.on_slider_change(change)
        for scrollbar in self.linked_scrollbars:
            scrollbar.setValue(self.value())

    def set_value(self, value):
        for scrollbar in self.linked_scrollbars:
            scrollbar.setValue(value)


class Scrollbar(QWidget):
    def __init__(self, text_edit, scrollbar):
        super().__init__(text_edit)
        self.scrollbar = scrollbar
        self.trough = Trough(scrollbar, text_edit.text_edit.setFocus)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.trough)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.line_height = 0
        self.scroll_step_mouse = 0
        self.scroll_step_trackpad = 0

    def on_line_up(self):
        scrollbar = self.scrollbar
        scrollbar.set_value(scrollbar.value() - self.line_height)

    def on_line_down(self):
        scrollbar = self.scrollbar
        scrollbar.set_value(scrollbar.value() + self.line_height)

    def on_page_up(self):
        scrollbar = self.scrollbar
        scrollbar.set_value(scrollbar.value() - scrollbar.pageStep())

    def on_page_down(self):
        scrollbar = self.scrollbar
        scrollbar.set_value(scrollbar.value() + scrollbar.pageStep())


class Trough(QWidget):
    def __init__(self, scrollbar, set_focus):
        super().__init__()
        self.bar = Bar(self, scrollbar)
        self.set_focus = set_focus
        self.timer = QTimer()
        self.cursor_within = False
        self._hover = False
        self._pressed = False
        self.setMouseTracking(True)
        self.timer.timeout.connect(self.page_up)
        self.timer.timeout.connect(self.page_down)
        self.brush = None
        self.update_brush()
        self.on_update_settings()
        self.on_update_theme()

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    @property
    def hover(self):
        return self._hover

    @hover.setter
    def hover(self, hover):
        self._hover = hover
        self.setProperty("hover", hover)
        self.style().polish(self)

    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, pressed):
        self._pressed = pressed
        self.setProperty("pressed", pressed)
        self.style().polish(self)

    @staticmethod
    def x_or_y(position):
        return position.y()

    def enterEvent(self, event):
        self.cursor_within = True

    def leaveEvent(self, event):
        self.cursor_within = False
        bar = self.bar
        bar.hover = False
        bar.on_update_theme()
        self.hover = False
        self.on_update_settings()
        self.on_update_theme()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.brush)

    def mouseMoveEvent(self, event):
        bar = self.bar
        press_position = self.x_or_y(event.position())
        if bar.pressed:
            delta_pos = press_position - bar.offset_at_press
            new_pos = bar.position_at_press + delta_pos
            scrollable_span = bar.length - bar.span
            if not scrollable_span:
                return
            new_rel_pos = new_pos / scrollable_span
            scrollbar = bar.scrollbar
            new_value = new_rel_pos * scrollbar.maximum()
            scrollbar.set_value(new_value)
        elif self.cursor_within and not self.pressed:
            if bar.position <= press_position < bar.position + bar.span:
                bar.hover = True
                self.hover = False
                bar.on_update_theme()
                self.on_update_theme()
            else:
                bar.hovered_over = False
                self.hover = True
                bar.on_update_theme()
                self.on_update_theme()

    def mousePressEvent(self, event):
        self.set_focus()
        if event.button() != Qt.MouseButton.LeftButton:
            return
        bar = self.bar
        press_position = self.x_or_y(event.position())
        if bar.position <= press_position < bar.position + bar.span:
            bar.pressed = True
            bar.on_update_theme()
            bar.offset_at_press = press_position
            bar.position_at_press = bar.position
        else:
            self.pressed = True
            self.on_update_theme()
            if (
                settings.text_editor_scroll_trough_behavior_on_press
                == settings.ScrollTroughBehaviorOnPress.JUMP_TO
            ):
                new_pos = press_position - bar.span / 2.0
                scrollable_span = bar.length - bar.span
                if not scrollable_span:
                    return
                new_rel_pos = new_pos / scrollable_span
                scrollbar = bar.scrollbar
                new_value = new_rel_pos * scrollbar.maximum()
                scrollbar.set_value(new_value)
                bar.pressed = True
                bar.on_update_theme()
                bar.offset_at_press = press_position
                bar.position_at_press = bar.position
            else:
                self.timer.stop()
                if press_position < bar.position:
                    self.page_up()
                else:
                    self.page_down()
                QTimer.singleShot(
                    settings.app_repeated_action_initial_delay,
                    lambda: (
                        self.timer.start() if self.pressed else lambda: None
                    ),
                )

    def mouseReleaseEvent(self, event):
        button = event.button()
        if button == Qt.MouseButton.LeftButton:
            self.timer.stop()
            bar = self.bar
            bar.pressed = False
            bar.on_update_theme()
            self.pressed = False
            self.on_update_theme()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = event.size()
        self.bar.setGeometry(
            0,
            0,
            size.width(),
            size.height(),
        )

    def page_up(self):
        bar = self.bar
        scrollbar = bar.scrollbar
        cursor_position = self.x_or_y(self.mapFromGlobal(QCursor.pos()))
        if cursor_position >= bar.position:
            return
        scrollbar.set_value(scrollbar.value() - scrollbar.pageStep())

    def page_down(self):
        bar = self.bar
        scrollbar = bar.scrollbar
        cursor_position = self.x_or_y(self.mapFromGlobal(QCursor.pos()))
        if cursor_position <= bar.position + bar.span:
            return
        scrollbar.set_value(scrollbar.value() + scrollbar.pageStep())

    def on_update_settings(self):
        self.timer.setInterval(settings.app_repeated_action_interval)
        self.bar.setGeometry(
            0,
            0,
            self.width(),
            self.height(),
        )
        self.update()

    def update_brush(self):
        color = self.palette().color(QPalette.ColorRole.Base)
        if self.pressed:
            color.setAlphaF(settings.app_scroll_trough_opacity_pressed)
        elif self.hover:
            color.setAlphaF(settings.app_scroll_trough_opacity_hover)
        else:
            color.setAlphaF(settings.app_scroll_trough_opacity_normal)
        self.brush = QBrush(color)
        self.update()

    def on_update_theme(self):
        utils.run_after_current_event(self.update_brush)


class Bar(QWidget):
    def __init__(self, parent, scrollbar):
        super().__init__(parent)
        self.scrollbar = scrollbar
        self.scrollbar.on_slider_change = self.on_slider_change
        self._hover = False
        self._pressed = False
        self.position = 0
        self.span = 0
        self.offset_at_press = 0
        self.position_at_press = 0
        self.brush = None
        self.update_brush()
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.on_update_theme()

    @property
    def hover(self):
        return self._hover

    @hover.setter
    def hover(self, hover):
        self._hover = hover
        self.setProperty("hover", hover)
        self.style().polish(self)

    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, pressed):
        self._pressed = pressed
        self.setProperty("pressed", pressed)
        self.style().polish(self)

    @property
    def thickness(self):
        return self.width()

    @property
    def length(self):
        return self.height()

    @property
    def bar_geometry(self):
        return QRect(0, self.position, self.thickness, self.span)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter_path = QPainterPath()
        thickness = self.thickness
        radius = thickness / 2.0
        bar_geometry = self.bar_geometry
        painter_path.addRoundedRect(bar_geometry, radius, radius)
        painter.fillPath(painter_path, self.brush)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_geometry()

    def update_geometry(self):
        scrollbar = self.scrollbar
        maximum = scrollbar.maximum()
        length = self.length
        if not maximum:
            self.span = length
            self.position = 0
            self.setVisible(False)
            return
        else:
            self.setVisible(True)
        page_step = scrollbar.pageStep()
        rel_span = page_step / (maximum + page_step)
        self.span = max(
            int(round(rel_span * length)),
            int(
                round(
                    self.thickness
                    * settings.app_scroll_bar_min_length_rel_thickness
                )
            ),
        )
        rel_pos = scrollbar.value() / maximum
        scrollable_span = length - self.span
        self.position = int(round(rel_pos * scrollable_span))
        self.update()

    def update_position(self):
        scrollbar = self.scrollbar
        maximum = scrollbar.maximum()
        if not maximum:
            self.position = 0
            self.setVisible(False)
            return
        else:
            self.setVisible(True)
        rel_pos = scrollbar.value() / maximum
        scrollable_span = self.length - self.span
        self.position = int(round(rel_pos * scrollable_span))
        self.update()

    def on_slider_change(self, change):
        if change == QScrollBar.SliderChange.SliderValueChange:
            self.update_position()
        elif change == QScrollBar.SliderChange.SliderRangeChange:
            self.update_geometry()

    def update_brush(self):
        color = self.palette().color(QPalette.ColorRole.Base)
        if self.pressed:
            color.setAlphaF(settings.app_scroll_bar_opacity_pressed)
        elif self.hover:
            color.setAlphaF(settings.app_scroll_bar_opacity_hover)
        else:
            color.setAlphaF(settings.app_scroll_bar_opacity_normal)
        self.brush = QBrush(color)
        self.update()

    def on_update_theme(self):
        utils.run_after_current_event(self.update_brush)


class ScrollbarH(Scrollbar):
    def __init__(self, text_edit, scrollbar):
        QWidget.__init__(self, text_edit)
        self.scrollbar = scrollbar
        self.trough = TroughH(scrollbar, text_edit.text_edit.setFocus)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.trough)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.scroll_step_mouse = 0
        self.scroll_step_trackpad = 0


class TroughH(Trough):
    def __init__(self, scrollbar, set_focus):
        QWidget.__init__(self)
        self.bar = BarH(self, scrollbar)
        self.set_focus = set_focus
        self.timer = QTimer()
        self.cursor_within = False
        self.hover = False
        self.pressed = False
        self.setMouseTracking(True)
        self.timer.timeout.connect(self.page_up)
        self.timer.timeout.connect(self.page_down)
        self.brush = None
        self.update_brush()
        self.on_update_settings()
        self.on_update_theme()

    @staticmethod
    def x_or_y(position):
        return position.x()


class BarH(Bar):
    def __init__(self, parent, scrollbar):
        QWidget.__init__(self, parent)
        self.scrollbar = scrollbar
        self.scrollbar.on_slider_change = self.on_slider_change
        self._hover = False
        self._pressed = False
        self.position = 0
        self.span = 0
        self.offset_at_press = 0
        self.position_at_press = 0
        self.brush = None
        self.update_brush()
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.on_update_theme()

    @property
    def thickness(self):
        return self.height()

    @property
    def length(self):
        return self.width()

    @property
    def bar_geometry(self):
        return QRect(self.position, 0, self.span, self.thickness)
