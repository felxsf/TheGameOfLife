# Juego de la Vida de Conway (PySide6)

Aplicación interactiva del Juego de la Vida con interfaz moderna usando PySide6 (Qt).

## Requisitos
- Python 3.9+ en Windows
- Dependencias de Python: ver [requirements.txt](file:///c:/Users/felix.sanchez/Documents/trae_projects/TheGameOfLife/requirements.txt)

## Instalación (con entorno virtual recomendado)
1. Crear entorno virtual:
   ```powershell
   python -m venv .venv
   ```
2. Activar el entorno (PowerShell):
   ```powershell
   & ".\.venv\Scripts\Activate.ps1"
   ```
3. Instalar dependencias:
   ```powershell
   & ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
   ```

## Ejecución
```powershell
& ".\.venv\Scripts\python.exe" ".\main.py"
```
Archivo principal: [main.py](file:///c:/Users/felix.sanchez/Documents/trae_projects/TheGameOfLife/main.py)

### Parámetros por línea de comandos
- Ajusta tamaño del tablero al iniciar:
  ```powershell
  & ".\.venv\Scripts\python.exe" ".\main.py" --rows 80 --cols 120 --cell-size 10
  ```
  - `--rows`: número de filas (default 50)
  - `--cols`: número de columnas (default 80)
  - `--cell-size`: tamaño de cada celda en píxeles (default 12)

## Controles
- Iniciar/Pausar: botón “Iniciar/Pausar”
- Paso: avanza una generación
- Limpiar: borra tablero
- Aleatorio: siembra ~20% de celdas vivas
- Velocidad: ajusta intervalo en ms
- Envoltura: conecta bordes (toroidal)
- Paleta: selecciona color de celdas vivas (Verde/Azul/Magenta/Naranja)
- Oscuro: alterna fondo oscuro/claro
- Patrones: selecciona y “Insertar” para colocar centrado
- Edición: clic y arrastre para alternar celdas viva/muerta

## Patrones incluidos
- Estables: Block, Boat, Loaf, Tub
- Osciladores: Blinker, Toad, Beacon, Pulsar
- Naves espaciales: Glider, Lightweight Spaceship (LWSS)
- Otros: Pentomino R

## Reglas del Juego de la Vida
- Supervivencia: una célula viva con 2 o 3 vecinas vivas sigue viva
- Nacimiento: una célula muerta con exactamente 3 vecinas vivas nace
- En otros casos, la célula muere o permanece muerta
- Vecindario: Moore (8 vecinos). Con “Envoltura”, los bordes se conectan

## Notas técnicas
- Renderizado con QPainter sobre un widget personalizado
- Temporizador QTimer para avanzar generaciones
- Inserción de patrones desde representaciones textuales centradas en el tablero

## Problemas comunes
- “No module named 'PySide6'”: instala dependencias dentro de tu .venv  
  ```powershell
  & ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
  ```
- Si PowerShell bloquea scripts, puedes ejecutar:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```

## Próximas mejoras sugeridas
- Inserción de patrones en la posición del cursor
- Más patrones (Gosper Glider Gun, penta-decathlon)
- Zoom y ajuste del tamaño de celda/tablero

## Troubleshooting avanzado
- Cambiar tamaño del tablero:
  - Edita los parámetros en la creación de la ventana en [main.py](file:///c:/Users/felix.sanchez/Documents/trae_projects/TheGameOfLife/main.py): `rows`, `cols`, `cell_size`.
  - Ejemplo: `GameOfLifeWindow(rows=80, cols=120, cell_size=10)` para más celdas con celdas más pequeñas.
  - Si el tablero no cabe en pantalla, reduce `cell_size` o el número de filas/columnas.
- Ajustar rendimiento:
  - Aumenta el intervalo del temporizador (ms) con el deslizador para reducir la frecuencia de actualizaciones.
  - Reduce `rows`/`cols` o `cell_size`.
  - Evita sembrar demasiadas celdas vivas simultáneamente si notas lag.
  - Cierra otras aplicaciones intensivas si la GPU/CPU está ocupada.
- Actualizar PySide6:
  - En .venv: `& ".\\.venv\\Scripts\\python.exe" -m pip install --upgrade PySide6`
  - Global: `python -m pip install --upgrade PySide6`
  - Para reinstalar limpio: `pip uninstall PySide6` y luego instalar de nuevo.
- Ejecutar con el intérprete correcto:
  - Usa siempre el Python del entorno virtual si lo creaste:
    - `& ".\\.venv\\Scripts\\python.exe" ".\\main.py"`
  - Si ves “No module named 'PySide6'”, asegúrate de instalar en el mismo entorno que ejecuta la app:
    - `& ".\\.venv\\Scripts\\python.exe" -m pip install -r requirements.txt`
- PowerShell y ejecución de scripts:
  - Si aparece un error de políticas al activar el venv, usa:
    - `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
- Alta densidad de píxeles (HiDPI):
  - Si la UI se ve muy pequeña/grande, ajusta `cell_size` y/o los `rows/cols`.
  - Opcionalmente, cambia el tamaño de la ventana en `main()` tras crear la ventana:
    - `w.resize(w.board.width() + 20, w.board.height() + 100)`
