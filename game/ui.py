"""Pantallas arcade de Kovu Run: marquesina, marcador, ranking y menús.

Todo se dibuja encima del demo o de la carrera; acá no hay fondo propio.
"""

from __future__ import annotations

from collections.abc import Sequence

import pygame

from game.accounts import NAME_MAX, Account
from game.dao import RankingEntry
from game.hits import Action, Hits
from game.options import COPY_LANG_ES, VOLUME_MAX, Options
from game.palette import Tone, tone
from game.pixelfont import default_font
from game.settings import BISCUIT, HEIGHT, TITLE, WIDTH
from game.sprites import MENU_KOVU, blit_feet, default_book
from game.telemetry import DayStats
from game.upgrades import UpgradeLine

COPY_TAGLINE = "Corré, saltá y que no te alcance"
COPY_LANE = "← → o A D  carril"
COPY_JUMP = "↑ W o espacio  saltar / subir"
COPY_SLIDE = "↓ o S  agacharse"
COPY_START = "Enter  jugar"
COPY_CREATE_LINE = "Enter  crear cuenta"
COPY_ACCOUNT_KEY = "C  cuentas"
COPY_UPGRADES_KEY = "U  mejoras"
COPY_OPTIONS_KEY = "O  opciones"
COPY_QUIT = "Esc  salir"
COPY_CONTROLS = "Controles"
COPY_BTN_PLAY = "Jugar"
COPY_BTN_LAVA = "El piso es lava"
COPY_BTN_CREATE = "Crear cuenta"
COPY_BTN_ACCOUNTS = "Cuentas"
COPY_BTN_UPGRADES = "Mejoras"
COPY_BTN_OPTIONS = "Opciones"
COPY_BTN_QUIT = "Salir"
COPY_LAVA_KEY = "L  el piso es lava"
COPY_COMBO = "x{mult}"
COPY_COMBO_MAX = "Combo máx x{mult}"
COPY_COMBO_NEXT = "{have}/{need}"
COPY_HEAT = "calor x{heat}"
COPY_MEDALS = "Medallas: {names}"
COPY_NO_MEDALS = "Sin medallas aún"
COPY_LAVA_HINT = "Solo trenes · no toques el piso"
COPY_BTN_BACK = "Volver"
COPY_BTN_NEW = "Nueva"
COPY_BTN_USE = "Usar"
COPY_BTN_BUY = "Comprar"
COPY_BTN_CONFIRM = "Confirmar"
COPY_BTN_RETRY = "Reintentar"
COPY_BTN_MENU = "Menú"
COPY_BTN_CREDITS = "Créditos"
COPY_BTN_MINUS = "-"
COPY_BTN_PLUS = "+"
BTN_H = 48
BTN_GAP = 12
COPY_OPTIONS_TITLE = "Opciones"
COPY_OPTIONS_HINT = "↑ ↓ elegir · ← → cambiar · Enter · Esc volver · F11 pantalla"
COPY_VOLUME = "Volumen"
COPY_FULLSCREEN = "Pantalla completa"
COPY_HITBOXES = "Hitboxes"
COPY_TELEMETRY = "Telemetría"
COPY_LANGUAGE = "Idioma"
COPY_CREDITS_ROW = "Créditos"
COPY_ON = "Sí"
COPY_OFF = "No"
COPY_VOLUME_BAR = "{filled}{empty} {level}"
VOLUME_FILL = "="
VOLUME_EMPTY = "-"
COPY_STATS_TODAY = "Hoy: {runs} partidas · media {average}"
COPY_STATS_EMPTY = "Hoy: sin partidas"
COPY_CREDITS_TITLE = "Créditos"
COPY_CREDITS = (
    "Kovu Run",
    "Un galgo, una viejita, muchas galletas",
    "",
    "Hecho con pygame",
    "Pixel art forjado en el barrio",
    "",
    "Esc para volver",
)
COPY_SPLASH_HINT = "Presioná Enter"
COPY_VERSION = "v0.1"
COPY_NO_ACCOUNT = "Sin cuenta"
COPY_SAVE_HINT = "C para guardar galletas"
COPY_PLAY = "Presioná Enter"
COPY_CREATE_PROMPT = "Enter para crear una cuenta"
COPY_WALLET = "{count} galletas"
COPY_UPGRADES_TITLE = "Mejoras"
COPY_UPGRADES_NOTE = "Cada carrera suma las galletas que juntaste"
COPY_UPGRADES_HINT = "↑ ↓ elegir · Enter comprar · Esc volver"
COPY_ACCOUNTS_TITLE = "Cuentas"
COPY_ACCOUNTS_EMPTY = "Todavía no hay cuentas. N para crear una"
COPY_ACCOUNTS_HINT = "↑ ↓ elegir · Enter usar · N nueva · Esc volver"
COPY_IN_USE = "En uso"
COPY_NAME_TITLE = "Nueva cuenta"
COPY_NAME_HINT = "Letras A–Z · Retroceso borra · Enter confirma · Esc cancela"
COPY_MAXED = "Al máximo"
COPY_PRICE = "{cost}"
COPY_BANKED = "+{count} galletas en la cuenta"
COPY_RECORD = "Récord: {best}"
COPY_RANKING = "Ranking"
COPY_EMPTY_RANKING = "Sé el primero"
COPY_PLACE = "Puesto {rank}"
COPY_OUTSIDE = "Fuera del ranking"
COPY_POINTS = "Puntos"
COPY_BEST = "Récord"
COPY_CAUGHT = "¡Te alcanzó!"
COPY_NEW_RECORD = "¡Nuevo récord!"
COPY_RETRY = "Enter para reintentar"
COPY_MENU = "Esc para el menú"
COPY_RANK_ROW = "{place:02d}"

SMALL = 2
MEDIUM = 3
LARGE = 4
TITLE_SCALE = 11
NAME_SCALE = 8
SCORE_SCALE = 7
CAUGHT_SCALE = 6

BORDER = 4
RIM = 2
PAD = 18
MARGIN = 36
HUD_TOP = 16
PANEL_ALPHA = 228
MENU_DIM = 70
SCREEN_DIM = 120
OVER_DIM = 140
BULB = 6
BULB_STEP = 28
BULB_RATE = 8.0
BLINK_RATE = 2.4
GALLOP_PACE = 170.0
GALLOP_MARGIN = 300
COUNT_TIME = 0.8
ICON = 32
SHOP_ICON = 40
CHARGE_W = 180
CHARGE_H = 10
RANK_ROWS = 10
ACCOUNT_ROWS = 7

TITLE_RAMP = (Tone.CREAM, Tone.SUN, Tone.CORAL, Tone.NEON_PINK)
RANK_TONES = (Tone.SUN, Tone.CREAM, Tone.CORAL)

_title_cache: dict[str, pygame.Surface] = {}


def _text(text: str, color: Tone, scale: int, shadow: bool = True) -> pygame.Surface:
    ink = tone(Tone.INK) if shadow else None
    return default_font().render(text, tone(color), scale, ink)


def _blink(time: float, rate: float = BLINK_RATE) -> bool:
    return int(time * rate * 2.0) % 2 == 0


def _dim(screen: pygame.Surface, alpha: int) -> None:
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((*tone(Tone.INK), alpha))
    screen.blit(shade, (0, 0))


def _frame(screen: pygame.Surface, rect: pygame.Rect, edge: Tone = Tone.MAUVE) -> None:
    """A pixel panel: ink border, a thin coloured rim and clipped corners."""
    card = pygame.Surface(rect.size, pygame.SRCALPHA)
    card.fill((*tone(Tone.PLUM_DARK), PANEL_ALPHA))
    pygame.draw.rect(card, tone(Tone.INK), card.get_rect(), BORDER)
    pygame.draw.rect(card, tone(edge), card.get_rect().inflate(-BORDER * 2, -BORDER * 2), RIM)
    clear = (0, 0, 0, 0)
    w, h = rect.size
    for x, y in ((0, 0), (w - BORDER, 0), (0, h - BORDER), (w - BORDER, h - BORDER)):
        card.fill(clear, (x, y, BORDER, BORDER))
    screen.blit(card, rect.topleft)


def _highlight(screen: pygame.Surface, rect: pygame.Rect) -> None:
    glow = pygame.Surface(rect.size, pygame.SRCALPHA)
    glow.fill((*tone(Tone.SUN), 44))
    screen.blit(glow, rect.topleft)
    arrow = _text("→", Tone.SUN, MEDIUM)
    screen.blit(arrow, arrow.get_rect(midright=(rect.left - 6, rect.centery)))


def _icon(slot: str, height: int, time: float = 0.0) -> pygame.Surface | None:
    stamp = default_book().stamp(slot, time)
    if stamp is None or stamp.image.get_height() <= 0:
        return None
    bounds = stamp.image.get_bounding_rect(min_alpha=1)
    if bounds.height <= 0:
        return None
    trimmed = stamp.image.subsurface(bounds)
    width = max(1, round(bounds.width * height / bounds.height))
    resize = pygame.transform.smoothscale if stamp.smooth else pygame.transform.scale
    return resize(trimmed, (width, height))


def _stack(screen: pygame.Surface, images: Sequence[pygame.Surface], x: int, y: int, gap: int) -> int:
    for image in images:
        screen.blit(image, (x, y))
        y += image.get_height() + gap
    return y


def _wallet(screen: pygame.Surface, count: int, x: int, y: int, scale: int) -> int:
    """Biscuit icon and count; returns the right edge."""
    label = _text(COPY_WALLET.format(count=count), Tone.CREAM, scale)
    icon = _icon(BISCUIT, label.get_height())
    if icon is not None:
        screen.blit(icon, (x, y))
        x += icon.get_width() + 8
    screen.blit(label, (x, y))
    return x + label.get_width()


def _title(scale: int) -> pygame.Surface:
    key = f"{TITLE}:{scale}"
    cached = _title_cache.get(key)
    if cached is not None:
        return cached
    font = default_font()
    mask = font.mask(TITLE, scale)
    ramp = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
    rows = mask.get_height()
    bands = len(TITLE_RAMP) - 1
    for y in range(rows):
        t = y / max(1, rows - 1) * bands
        index = min(bands - 1, int(t))
        start, end = tone(TITLE_RAMP[index]), tone(TITLE_RAMP[index + 1])
        local = t - index
        color = tuple(int(a + (b - a) * local) for a, b in zip(start, end))
        ramp.fill((*color, 255), (0, y, mask.get_width(), 1))
    lit = mask.copy()
    lit.blit(ramp, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    edge = font.render(TITLE, tone(Tone.INK), scale)
    drop = font.render(TITLE, tone(Tone.PLUM), scale)
    pad = scale
    image = pygame.Surface((mask.get_width() + pad * 3, mask.get_height() + pad * 3), pygame.SRCALPHA)
    image.blit(drop, (pad * 2, pad * 2))
    for dx, dy in ((0, pad), (pad * 2, pad), (pad, 0), (pad, pad * 2)):
        image.blit(edge, (dx, dy))
    image.blit(lit, (pad, pad))
    _title_cache[key] = image
    return image


def _marquee(screen: pygame.Surface, time: float) -> pygame.Rect:
    title = _title(TITLE_SCALE)
    rect = title.get_rect(midtop=(WIDTH // 2, 28)).inflate(PAD * 3, PAD * 2)
    _frame(screen, rect, Tone.SUN)
    screen.blit(title, title.get_rect(center=rect.center))
    tick = int(time * BULB_RATE)
    spots = [(x, rect.top + BORDER) for x in range(rect.left + BULB_STEP // 2, rect.right, BULB_STEP)]
    spots += [(x, rect.bottom - BORDER - BULB) for x in range(rect.left + BULB_STEP // 2, rect.right, BULB_STEP)]
    for index, (x, y) in enumerate(spots):
        lit = (index + tick) % 2 == 0
        screen.fill(tone(Tone.SUN if lit else Tone.BRICK_DARK), (x, y, BULB, BULB))
        if lit:
            screen.fill(tone(Tone.CREAM), (x + 2, y + 2, 2, 2))
    tag = _text(COPY_TAGLINE, Tone.CREAM, SMALL)
    screen.blit(tag, tag.get_rect(midtop=(WIDTH // 2, rect.bottom + 10)))
    return rect


def _ranking(screen: pygame.Surface, entries: Sequence[RankingEntry], top: int) -> None:
    header = _text(COPY_RANKING, Tone.SUN, MEDIUM)
    shown = list(entries[:RANK_ROWS])
    row_h = default_font().height * SMALL + 8
    width = 360
    height = PAD * 2 + header.get_height() + 12 + row_h * max(1, len(shown))
    rect = pygame.Rect(MARGIN, top, width, height)
    _frame(screen, rect)
    screen.blit(header, (rect.left + PAD, rect.top + PAD))
    y = rect.top + PAD + header.get_height() + 12
    if not shown:
        screen.blit(_text(COPY_EMPTY_RANKING, Tone.WALK_LIGHT, SMALL), (rect.left + PAD, y))
        return
    for place, entry in enumerate(shown, start=1):
        color = RANK_TONES[place - 1] if place <= len(RANK_TONES) else Tone.WALK_LIGHT
        screen.blit(_text(COPY_RANK_ROW.format(place=place), color, SMALL), (rect.left + PAD, y))
        screen.blit(_text(entry.name, color, SMALL), (rect.left + PAD + 56, y))
        points = _text(str(entry.score), color, SMALL)
        screen.blit(points, points.get_rect(topright=(rect.right - PAD, y)))
        y += row_h


def _account_card(
    screen: pygame.Surface,
    name: str | None,
    wallet: int,
    top: int,
    medals: Sequence[str] | None = None,
) -> pygame.Rect:
    title = _text(name if name else COPY_NO_ACCOUNT, Tone.SUN, MEDIUM)
    line_h = default_font().height * SMALL
    extra = line_h + 6 if name and medals is not None else 0
    width = 340
    rect = pygame.Rect(0, top, width, PAD * 2 + title.get_height() + 10 + line_h + extra)
    rect.right = WIDTH - MARGIN
    _frame(screen, rect, Tone.SUN if name else Tone.MAUVE)
    screen.blit(title, (rect.left + PAD, rect.top + PAD))
    y = rect.top + PAD + title.get_height() + 10
    if name:
        _wallet(screen, wallet, rect.left + PAD, y, SMALL)
        y += line_h + 6
        if medals is not None:
            from game.medals import label_for

            if medals:
                short = ", ".join(label_for(item).split(" (")[0] for item in medals[:3])
                line = COPY_MEDALS.format(names=short)
            else:
                line = COPY_NO_MEDALS
            screen.blit(_text(line, Tone.WALK_LIGHT, SMALL), (rect.left + PAD, y))
    else:
        screen.blit(_text(COPY_SAVE_HINT, Tone.WALK_LIGHT, SMALL), (rect.left + PAD, y))
    return rect


def _button(
    screen: pygame.Surface,
    hits: Hits,
    action: Action,
    label: str,
    rect: pygame.Rect,
    accent: Tone = Tone.SUN,
    index: int = 0,
    delta: int = 0,
) -> None:
    _frame(screen, rect, accent)
    image = _text(label, Tone.CREAM, MEDIUM)
    screen.blit(image, image.get_rect(center=rect.center))
    hits.add(action, rect, index, delta)


def _menu_buttons(screen: pygame.Surface, top: int, has_account: bool) -> Hits:
    hits = Hits()
    width = 340
    left = WIDTH - MARGIN - width
    y = top
    primary = COPY_BTN_PLAY if has_account else COPY_BTN_CREATE
    _button(screen, hits, Action.PLAY, primary, pygame.Rect(left, y, width, BTN_H), Tone.SUN)
    y += BTN_H + BTN_GAP
    if has_account:
        _button(screen, hits, Action.LAVA, COPY_BTN_LAVA, pygame.Rect(left, y, width, BTN_H), Tone.CORAL)
        y += BTN_H + BTN_GAP
    for label, action, accent in (
        (COPY_BTN_ACCOUNTS, Action.ACCOUNTS, Tone.MAUVE),
        (COPY_BTN_UPGRADES, Action.UPGRADES, Tone.MAUVE),
        (COPY_BTN_OPTIONS, Action.OPTIONS, Tone.MAUVE),
        (COPY_BTN_QUIT, Action.QUIT, Tone.PLUM),
    ):
        _button(screen, hits, action, label, pygame.Rect(left, y, width, BTN_H), accent)
        y += BTN_H + BTN_GAP
    keys = _text(COPY_CONTROLS, Tone.SUN, SMALL)
    screen.blit(keys, (left, y + 8))
    tip = _text(f"{COPY_LANE} · {COPY_JUMP}", Tone.WALK_LIGHT, SMALL)
    screen.blit(tip, (left, y + 8 + keys.get_height() + 6))
    if has_account:
        lava_tip = _text(COPY_LAVA_KEY, Tone.WALK_LIGHT, SMALL)
        screen.blit(lava_tip, (left, y + 8 + keys.get_height() + tip.get_height() + 12))
    return hits


def _gallop(screen: pygame.Surface, time: float) -> None:
    stamp = default_book().stamp(MENU_KOVU, time)
    if stamp is None:
        return
    span = WIDTH + GALLOP_MARGIN * 2
    x = (time * GALLOP_PACE) % span - GALLOP_MARGIN
    blit_feet(screen, stamp.image, x, HEIGHT - 6, stamp.scale, stamp.smooth)


def _prompt(screen: pygame.Surface, time: float, label: str, y: int) -> None:
    if not _blink(time):
        return
    image = _text(label, Tone.SUN, LARGE)
    screen.blit(image, image.get_rect(center=(WIDTH // 2, y)))


def draw_menu(
    screen: pygame.Surface,
    entries: Sequence[RankingEntry],
    time: float,
    account_name: str | None = None,
    wallet: int = 0,
    medals: Sequence[str] | None = None,
) -> Hits:
    _dim(screen, MENU_DIM)
    marquee = _marquee(screen, time)
    top = marquee.bottom + 48
    _ranking(screen, entries, top)
    card = _account_card(screen, account_name, wallet, top, medals)
    hits = _menu_buttons(screen, card.bottom + 12, account_name is not None)
    hits.add(Action.ACCOUNTS, card)
    _gallop(screen, time)
    _prompt(screen, time, COPY_PLAY if account_name else COPY_CREATE_PROMPT, HEIGHT - 200)
    return hits


def draw_hud(
    screen: pygame.Surface,
    score: int,
    best: int,
    biscuits: int,
    power: str = "",
    charge: float = 0.0,
    combo: int = 1,
    toast_title: str = "",
    toast_line: str = "",
    heat: float = 1.0,
    combo_streak: int = 0,
    combo_next: int = 0,
) -> None:
    label = _text(COPY_POINTS, Tone.SUN, SMALL)
    value = _text(str(score), Tone.CREAM, LARGE)
    rows: list[pygame.Surface] = [label, value]
    if heat >= 1.05:
        rows.append(_text(COPY_HEAT.format(heat=f"{heat:.2f}".rstrip("0").rstrip(".")), Tone.NEON_CYAN, SMALL))
    width = max(row.get_width() for row in rows) + PAD * 2
    height = sum(row.get_height() for row in rows) + 6 * (len(rows) - 1) + PAD * 2
    rect = pygame.Rect(16, HUD_TOP, max(160, width), height)
    _frame(screen, rect)
    _stack(screen, rows, rect.left + PAD, rect.top + PAD, 6)

    best_label = _text(COPY_BEST, Tone.SUN, SMALL)
    best_value = _text(str(best), Tone.CREAM, LARGE)
    count = _text(str(biscuits), Tone.CREAM, LARGE)
    icon = _icon(BISCUIT, count.get_height())
    icon_w = 0 if icon is None else icon.get_width() + 8
    combo_img = None
    combo_w = 0
    if combo > 1:
        combo_img = _text(COPY_COMBO.format(mult=combo), Tone.CORAL, LARGE)
        combo_w = combo_img.get_width() + 16
    elif combo_next > 0 and combo_streak > 0:
        combo_img = _text(COPY_COMBO_NEXT.format(have=combo_streak, need=combo_next), Tone.WALK_LIGHT, MEDIUM)
        combo_w = combo_img.get_width() + 16
    text_w = max(best_label.get_width(), best_value.get_width())
    width = PAD + text_w + 28 + icon_w + count.get_width() + combo_w + PAD
    rect = pygame.Rect(0, HUD_TOP, width, PAD * 2 + best_label.get_height() + 6 + best_value.get_height())
    rect.right = WIDTH - 16
    _frame(screen, rect)
    _stack(screen, (best_label, best_value), rect.left + PAD, rect.top + PAD, 6)
    x = rect.left + PAD + text_w + 28
    y = rect.bottom - PAD - count.get_height()
    if icon is not None:
        screen.blit(icon, (x, y))
    screen.blit(count, (x + icon_w, y))
    if combo_img is not None:
        screen.blit(combo_img, (x + icon_w + count.get_width() + 12, y))
    if power:
        _power(screen, power, charge)
    if toast_title or toast_line:
        _story_toast(screen, toast_title, toast_line)


def _story_toast(screen: pygame.Surface, title: str, line: str) -> None:
    rows: list[pygame.Surface] = []
    if title:
        rows.append(_text(title, Tone.SUN, MEDIUM))
    if line:
        rows.append(_text(line, Tone.CREAM, SMALL))
    if not rows:
        return
    width = max(row.get_width() for row in rows) + PAD * 2
    height = sum(row.get_height() for row in rows) + 8 * (len(rows) - 1) + PAD * 2
    rect = pygame.Rect(0, HEIGHT - 120, min(WIDTH - 48, width), height)
    rect.centerx = WIDTH // 2
    _frame(screen, rect, Tone.MAUVE)
    y = rect.top + PAD
    for row in rows:
        screen.blit(row, row.get_rect(midtop=(rect.centerx, y)))
        y += row.get_height() + 8


def _power(screen: pygame.Surface, power: str, charge: float) -> None:
    label = _text(power, Tone.SUN, MEDIUM)
    bar_h = CHARGE_H + 10 if charge > 0.0 else 0
    width = max(label.get_width(), CHARGE_W if charge > 0.0 else 0) + PAD * 2
    rect = pygame.Rect(0, HUD_TOP, width, PAD * 2 + label.get_height() + bar_h)
    rect.centerx = WIDTH // 2
    _frame(screen, rect, Tone.SUN)
    screen.blit(label, label.get_rect(midtop=(rect.centerx, rect.top + PAD)))
    if charge <= 0.0:
        return
    bar = pygame.Rect(0, rect.top + PAD + label.get_height() + 10, CHARGE_W, CHARGE_H)
    bar.centerx = rect.centerx
    screen.fill(tone(Tone.INK), bar.inflate(4, 4))
    screen.fill(tone(Tone.PLUM), bar)
    fill = bar.copy()
    fill.width = max(2, int(bar.width * charge) // 2 * 2)
    screen.fill(tone(Tone.CORAL), fill)
    screen.fill(tone(Tone.SUN), (fill.left, fill.top, fill.width, 2))


def draw_game_over(
    screen: pygame.Surface,
    score: int,
    best: int,
    rank: int,
    banked: int = 0,
    since: float = COUNT_TIME,
    combo_max: int = 1,
    new_medals: Sequence[str] | None = None,
    lava: bool = False,
) -> Hits:
    hits = Hits()
    _dim(screen, OVER_DIM)
    counted = int(score * min(1.0, max(0.0, since) / COUNT_TIME))
    rows: list[pygame.Surface | None] = [
        _text(COPY_CAUGHT, Tone.NEON_PINK, CAUGHT_SCALE),
        _text(str(counted), Tone.CREAM, SCORE_SCALE),
    ]
    if lava:
        rows.append(_text(COPY_LAVA_HINT, Tone.CORAL, SMALL))
    if rank == 1:
        rows.append(_text(COPY_NEW_RECORD, Tone.SUN, MEDIUM) if _blink(since) else None)
    elif rank > 1:
        rows.append(_text(COPY_PLACE.format(rank=rank), Tone.SUN, MEDIUM))
    else:
        rows.append(_text(COPY_OUTSIDE, Tone.WALK_LIGHT, MEDIUM))
        rows.append(_text(COPY_RECORD.format(best=best), Tone.WALK_LIGHT, SMALL))
    if combo_max > 1:
        rows.append(_text(COPY_COMBO_MAX.format(mult=combo_max), Tone.CORAL, SMALL))
    if new_medals:
        from game.medals import label_for

        rows.append(
            _text(COPY_MEDALS.format(names=", ".join(label_for(m) for m in new_medals)), Tone.SUN, SMALL)
        )
    if banked > 0:
        rows.append(_text(COPY_BANKED.format(count=banked), Tone.SUN, SMALL))
    blank = default_font().height * MEDIUM
    heights = [blank if row is None else row.get_height() for row in rows]
    widths = [0 if row is None else row.get_width() for row in rows]
    gap = 14
    btn_block = BTN_H + BTN_GAP + BTN_H
    rect = pygame.Rect(
        0,
        0,
        max(560, max(widths) + PAD * 4),
        sum(heights) + gap * (len(rows) - 1) + PAD * 3 + btn_block,
    )
    rect.center = (WIDTH // 2, HEIGHT // 2)
    _frame(screen, rect, Tone.NEON_PINK)
    y = rect.top + PAD + PAD // 2
    for row, height in zip(rows, heights):
        if row is not None:
            screen.blit(row, row.get_rect(midtop=(rect.centerx, y)))
        y += height + gap
    btn_w = 220
    retry = pygame.Rect(0, y + 4, btn_w, BTN_H)
    retry.centerx = rect.centerx - btn_w // 2 - 8
    menu = pygame.Rect(0, y + 4, btn_w, BTN_H)
    menu.centerx = rect.centerx + btn_w // 2 + 8
    _button(screen, hits, Action.RETRY, COPY_BTN_RETRY, retry, Tone.SUN)
    _button(screen, hits, Action.BACK, COPY_BTN_MENU, menu, Tone.MAUVE)
    return hits


def _screen_title(screen: pygame.Surface, label: str, y: int) -> int:
    title = _text(label, Tone.SUN, LARGE + 1)
    screen.blit(title, title.get_rect(midtop=(WIDTH // 2, y)))
    return y + title.get_height()


def _hint(screen: pygame.Surface, lines: Sequence[pygame.Surface], top: int) -> None:
    width = max(line.get_width() for line in lines) + PAD * 2
    height = sum(line.get_height() for line in lines) + 8 * (len(lines) - 1) + PAD * 2
    rect = pygame.Rect(0, top, width, height)
    rect.centerx = WIDTH // 2
    _frame(screen, rect)
    y = rect.top + PAD
    for line in lines:
        screen.blit(line, line.get_rect(midtop=(rect.centerx, y)))
        y += line.get_height() + 8


def draw_accounts(
    screen: pygame.Surface,
    rows: Sequence[Account],
    active: Account | None,
    index: int,
) -> Hits:
    hits = Hits()
    _dim(screen, SCREEN_DIM)
    y = _screen_title(screen, COPY_ACCOUNTS_TITLE, 60) + 24
    row_h = default_font().height * MEDIUM + 20
    shown = list(rows)
    offset = 0
    if len(shown) > ACCOUNT_ROWS:
        offset = min(max(0, index - ACCOUNT_ROWS // 2), len(shown) - ACCOUNT_ROWS)
        shown = shown[offset : offset + ACCOUNT_ROWS]
    card = pygame.Rect(0, y, 660, PAD * 2 + row_h * max(1, len(shown)))
    card.centerx = WIDTH // 2
    _frame(screen, card)
    if not rows:
        empty = _text(COPY_ACCOUNTS_EMPTY, Tone.WALK_LIGHT, SMALL)
        screen.blit(empty, empty.get_rect(center=card.center))
    for slot, account in enumerate(shown):
        row = pygame.Rect(card.left + PAD, card.top + PAD + slot * row_h, card.width - PAD * 2, row_h)
        selected = offset + slot == index
        if selected:
            _highlight(screen, row)
        name = _text(account.name, Tone.SUN if selected else Tone.CREAM, MEDIUM)
        screen.blit(name, name.get_rect(midleft=(row.left + 12, row.centery)))
        if active is not None and account.name == active.name:
            mark = _text(COPY_IN_USE, Tone.NEON_CYAN, SMALL)
            screen.blit(mark, mark.get_rect(midleft=(row.left + 24 + name.get_width(), row.centery)))
        count = _text(str(account.biscuits), Tone.CREAM, MEDIUM)
        count_rect = count.get_rect(midright=(row.right - 12, row.centery))
        screen.blit(count, count_rect)
        icon = _icon(BISCUIT, count.get_height())
        if icon is not None:
            screen.blit(icon, icon.get_rect(midright=(count_rect.left - 8, row.centery)))
        hits.add(Action.SELECT, row, offset + slot)
    btn_y = card.bottom + 20
    new_btn = pygame.Rect(0, btn_y, 200, BTN_H)
    new_btn.centerx = WIDTH // 2 - 220
    use_btn = pygame.Rect(0, btn_y, 200, BTN_H)
    use_btn.centerx = WIDTH // 2
    back_btn = pygame.Rect(0, btn_y, 200, BTN_H)
    back_btn.centerx = WIDTH // 2 + 220
    _button(screen, hits, Action.NEW, COPY_BTN_NEW, new_btn, Tone.SUN)
    if rows:
        _button(screen, hits, Action.CONFIRM, COPY_BTN_USE, use_btn, Tone.NEON_CYAN)
    _button(screen, hits, Action.BACK, COPY_BTN_BACK, back_btn, Tone.MAUVE)
    return hits


def draw_naming(screen: pygame.Surface, text: str, error: str, time: float) -> Hits:
    hits = Hits()
    _dim(screen, SCREEN_DIM)
    title = _text(COPY_NAME_TITLE, Tone.SUN, LARGE + 1)
    font = default_font()
    cell_w = font.size("W", NAME_SCALE)[0] + NAME_SCALE * 2
    cell_h = font.height * NAME_SCALE
    width = max(title.get_width(), cell_w * NAME_MAX) + PAD * 4
    hint = _text(COPY_NAME_HINT, Tone.CREAM, SMALL)
    width = max(width, hint.get_width() + PAD * 2, 480)
    note = _text(error, Tone.CORAL, SMALL) if error else None
    height = PAD * 3 + title.get_height() + 24 + cell_h + 24 + hint.get_height() + BTN_H + 20
    height += note.get_height() + 12 if note is not None else 0
    rect = pygame.Rect(0, 0, width, height)
    rect.center = (WIDTH // 2, HEIGHT // 2)
    _frame(screen, rect, Tone.SUN)
    y = rect.top + PAD
    screen.blit(title, title.get_rect(midtop=(rect.centerx, y)))
    y += title.get_height() + 24
    left = rect.centerx - cell_w * NAME_MAX // 2
    for slot in range(NAME_MAX):
        x = left + slot * cell_w
        screen.fill(tone(Tone.MAUVE), (x + NAME_SCALE, y + cell_h + 4, cell_w - NAME_SCALE * 2, NAME_SCALE // 2))
        if slot < len(text):
            letter = _text(text[slot], Tone.CREAM, NAME_SCALE)
            screen.blit(letter, letter.get_rect(midtop=(x + cell_w // 2, y)))
        elif slot == len(text) and _blink(time):
            screen.fill(tone(Tone.SUN), (x + NAME_SCALE, y, cell_w - NAME_SCALE * 2, cell_h))
    y += cell_h + 24
    screen.blit(hint, hint.get_rect(midtop=(rect.centerx, y)))
    y += hint.get_height() + 12
    if note is not None:
        screen.blit(note, note.get_rect(midtop=(rect.centerx, y)))
        y += note.get_height() + 12
    confirm = pygame.Rect(0, y, 200, BTN_H)
    confirm.centerx = rect.centerx - 110
    back = pygame.Rect(0, y, 200, BTN_H)
    back.centerx = rect.centerx + 110
    _button(screen, hits, Action.CONFIRM, COPY_BTN_CONFIRM, confirm, Tone.SUN)
    _button(screen, hits, Action.BACK, COPY_BTN_BACK, back, Tone.MAUVE)
    return hits


def draw_upgrades(
    screen: pygame.Surface,
    rows: Sequence[UpgradeLine],
    wallet: int,
    account_name: str,
    index: int,
    note: str,
) -> Hits:
    hits = Hits()
    _dim(screen, SCREEN_DIM)
    y = _screen_title(screen, COPY_UPGRADES_TITLE, 24) + 12
    owner = _text(account_name, Tone.SUN, MEDIUM)
    wallet_w = _text(COPY_WALLET.format(count=wallet), Tone.CREAM, MEDIUM).get_width() + owner.get_height() + 8
    line_w = owner.get_width() + 28 + wallet_w
    x = WIDTH // 2 - line_w // 2
    screen.blit(owner, (x, y))
    _wallet(screen, wallet, x + owner.get_width() + 28, y, MEDIUM)
    y += owner.get_height() + 8
    tip = _text(COPY_UPGRADES_NOTE, Tone.WALK_LIGHT, SMALL)
    screen.blit(tip, tip.get_rect(midtop=(WIDTH // 2, y)))
    y += tip.get_height() + 16
    row_h = 54
    card = pygame.Rect(0, y, 900, PAD * 2 + row_h * len(rows))
    card.centerx = WIDTH // 2
    _frame(screen, card)
    chosen = 0 if not rows else max(0, min(index, len(rows) - 1))
    for slot, line in enumerate(rows):
        row = pygame.Rect(card.left + PAD, card.top + PAD + slot * row_h, card.width - PAD * 2, row_h)
        selected = slot == chosen
        if selected:
            _highlight(screen, row)
        _shop_row(screen, row, line, wallet, selected)
        hits.add(Action.SELECT, row, slot)
    btn_y = card.bottom + 14
    buy = pygame.Rect(0, btn_y, 220, BTN_H)
    buy.centerx = WIDTH // 2 - 120
    back = pygame.Rect(0, btn_y, 220, BTN_H)
    back.centerx = WIDTH // 2 + 120
    _button(screen, hits, Action.BUY, COPY_BTN_BUY, buy, Tone.SUN)
    _button(screen, hits, Action.BACK, COPY_BTN_BACK, back, Tone.MAUVE)
    if note:
        mark = _text(note, Tone.CORAL, SMALL)
        screen.blit(mark, mark.get_rect(midtop=(WIDTH // 2, btn_y + BTN_H + 10)))
    return hits


def _shop_row(screen: pygame.Surface, row: pygame.Rect, line: UpgradeLine, wallet: int, selected: bool) -> None:
    x = row.left + 12
    icon = _icon(line.sprite, SHOP_ICON)
    if icon is not None:
        screen.blit(icon, icon.get_rect(midleft=(x, row.centery)))
        x += SHOP_ICON + 16
    name = _text(line.name, Tone.SUN if selected else Tone.CREAM, MEDIUM)
    screen.blit(name, (x, row.top + 8))
    effect = _text(line.effect, Tone.CREAM if selected else Tone.WALK_LIGHT, SMALL)
    screen.blit(effect, (x, row.top + 12 + name.get_height()))
    if line.cost is None:
        price = _text(COPY_MAXED, Tone.NEON_CYAN, MEDIUM)
    else:
        price = _text(COPY_PRICE.format(cost=line.cost), Tone.SUN if wallet >= line.cost else Tone.CORAL, MEDIUM)
    price_rect = price.get_rect(midright=(row.right - 12, row.centery))
    screen.blit(price, price_rect)
    coin = _icon(BISCUIT, price.get_height()) if line.cost is not None else None
    right = price_rect.left - 8
    if coin is not None:
        screen.blit(coin, coin.get_rect(midright=(right, row.centery)))
        right -= coin.get_width() + 8
    pip = 12
    for step in range(line.max_level - 1, -1, -1):
        right -= pip + 6
        filled = step < line.level
        box = pygame.Rect(right, row.centery - pip // 2, pip, pip)
        screen.fill(tone(Tone.INK), box.inflate(4, 4))
        screen.fill(tone(Tone.SUN if filled else Tone.PLUM), box)


def draw_splash(screen: pygame.Surface, time: float) -> Hits:
    hits = Hits()
    screen.fill(tone(Tone.PLUM_DARK))
    title = _title(TITLE_SCALE)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
    tag = _text(COPY_TAGLINE, Tone.CREAM, MEDIUM)
    screen.blit(tag, tag.get_rect(midtop=(WIDTH // 2, HEIGHT // 2 + 40)))
    version = _text(COPY_VERSION, Tone.WALK_LIGHT, SMALL)
    screen.blit(version, version.get_rect(bottomright=(WIDTH - 24, HEIGHT - 20)))
    _gallop(screen, time)
    _prompt(screen, time, COPY_SPLASH_HINT, HEIGHT - 120)
    hits.add(Action.SKIP, pygame.Rect(0, 0, WIDTH, HEIGHT))
    start = pygame.Rect(0, HEIGHT - 160, 280, BTN_H)
    start.centerx = WIDTH // 2
    _button(screen, hits, Action.SKIP, COPY_SPLASH_HINT, start, Tone.SUN)
    return hits


def draw_credits(screen: pygame.Surface) -> Hits:
    hits = Hits()
    _dim(screen, SCREEN_DIM)
    y = _screen_title(screen, COPY_CREDITS_TITLE, 80) + 36
    for slot, source in enumerate(COPY_CREDITS):
        if not source:
            y += 16
            continue
        color = Tone.SUN if slot == 0 else Tone.CREAM
        scale = MEDIUM if slot == 0 else SMALL + 1
        image = _text(source, color, scale)
        screen.blit(image, image.get_rect(midtop=(WIDTH // 2, y)))
        y += image.get_height() + 14
    back = pygame.Rect(0, HEIGHT - 100, 220, BTN_H)
    back.centerx = WIDTH // 2
    _button(screen, hits, Action.BACK, COPY_BTN_BACK, back, Tone.MAUVE)
    return hits


def draw_options(
    screen: pygame.Surface,
    options: Options,
    index: int,
    stats: DayStats | None = None,
) -> Hits:
    hits = Hits()
    _dim(screen, SCREEN_DIM)
    y = _screen_title(screen, COPY_OPTIONS_TITLE, 48) + 20
    rows = (
        (COPY_VOLUME, _volume_label(options.volume)),
        (COPY_FULLSCREEN, COPY_ON if options.fullscreen else COPY_OFF),
        (COPY_HITBOXES, COPY_ON if options.show_hitboxes else COPY_OFF),
        (COPY_TELEMETRY, COPY_ON if options.telemetry else COPY_OFF),
        (COPY_LANGUAGE, COPY_LANG_ES),
        (COPY_CREDITS_ROW, ""),
    )
    row_h = 52
    card = pygame.Rect(0, y, 720, PAD * 2 + row_h * len(rows))
    card.centerx = WIDTH // 2
    _frame(screen, card)
    chosen = max(0, min(index, len(rows) - 1))
    for slot, (label, value) in enumerate(rows):
        row = pygame.Rect(card.left + PAD, card.top + PAD + slot * row_h, card.width - PAD * 2, row_h)
        if slot == chosen:
            _highlight(screen, row)
        left = _text(label, Tone.SUN if slot == chosen else Tone.CREAM, MEDIUM)
        screen.blit(left, (row.left + 12, row.centery - left.get_height() // 2))
        if slot == 0:
            minus = pygame.Rect(row.right - 140, row.centery - 18, 36, 36)
            plus = pygame.Rect(row.right - 48, row.centery - 18, 36, 36)
            _button(screen, hits, Action.NUDGE, COPY_BTN_MINUS, minus, Tone.MAUVE, slot, -1)
            _button(screen, hits, Action.NUDGE, COPY_BTN_PLUS, plus, Tone.MAUVE, slot, 1)
            mid = _text(value, Tone.CREAM, SMALL)
            screen.blit(mid, mid.get_rect(midright=(minus.left - 12, row.centery)))
        elif value:
            right = _text(value, Tone.CREAM, MEDIUM)
            screen.blit(right, right.get_rect(midright=(row.right - 12, row.centery)))
        if slot == 0:
            pass
        elif slot == 5:
            hits.add(Action.CREDITS, row, slot)
        elif slot in (1, 2, 3):
            hits.add(Action.TOGGLE, row, slot)
        else:
            hits.add(Action.SELECT, row, slot)
    btn_y = card.bottom + 14
    credits = pygame.Rect(0, btn_y, 220, BTN_H)
    credits.centerx = WIDTH // 2 - 120
    back = pygame.Rect(0, btn_y, 220, BTN_H)
    back.centerx = WIDTH // 2 + 120
    _button(screen, hits, Action.CREDITS, COPY_BTN_CREDITS, credits, Tone.SUN)
    _button(screen, hits, Action.BACK, COPY_BTN_BACK, back, Tone.MAUVE)
    if options.telemetry and stats is not None:
        text = (
            COPY_STATS_TODAY.format(runs=stats.runs, average=stats.average)
            if stats.runs > 0
            else COPY_STATS_EMPTY
        )
        mark = _text(text, Tone.WALK_LIGHT, SMALL)
        screen.blit(mark, mark.get_rect(midtop=(WIDTH // 2, btn_y + BTN_H + 10)))
    return hits


def _volume_label(level: int) -> str:
    filled = max(0, min(VOLUME_MAX, level))
    empty = VOLUME_MAX - filled
    return COPY_VOLUME_BAR.format(
        filled=VOLUME_FILL * filled,
        empty=VOLUME_EMPTY * empty,
        level=filled,
    )
