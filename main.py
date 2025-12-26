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
        self.setMinimumSize(
            len(grid[0]) * cell_size,
            len(grid) * cell_size,
        )
        self.setMouseTracking(True)

    def set_colors(self, alive_hex, bg_hex):
        self.alive_color = QColor(alive_hex)
        self.bg_color = QColor(bg_hex)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), self.bg_color)
        for r in range(len(self.grid)):
            for c in range(len(self.grid[0])):
                if self.grid[r][c] == 1:
                    x0 = c * self.cell_size
                    y0 = r * self.cell_size
                    p.fillRect(x0, y0, self.cell_size, self.cell_size, self.alive_color)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_at(event.position())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.toggle_at(event.position())

    def toggle_at(self, pos):
        c = int(pos.x()) // self.cell_size
        r = int(pos.y()) // self.cell_size
        if 0 <= r < len(self.grid) and 0 <= c < len(self.grid[0]):
            self.grid[r][c] = 0 if self.grid[r][c] == 1 else 1
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

        controls = QHBoxLayout()
        controls.addWidget(self.btn_play)
        controls.addWidget(self.btn_step)
        controls.addWidget(self.btn_clear)
        controls.addWidget(self.btn_rand)
        controls.addWidget(self.speed_label)
        controls.addWidget(self.speed_slider)
        controls.addWidget(self.wrap_check)
        controls.addWidget(QLabel("Paleta"))
        controls.addWidget(self.palette_combo)
        controls.addWidget(self.dark_check)
        controls.addWidget(self.patterns_combo)
        controls.addWidget(self.btn_insert)
        controls.addWidget(self.btn_info)

        layout = QVBoxLayout()
        layout.addWidget(self.board)
        layout.addLayout(controls)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.apply_theme()

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

    def apply_theme(self):
        alive = self.palettes.get(self.current_palette, "#00e676")
        bg = "#121212" if self.dark_mode else "#ffffff"
        self.board.set_colors(alive, bg)

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


def main():
    app = QApplication([])
    w = GameOfLifeWindow(rows=50, cols=80, cell_size=12)
    w.resize(w.board.width() + 20, w.board.height() + 100)
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
