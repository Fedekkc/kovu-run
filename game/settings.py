"""Constantes compartidas. El resto de los módulos importa de acá."""

WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "Kovu Run"
# Un pixel del arte ocupa ART_PIXEL x ART_PIXEL en pantalla.
ART_PIXEL = 4
# La grilla del mundo: con 2 se ve a 640x360, así lo lejano conserva detalle.
PIXEL = 2

# Proyección 2.5D. z=0 está en los pies del jugador; z grande está en el horizonte.
HORIZON_Y = 248
GROUND_Y = 700
NEAR = 9.0
LANE_SPREAD = 390
FAR_Z = 150.0
SPAWN_Z = 132.0
DESPAWN_Z = -10.0
PLAYER_DRAW_Z = 2.5

# Ritmo
BASE_SPEED = 34.0
MAX_SPEED = 82.0
ACCEL_PER_METER = 0.018
# Jugador
LANE_SWITCH = 0.13
JUMP_TIME = 0.64
SLIDE_TIME = 0.52

# Puntaje (ranking). La alcancía mejora cuántas galletas van a la cuenta.
BISCUIT_POINTS = 25
PICKUP_SPAN = 1.0
LUCK_WEIGHT = 0
BANK_RATE = 0.0

# Tipos de obstáculo. Chocarlos sin esquivarlos termina la partida.
LOW = "low"    # se salta
HIGH = "high"  # se esquiva agachándose
FULL = "full"  # hay que cambiar de carril
WAGON = "wagon"  # se trepa y se corre un tramo elevado

# Recogibles
BISCUIT = "biscuit"
ROCKET = "rocket"
SUPER_JUMP = "super_jump"
DOUBLE_JUMP = "double_jump"

ROCKET_TIME = 3.6
ROCKET_SPEED = 1.45
# Tiempo en el aire del salto potenciado (arco).
SUPER_JUMP_TIME = 0.86
SUPER_JUMP_SCALE = 1.6
DOUBLE_JUMP_TIME = 0.8
DOUBLE_JUMP_SCALE = 1.95
# Ventana para usar el poder después de agarrarlo (no es el vuelo).
SUPER_HOLD = 3.6
DOUBLE_HOLD = 3.6

RANKING_LIMIT = 10
