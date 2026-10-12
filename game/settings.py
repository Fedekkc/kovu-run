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

# Ritmo: arranque legible, techo alto y lejos (la partida sigue escalando).
BASE_SPEED = 30.0
MAX_SPEED = 94.0
ACCEL_PER_METER = 0.010
LATE_SPEED_FROM = 2800.0
LATE_ACCEL_PER_METER = 0.006
# Jugador
LANE_SWITCH = 0.18
JUMP_TIME = 0.64
SLIDE_TIME = 0.52

# Puntaje. El combo es exclusivo; el calor de distancia hace que “llegar lejos” pague.
BISCUIT_POINTS = 20
COMBO_WINDOW = 2.4
COMBO_MAX = 3
COMBO_X2_AT = 8
COMBO_X3_AT = 15
# Calor de score por metros (interpolado). Multiplica la distancia en el marcador.
HEAT_KEYS = (
    (0.0, 1.0),
    (500.0, 1.1),
    (1000.0, 1.25),
    (2000.0, 1.5),
    (3500.0, 1.85),
    (5000.0, 2.25),
    (7500.0, 2.75),
    (10000.0, 3.0),
)
PICKUP_SPAN = 1.0
LUCK_WEIGHT = 0
BANK_RATE = 0.0

# Medallas de distancia (metros). Solo bragging rights.
MEDAL_THRESHOLDS = (
    ("barrio", 500),
    ("avenida", 1000),
    ("autopista", 2000),
    ("leyenda", 5000),
)

# Tipos de obstáculo. Chocarlos sin esquivarlos termina la partida.
LOW = "low"  # se salta
HIGH = "high"  # se esquiva agachándose
FULL = "full"  # hay que cambiar de carril
WAGON = "wagon"  # se trepa y se corre un tramo elevado

# Recogibles
BISCUIT = "biscuit"
ROCKET = "rocket"
SUPER_JUMP = "super_jump"
DOUBLE_JUMP = "double_jump"

ROCKET_TIME = 2.8
ROCKET_SPEED = 1.28
SUPER_JUMP_TIME = 0.86
SUPER_JUMP_SCALE = 1.45
DOUBLE_JUMP_TIME = 0.8
DOUBLE_JUMP_SCALE = 1.75
SUPER_HOLD = 2.8
DOUBLE_HOLD = 2.8

RANKING_LIMIT = 10

# Modos de partida
MODE_NORMAL = "normal"
MODE_LAVA = "lava"


def combo_mult_for(streak: int) -> int:
    if streak >= COMBO_X3_AT:
        return COMBO_MAX
    if streak >= COMBO_X2_AT:
        return 2
    return 1


def heat_at(distance: float) -> float:
    """Multiplicador de metros en el score; crece con la profundidad de la corrida."""
    if distance <= HEAT_KEYS[0][0]:
        return HEAT_KEYS[0][1]
    for (start, low), (end, high) in zip(HEAT_KEYS, HEAT_KEYS[1:]):
        if distance <= end:
            span = end - start
            t = 0.0 if span <= 0.0 else (distance - start) / span
            return low + (high - low) * t
    return HEAT_KEYS[-1][1]
