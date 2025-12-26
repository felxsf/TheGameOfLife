import random
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QSlider,
    QLabel,
    QCheckBox,
    QComboBox,
    QDialog,
    QTextEdit,
    QDialogButtonBox,
    QScrollArea,
    QSpinBox,
    QFormLayout,
    QSizePolicy,
    QHBoxLayout,
    QVBoxLayout,
)


class GridWidget(QWidget):
    def __init__(self, grid, cell_size, alive_color="#00e676", bg_color="#121212"):
        super().__init__()
        self.grid = grid
        self.cell_size = cell_size
        self.alive_color = QColor(alive_color)
        self.bg_color = QColor(bg_color)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_colors(self, alive_hex, bg_hex):
        self.alive_color = QColor(alive_hex)
        self.bg_color = QColor(bg_hex)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.fillRect(self.rect(), self.bg_color)
        
        # Centering logic
        grid_w = len(self.grid[0]) * self.cell_size
        grid_h = len(self.grid) * self.cell_size
        off_x = (self.width() - grid_w) // 2
        off_y = (self.height() - grid_h) // 2

        gap = max(1, int(self.cell_size * 0.12))
        radius = max(2.0, self.cell_size * 0.18)
        
        # Only draw if visible
        for r in range(len(self.grid)):
            for c in range(len(self.grid[0])):
                if self.grid[r][c] == 1:
                    x0 = off_x + c * self.cell_size + gap
                    y0 = off_y + r * self.cell_size + gap
                    w = self.cell_size - 2 * gap
                    h = self.cell_size - 2 * gap
                    if w > 0 and h > 0:
                        p.fillRect(x0, y0, w, h, self.alive_color)
                        if self.cell_size >= 12:
                            border = QColor(self.alive_color)
                            border.setAlpha(180)
                            p.setPen(border)
                            p.drawRoundedRect(x0, y0, w, h, radius, radius)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_at(event.position())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.toggle_at(event.position())

    def toggle_at(self, pos):
        grid_w = len(self.grid[0]) * self.cell_size
        grid_h = len(self.grid) * self.cell_size
        off_x = (self.width() - grid_w) // 2
        off_y = (self.height() - grid_h) // 2

        c = int(pos.x() - off_x) // self.cell_size
        r = int(pos.y() - off_y) // self.cell_size
        if 0 <= r < len(self.grid) and 0 <= c < len(self.grid[0]):
            self.grid[r][c] = 0 if self.grid[r][c] == 1 else 1
            self.update()
    
    def update_grid(self, grid, cell_size):
        self.grid = grid
        self.cell_size = cell_size
        self.update()


class PatternPreview(QWidget):
    def __init__(self, strings, cell_size=12, alive_color="#00e676", bg_color="#121212"):
        super().__init__()
        self.strings = strings
        self.cell_size = cell_size
        self.alive_color = QColor(alive_color)
        self.bg_color = QColor(bg_color)
        self.rows = len(strings)
        self.cols = len(strings[0]) if strings else 0
        self.setFixedSize(self.cols * cell_size, self.rows * cell_size)

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), self.bg_color)
        for r, row in enumerate(self.strings):
            for c, ch in enumerate(row):
                if ch == "#":
                    x0 = c * self.cell_size
                    y0 = r * self.cell_size
                    p.fillRect(x0, y0, self.cell_size, self.cell_size, self.alive_color)


class GameOfLifeWindow(QMainWindow):
    def __init__(self, rows=50, cols=80, cell_size=12):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.running = False
        self.delay_ms = 100
        self.wrap = False
        self.dark_mode = True
        self.density = 20
        self.auto_fit = True
        self.palettes = {
            "Verde": "#00e676",
            "Azul": "#2196f3",
            "Magenta": "#e91e63",
            "Naranja": "#ff9800",
        }
        self.current_palette = "Verde"

        self.setWindowTitle("Juego de la Vida de Conway")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)

        self.board = GridWidget(self.grid, self.cell_size)

        self.btn_play = QPushButton("Iniciar")
        self.btn_play.clicked.connect(self.toggle_run)

        self.btn_step = QPushButton("Paso")
        self.btn_step.clicked.connect(self.step_once)

        self.btn_clear = QPushButton("Limpiar")
        self.btn_clear.clicked.connect(self.clear)

        self.btn_rand = QPushButton("Aleatorio")
        self.btn_rand.clicked.connect(self.randomize)
        self.btn_fill = QPushButton("Rellenar")
        self.btn_fill.clicked.connect(self.fill_all)

        self.speed_label = QLabel("Velocidad")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(20, 400)
        self.speed_slider.setValue(self.delay_ms)
        self.speed_slider.valueChanged.connect(self.on_speed_change)

        self.wrap_check = QCheckBox("Envoltura")
        self.wrap_check.stateChanged.connect(self.on_wrap_change)

        self.dark_check = QCheckBox("Oscuro")
        self.dark_check.setChecked(True)
        self.dark_check.stateChanged.connect(self.on_theme_change)

        self.fit_check = QCheckBox("Ajustar")
        self.fit_check.setChecked(True)
        self.fit_check.stateChanged.connect(self.on_fit_change)

        self.palette_combo = QComboBox()
        self.palette_combo.addItems(list(self.palettes.keys()))
        self.palette_combo.currentIndexChanged.connect(self.on_theme_change)

        self.patterns_combo = QComboBox()
        self.patterns = {
            "Glider": [
                ".#.",
                "..#",
                "###",
            ],
            "Pulsar": [
                "..###...###..",
                "............",
                "#....#.#....#",
                "#....#.#....#",
                "#....#.#....#",
                "..###...###..",
                "............",
                "..###...###..",
                "#....#.#....#",
                "#....#.#....#",
                "#....#.#....#",
                "............",
                "..###...###..",
            ],
            "Spaceship (LWSS)": [
                ".#..#",
                "#....",
                "#...#",
                "####.",
            ],
            "Blinker": [
                "###",
            ],
            "Toad": [
                ".###",
                "###.",
            ],
            "Beacon": [
                "##..",
                "##..",
                "..##",
                "..##",
            ],
            "Block": [
                "##",
                "##",
            ],
            "Boat": [
                "#..",
                ".##",
                ".#.",
            ],
            "Loaf": [
                ".##.",
                "#..#",
                ".#.#",
                "..#.",
            ],
            "Tub": [
                ".#.",
                "#.#",
                ".#.",
            ],
            "Pentomino R": [
                "..#",
                ".##",
                ".#.",
            ],
        }
        self.patterns_combo.addItems(list(self.patterns.keys()))
        self.btn_insert = QPushButton("Insertar")
        self.btn_insert.clicked.connect(self.insert_selected_pattern)
        self.btn_info = QPushButton("Info")
        self.btn_info.clicked.connect(self.show_info)

        # --- Header ---
        self.btn_menu = QPushButton("≡")
        self.btn_menu.setFixedSize(40, 32)
        self.btn_menu.setObjectName("btn_menu")
        self.btn_menu.clicked.connect(self.toggle_sidebar)
        
        lbl_title = QLabel("Juego de la Vida")
        lbl_title.setObjectName("app_title")
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_menu)
        header_layout.setContentsMargins(16, 8, 16, 8)
        
        self.header_widget = QWidget()
        self.header_widget.setObjectName("header_bar")
        self.header_widget.setLayout(header_layout)

        # --- Sidebar Layout ---
        sidebar = QVBoxLayout()
        sidebar.setSpacing(20)
        sidebar.setContentsMargins(20, 20, 20, 20)
        sidebar.setAlignment(Qt.AlignTop)

        # Group: Playback
        grp_play = QVBoxLayout()
        grp_play.setSpacing(8)
        lbl_play = QLabel("Control")
        lbl_play.setObjectName("header")
        grp_play.addWidget(lbl_play)
        
        row_play = QHBoxLayout()
        row_play.addWidget(self.btn_play)
        row_play.addWidget(self.btn_step)
        grp_play.addLayout(row_play)
        grp_play.addWidget(self.btn_clear)
        sidebar.addLayout(grp_play)

        # Group: Generation
        grp_gen = QVBoxLayout()
        grp_gen.setSpacing(8)
        lbl_gen = QLabel("Generación")
        lbl_gen.setObjectName("header")
        grp_gen.addWidget(lbl_gen)
        
        row_gen = QHBoxLayout()
        row_gen.addWidget(self.btn_rand)
        row_gen.addWidget(self.btn_fill)
        grp_gen.addLayout(row_gen)
        
        sidebar.addLayout(grp_gen)

        # Group: Settings
        grp_set = QVBoxLayout()
        grp_set.setSpacing(8)
        lbl_set = QLabel("Ajustes")
        lbl_set.setObjectName("header")
        grp_set.addWidget(lbl_set)
        
        grp_set.addWidget(self.speed_label)
        grp_set.addWidget(self.speed_slider)
        
        row_checks = QHBoxLayout()
        row_checks.addWidget(self.wrap_check)
        row_checks.addWidget(self.fit_check)
        grp_set.addLayout(row_checks)
        
        sidebar.addLayout(grp_set)

        # Group: Appearance
        grp_app = QVBoxLayout()
        grp_app.setSpacing(8)
        lbl_app = QLabel("Apariencia")
        lbl_app.setObjectName("header")
        grp_app.addWidget(lbl_app)
        
        grp_app.addWidget(QLabel("Paleta"))
        grp_app.addWidget(self.palette_combo)
        grp_app.addWidget(self.dark_check)
        sidebar.addLayout(grp_app)

        # Group: Patterns
        grp_pat = QVBoxLayout()
        grp_pat.setSpacing(8)
        lbl_pat = QLabel("Patrones")
        lbl_pat.setObjectName("header")
        grp_pat.addWidget(lbl_pat)
        
        grp_pat.addWidget(self.patterns_combo)
        grp_pat.addWidget(self.btn_insert)
        sidebar.addLayout(grp_pat)

        # Footer
        sidebar.addStretch()
        sidebar.addWidget(self.btn_info)

        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("sidebar")
        self.sidebar_widget.setFixedWidth(280)
        self.sidebar_widget.setLayout(sidebar)
        
        # --- Main Area ---
        main_area_layout = QVBoxLayout()
        main_area_layout.setContentsMargins(0, 0, 0, 0)
        main_area_layout.setSpacing(0)
        main_area_layout.addWidget(self.header_widget)
        main_area_layout.addWidget(self.board, stretch=1)
        
        self.main_area = QWidget()
        self.main_area.setLayout(main_area_layout)

        # Main Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.main_area, stretch=1)
        layout.addWidget(self.sidebar_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.apply_theme()
        self.apply_styles()

    def toggle_sidebar(self):
        visible = self.sidebar_widget.isVisible()
        self.sidebar_widget.setVisible(not visible)
        self.btn_menu.setText("»" if not visible else "≡")

    def on_speed_change(self, value):
        self.delay_ms = int(value)
        if self.running:
            self.timer.setInterval(self.delay_ms)

    def on_wrap_change(self, state):
        self.wrap = state == Qt.Checked

    def on_theme_change(self, *_):
        self.current_palette = self.palette_combo.currentText()
        self.dark_mode = self.dark_check.isChecked()
        self.apply_theme()

    def on_density_change(self, value):
        self.density = int(value)

    def on_fit_change(self, state):
        self.auto_fit = state == Qt.Checked

    def apply_theme(self):
        alive = self.palettes.get(self.current_palette, "#00e676")
        bg = "#121212" if self.dark_mode else "#ffffff"
        self.board.set_colors(alive, bg)

    def apply_styles(self):
        if self.dark_mode:
            self.setStyleSheet("""
                * { font-family: 'Segoe UI', sans-serif; font-size: 12px; }
                QMainWindow { background-color: #0f1216; }
                QWidget#sidebar { background-color: #161b22; border-left: 1px solid #30363d; }
                QWidget#header_bar { background-color: #161b22; border-bottom: 1px solid #30363d; }
                QLabel#header { font-weight: bold; font-size: 13px; color: #f0f6fc; margin-top: 10px; margin-bottom: 4px; }
                QLabel#app_title { font-weight: bold; font-size: 14px; color: #f0f6fc; }
                QPushButton {
                    background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 6px 12px; border-radius: 6px;
                }
                QPushButton:hover { background: #30363d; border-color: #8b949e; }
                QPushButton:pressed { background: #161b22; }
                QPushButton#btn_menu { background: transparent; border: none; font-size: 18px; color: #c9d1d9; }
                QPushButton#btn_menu:hover { background: #30363d; }
                QSlider::groove:horizontal { height: 4px; background: #30363d; border-radius: 2px; }
                QSlider::handle:horizontal { width: 16px; height: 16px; background: #58a6ff; border-radius: 8px; margin: -6px 0; }
                QComboBox {
                    background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px; border-radius: 6px;
                }
                QCheckBox { color: #c9d1d9; spacing: 8px; }
                QLabel { color: #8b949e; }
            """)
        else:
            self.setStyleSheet("""
                * { font-family: 'Segoe UI', sans-serif; font-size: 12px; }
                QMainWindow { background-color: #ffffff; }
                QWidget#sidebar { background-color: #f6f8fa; border-left: 1px solid #d0d7de; }
                QWidget#header_bar { background-color: #f6f8fa; border-bottom: 1px solid #d0d7de; }
                QLabel#header { font-weight: bold; font-size: 13px; color: #24292f; margin-top: 10px; margin-bottom: 4px; }
                QLabel#app_title { font-weight: bold; font-size: 14px; color: #24292f; }
                QPushButton {
                    background: #f6f8fa; color: #24292f; border: 1px solid #d0d7de; padding: 6px 12px; border-radius: 6px;
                }
                QPushButton:hover { background: #f3f4f6; border-color: #0969da; }
                QPushButton:pressed { background: #ebecf0; }
                QPushButton#btn_menu { background: transparent; border: none; font-size: 18px; color: #57606a; }
                QPushButton#btn_menu:hover { background: #ebecf0; }
                QSlider::groove:horizontal { height: 4px; background: #d0d7de; border-radius: 2px; }
                QSlider::handle:horizontal { width: 16px; height: 16px; background: #0969da; border-radius: 8px; margin: -6px 0; }
                QComboBox {
                    background: #ffffff; color: #24292f; border: 1px solid #d0d7de; padding: 4px; border-radius: 6px;
                }
                QCheckBox { color: #24292f; spacing: 8px; }
                QLabel { color: #57606a; }
            """)
    def toggle_run(self):
        self.running = not self.running
        self.btn_play.setText("Pausar" if self.running else "Iniciar")
        if self.running:
            self.timer.start(self.delay_ms)
        else:
            self.timer.stop()

    def clear(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 0
        self.board.update()

    def randomize(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 1 if random.random() < 0.2 else 0
        self.board.update()

    def fill_all(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 1
        self.board.update()

    def step_once(self):
        self.grid = self.next_state(self.grid)
        self.board.grid = self.grid
        self.board.update()

    def tick(self):
        self.grid = self.next_state(self.grid)
        self.board.grid = self.grid
        self.board.update()

    def next_state(self, grid):
        rows = self.rows
        cols = self.cols
        new_grid = [[0 for _ in range(cols)] for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                n = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        rr = r + dr
                        cc = c + dc
                        if self.wrap:
                            rr = (rr + rows) % rows
                            cc = (cc + cols) % cols
                            n += grid[rr][cc]
                        else:
                            if 0 <= rr < rows and 0 <= cc < cols:
                                n += grid[rr][cc]
                if grid[r][c] == 1:
                    new_grid[r][c] = 1 if n == 2 or n == 3 else 0
                else:
                    new_grid[r][c] = 1 if n == 3 else 0
        return new_grid

    def pattern_offsets(self, strings):
        offs = []
        for r, row in enumerate(strings):
            for c, ch in enumerate(row):
                if ch == "#":
                    offs.append((r, c))
        return offs

    def insert_selected_pattern(self):
        name = self.patterns_combo.currentText()
        strings = self.patterns.get(name)
        if strings:
            self.insert_pattern_center(strings)

    def insert_pattern_center(self, strings):
        offs = self.pattern_offsets(strings)
        ph = len(strings)
        pw = len(strings[0])
        cr = self.rows // 2 - ph // 2
        cc = self.cols // 2 - pw // 2
        for dr, dc in offs:
            rr = cr + dr
            cc2 = cc + dc
            if self.wrap:
                rr = (rr + self.rows) % self.rows
                cc2 = (cc2 + self.cols) % self.cols
                self.grid[rr][cc2] = 1
            else:
                if 0 <= rr < self.rows and 0 <= cc2 < self.cols:
                    self.grid[rr][cc2] = 1
        self.board.update()

    def info_text(self):
        return (
            "Juego de la Vida de Conway\n\n"
            "Descripción:\n"
            "Autómata celular en un tablero bidimensional de celdas que pueden estar vivas o muertas. "
            "Cada generación se calcula aplicando las mismas reglas a todas las celdas.\n\n"
            "Reglas:\n"
            "1) Supervivencia: una célula viva con 2 o 3 vecinas vivas sigue viva.\n"
            "2) Nacimiento: una célula muerta con exactamente 3 vecinas vivas nace.\n"
            "3) En otros casos, la célula muere o permanece muerta.\n\n"
            "Vecindario:\n"
            "Se usa el vecindario de Moore (8 vecinos alrededor). Con 'Envoltura' activada, los bordes "
            "se conectan como en un toro: el tablero no tiene límites.\n\n"
            "Patrones clásicos:\n"
            "- Estables: Block, Boat, Loaf, Tub.\n"
            "- Osciladores: Blinker, Toad, Beacon, Pulsar.\n"
            "- Naves espaciales: Glider, Lightweight Spaceship (LWSS).\n"
            "- Otros: Pentomino R. Existen generadores como el Gosper Glider Gun.\n\n"
            "Controles:\n"
            "- Iniciar/Pausar, Paso, Limpiar, Aleatorio, Velocidad (ms).\n"
            "- Envoltura: bordes toroidales.\n"
            "- Paleta y Oscuro: personaliza colores.\n"
            "- Patrones: selecciona e inserta centrado.\n\n"
            "Créditos:\n"
            "Creado por John H. Conway. Es un sistema determinista con comportamiento emergente muy "
            "estudiado en matemáticas y ciencias de la computación.\n"
        )

    def show_info(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Información")
        text = QTextEdit(dlg)
        text.setReadOnly(True)
        text.setPlainText(self.info_text())
        if self.dark_mode:
            text.setStyleSheet("QTextEdit { background: #121212; color: #e0e0e0; }")
        else:
            text.setStyleSheet("QTextEdit { background: #ffffff; color: #000000; }")
        scroll = QScrollArea(dlg)
        content = QWidget()
        v = QVBoxLayout()
        alive = self.palettes.get(self.current_palette, "#00e676")
        bg = "#121212" if self.dark_mode else "#ffffff"
        for name, strings in self.patterns.items():
            name_lbl = QLabel(name)
            if self.dark_mode:
                name_lbl.setStyleSheet("QLabel { color: #e0e0e0; }")
            preview = PatternPreview(strings, cell_size=12, alive_color=alive, bg_color=bg)
            v.addWidget(name_lbl)
            v.addWidget(preview)
        content.setLayout(v)
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        buttons = QDialogButtonBox(QDialogButtonBox.Close, parent=dlg)
        buttons.rejected.connect(dlg.reject)
        layout = QVBoxLayout()
        layout.addWidget(text)
        layout.addWidget(scroll)
        layout.addWidget(buttons)
        dlg.setLayout(layout)
        dlg.resize(700, 700)
        dlg.exec()
    
    def show_resize_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Definir tablero")
        rows_spin = QSpinBox(dlg)
        cols_spin = QSpinBox(dlg)
        size_spin = QSpinBox(dlg)
        preserve_check = QCheckBox("Conservar contenido", dlg)
        rows_spin.setRange(10, 500)
        cols_spin.setRange(10, 500)
        size_spin.setRange(4, 40)
        rows_spin.setValue(self.rows)
        cols_spin.setValue(self.cols)
        size_spin.setValue(self.cell_size)
        preserve_check.setChecked(True)
        form = QFormLayout()
        form.addRow("Filas", rows_spin)
        form.addRow("Columnas", cols_spin)
        form.addRow("Tamaño celda (px)", size_spin)
        form.addRow(preserve_check)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=dlg)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        v = QVBoxLayout()
        v.addLayout(form)
        v.addWidget(buttons)
        dlg.setLayout(v)
        if dlg.exec():
            r = int(rows_spin.value())
            c = int(cols_spin.value())
            s = int(size_spin.value())
            self.apply_resize(r, c, s, preserve=preserve_check.isChecked())

    def apply_resize(self, rows, cols, cell_size, preserve=True):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        if preserve:
            old = self.grid
            old_rows = len(old)
            old_cols = len(old[0]) if old_rows else 0
            new_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
            sr = max(0, (self.rows - old_rows) // 2)
            sc = max(0, (self.cols - old_cols) // 2)
            for r in range(old_rows):
                for c in range(old_cols):
                    rr = r + sr
                    cc = c + sc
                    if 0 <= rr < self.rows and 0 <= cc < self.cols:
                        new_grid[rr][cc] = old[r][c]
            self.grid = new_grid
        else:
            self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.board.update_grid(self.grid, self.cell_size)
        self.resize(self.board.width() + 20, self.board.height() + 100)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.auto_fit:
            return
        
        # Available space for board is roughly current board size
        # But we need to be careful not to shrink indefinitely
        # Using self.board.width() is safe because it's managed by layout
        board_w = self.board.width()
        board_h = self.board.height()
        
        if board_w <= 0 or board_h <= 0:
            return

        new_cell = max(1, int(min(board_w / self.cols, board_h / self.rows)))
        if new_cell != self.cell_size:
            self.cell_size = new_cell
            self.board.update_grid(self.grid, self.cell_size)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=50)
    parser.add_argument("--cols", type=int, default=80)
    parser.add_argument("--cell-size", type=int, default=12)
    args = parser.parse_args()

    app = QApplication([])
    w = GameOfLifeWindow(rows=args.rows, cols=args.cols, cell_size=args.cell_size)
    w.resize(w.board.width() + 20, w.board.height() + 100)
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
