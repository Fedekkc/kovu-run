"""Punto de entrada de Kovu Run."""

from __future__ import annotations

from enum import IntEnum, StrEnum

import pygame

from game.accounts import COPY_NAME_SHORT, AccountError, LocalAccountDAO
from game.audio import Audio
from game.crashlog import write_crash
from game.dao import LocalArcadeDAO
from game.demo import Demo
from game.hits import Action, Hit, Hits
from game.name import NameBuffer
from game.options import OptionsStore
from game.render import Renderer
from game.session import Session
from game.settings import FPS
from game.telemetry import Telemetry
from game.ui import (
    draw_accounts,
    draw_credits,
    draw_game_over,
    draw_hud,
    draw_menu,
    draw_naming,
    draw_options,
    draw_splash,
    draw_upgrades,
)
from game.upgrades import banked_biscuits, lines_for, purchase, run_mods
from game.window import decorate, open_display

COPY_SAVE_FAILED = "No se pudo guardar."
CAUGHT_AT = 1.05
RETRY_AT = 0.85
SPLASH_TIME = 2.4
ENTER_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER)


class State(StrEnum):
    SPLASH = "splash"
    MENU = "menu"
    PLAY = "play"
    OVER = "over"
    ACCOUNTS = "accounts"
    NAMING = "naming"
    UPGRADES = "upgrades"
    OPTIONS = "options"
    CREDITS = "credits"


class OptionRow(IntEnum):
    VOLUME = 0
    FULLSCREEN = 1
    HITBOXES = 2
    TELEMETRY = 3
    LANGUAGE = 4
    CREDITS = 5


def main() -> None:
    try:
        _run()
    except BaseException as error:
        if isinstance(error, (SystemExit, KeyboardInterrupt)):
            raise
        try:
            write_crash(error)
        except OSError:
            pass
        raise
    finally:
        try:
            pygame.quit()
        except pygame.error:
            pass


def _run() -> None:
    pygame.init()
    options = OptionsStore()
    screen = open_display(options.value.fullscreen)
    decorate()
    clock = pygame.time.Clock()

    audio = Audio()
    audio.set_volume(options.value.volume)
    audio.play_music()
    telemetry = Telemetry()

    session = Session()
    player = session.player
    world = session.world
    demo = Demo()
    renderer = Renderer(screen)
    renderer.show_hitboxes = options.value.show_hitboxes
    backdrop = Renderer(screen)
    backdrop.show_hitboxes = False
    accounts = LocalAccountDAO()
    ranking = LocalArcadeDAO(accounts=accounts)
    name_buffer = NameBuffer()
    state = State.SPLASH
    rank = 0
    elapsed = 0.0
    splash_at = 0.0
    over_at = 0.0
    account_index = 0
    shop_index = 0
    shop_note = ""
    name_error = ""
    biscuits_saved = False
    saved_count = 0
    option_index = 0
    hits = Hits()

    def begin_run() -> None:
        nonlocal state, rank, biscuits_saved, saved_count
        account = accounts.active()
        if account is None:
            open_accounts()
            return
        player.equip(run_mods(account.levels))
        session.reset()
        rank = 0
        biscuits_saved = False
        saved_count = 0
        state = State.PLAY
        audio.start()

    def bank_biscuits() -> None:
        nonlocal biscuits_saved, saved_count
        if biscuits_saved:
            return
        biscuits_saved = True
        saved_count = 0
        account = accounts.active()
        if account is None or world.biscuits_taken <= 0:
            return
        gained = banked_biscuits(world.biscuits_taken, player.mods.bank_rate)
        account.biscuits += gained
        try:
            accounts.update(account)
        except OSError:
            return
        saved_count = gained

    def record_score() -> None:
        nonlocal rank
        rank = 0
        account = accounts.active()
        if account is None:
            return
        score = world.display_score
        try:
            rank = ranking.insert(account.name, score, world.biscuits_taken)
        except OSError:
            rank = 0
        try:
            telemetry.record(score, options.value.telemetry)
        except OSError:
            pass

    def open_accounts() -> None:
        nonlocal state, account_index
        rows = accounts.list()
        current = accounts.active()
        account_index = 0
        if current is not None:
            for index, row in enumerate(rows):
                if row.name == current.name:
                    account_index = index
                    break
        state = State.ACCOUNTS

    def open_upgrades() -> None:
        nonlocal state, shop_index, shop_note
        if accounts.active() is None:
            open_accounts()
            return
        shop_index = 0
        shop_note = ""
        state = State.UPGRADES

    def open_naming() -> None:
        nonlocal state, name_error
        name_buffer.reset()
        name_error = ""
        state = State.NAMING

    def open_options() -> None:
        nonlocal state, option_index
        option_index = 0
        state = State.OPTIONS

    def apply_display() -> None:
        nonlocal screen
        screen = open_display(options.value.fullscreen)
        decorate()
        renderer.attach(screen)
        backdrop.attach(screen)

    def apply_options() -> None:
        renderer.show_hitboxes = options.value.show_hitboxes
        audio.set_volume(options.value.volume)
        audio.play_music()

    def toggle_fullscreen() -> None:
        options.toggle_fullscreen()
        apply_display()

    def nudge_option(delta: int) -> None:
        row = OptionRow(option_index)
        if row == OptionRow.VOLUME:
            options.set_volume(options.value.volume + delta)
            apply_options()
        elif row == OptionRow.FULLSCREEN and delta != 0:
            toggle_fullscreen()
        elif row == OptionRow.HITBOXES and delta != 0:
            options.toggle_hitboxes()
            apply_options()
        elif row == OptionRow.TELEMETRY and delta != 0:
            options.toggle_telemetry()

    def select_account() -> None:
        nonlocal state
        rows = accounts.list()
        if not rows:
            return
        account_index_safe = max(0, min(account_index, len(rows) - 1))
        try:
            accounts.select(rows[account_index_safe].name)
        except AccountError:
            return
        state = State.MENU

    def buy_upgrade() -> None:
        nonlocal shop_note
        account = accounts.active()
        catalog = lines_for({} if account is None else account.levels)
        if account is None or not catalog:
            return
        shop_index_safe = max(0, min(shop_index, len(catalog) - 1))
        shop_note = purchase(account, catalog[shop_index_safe].id)
        if not shop_note:
            try:
                accounts.update(account)
            except OSError:
                shop_note = COPY_SAVE_FAILED

    def confirm_name() -> None:
        nonlocal state, name_error
        if name_buffer.handle_key(pygame.K_RETURN):
            try:
                accounts.create(name_buffer.text)
            except AccountError as error:
                name_error = str(error)
            else:
                state = State.MENU
        else:
            name_error = COPY_NAME_SHORT

    def handle_hit(hit: Hit) -> bool:
        """True si hay que salir del juego."""
        nonlocal state, account_index, shop_index, shop_note, option_index
        if hit.action == Action.QUIT:
            audio.click()
            return True
        if hit.action == Action.SKIP:
            audio.click()
            state = State.MENU
            return False
        if hit.action == Action.PLAY:
            audio.click()
            if accounts.active() is None:
                open_accounts()
            else:
                begin_run()
            return False
        if hit.action == Action.ACCOUNTS:
            audio.click()
            open_accounts()
            return False
        if hit.action == Action.UPGRADES:
            audio.click()
            open_upgrades()
            return False
        if hit.action == Action.OPTIONS:
            audio.click()
            open_options()
            return False
        if hit.action == Action.CREDITS:
            audio.click()
            state = State.CREDITS
            return False
        if hit.action == Action.BACK:
            audio.click()
            if state == State.NAMING:
                state = State.ACCOUNTS
            elif state == State.CREDITS:
                state = State.OPTIONS
            elif state == State.OVER:
                state = State.MENU
            else:
                state = State.MENU
            return False
        if hit.action == Action.NEW:
            audio.click()
            open_naming()
            return False
        if hit.action == Action.SELECT:
            audio.click()
            if state == State.ACCOUNTS:
                account_index = hit.index
            elif state == State.UPGRADES:
                shop_index = hit.index
                shop_note = ""
            elif state == State.OPTIONS:
                option_index = hit.index
            return False
        if hit.action == Action.CONFIRM:
            audio.click()
            if state == State.ACCOUNTS:
                select_account()
            elif state == State.NAMING:
                confirm_name()
            return False
        if hit.action == Action.BUY:
            audio.click()
            buy_upgrade()
            return False
        if hit.action == Action.RETRY:
            if elapsed - over_at > RETRY_AT:
                begin_run()
            return False
        if hit.action == Action.TOGGLE:
            audio.click()
            option_index = hit.index
            if hit.index == OptionRow.FULLSCREEN:
                toggle_fullscreen()
            elif hit.index == OptionRow.HITBOXES:
                options.toggle_hitboxes()
                apply_options()
            elif hit.index == OptionRow.TELEMETRY:
                options.toggle_telemetry()
            return False
        if hit.action == Action.NUDGE:
            audio.click()
            option_index = hit.index
            nudge_option(hit.delta)
            return False
        return False

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)
        elapsed += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                hit = hits.at(event.pos)
                if hit is not None and handle_hit(hit):
                    running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_h and state == State.PLAY:
                options.toggle_hitboxes()
                apply_options()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p and state == State.PLAY:
                renderer.pixelate = not renderer.pixelate
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state == State.SPLASH:
                    state = State.MENU
                elif state == State.MENU:
                    running = False
                elif state == State.NAMING:
                    state = State.ACCOUNTS
                elif state == State.CREDITS:
                    state = State.OPTIONS
                elif state == State.OPTIONS:
                    state = State.MENU
                else:
                    state = State.MENU
            elif state == State.SPLASH and event.type == pygame.KEYDOWN and event.key in (*ENTER_KEYS, pygame.K_SPACE):
                state = State.MENU
            elif state == State.OPTIONS and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    option_index = (option_index - 1) % len(OptionRow)
                elif event.key == pygame.K_DOWN:
                    option_index = (option_index + 1) % len(OptionRow)
                elif event.key == pygame.K_LEFT:
                    nudge_option(-1)
                elif event.key == pygame.K_RIGHT:
                    nudge_option(1)
                elif event.key in ENTER_KEYS:
                    if option_index == OptionRow.CREDITS:
                        state = State.CREDITS
                    elif option_index == OptionRow.FULLSCREEN:
                        toggle_fullscreen()
                    elif option_index == OptionRow.HITBOXES:
                        options.toggle_hitboxes()
                        apply_options()
                    elif option_index == OptionRow.TELEMETRY:
                        options.toggle_telemetry()
            elif state == State.NAMING and event.type == pygame.KEYDOWN:
                edited = event.key == pygame.K_BACKSPACE or pygame.K_a <= event.key <= pygame.K_z
                if edited:
                    name_error = ""
                    name_buffer.handle_key(event.key)
                elif event.key in ENTER_KEYS:
                    confirm_name()
            elif state == State.ACCOUNTS and event.type == pygame.KEYDOWN:
                rows = accounts.list()
                if event.key == pygame.K_n:
                    open_naming()
                elif rows and event.key == pygame.K_UP:
                    account_index = (account_index - 1) % len(rows)
                elif rows and event.key == pygame.K_DOWN:
                    account_index = (account_index + 1) % len(rows)
                elif rows and event.key in ENTER_KEYS:
                    select_account()
            elif state == State.UPGRADES and event.type == pygame.KEYDOWN:
                account = accounts.active()
                catalog = lines_for({} if account is None else account.levels)
                if event.key == pygame.K_UP and catalog:
                    shop_index = (shop_index - 1) % len(catalog)
                    shop_note = ""
                elif event.key == pygame.K_DOWN and catalog:
                    shop_index = (shop_index + 1) % len(catalog)
                    shop_note = ""
                elif event.key in ENTER_KEYS and account is not None and catalog:
                    buy_upgrade()
            elif event.type == pygame.KEYDOWN and event.key in (*ENTER_KEYS, pygame.K_SPACE):
                if state == State.MENU:
                    if accounts.active() is None:
                        open_accounts()
                    else:
                        begin_run()
                elif state == State.OVER and elapsed - over_at > RETRY_AT:
                    begin_run()
            elif state == State.MENU and event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                open_accounts()
            elif state == State.MENU and event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                open_upgrades()
            elif state == State.MENU and event.type == pygame.KEYDOWN and event.key == pygame.K_o:
                open_options()
            elif state == State.PLAY and not world.game_over:
                player.handle_event(event)

        if state == State.SPLASH and elapsed - splash_at >= SPLASH_TIME:
            state = State.MENU

        if state in (State.PLAY, State.OVER):
            session.step(dt, audio)
            if state == State.PLAY and world.game_over and world.catch_timer > CAUGHT_AT:
                bank_biscuits()
                record_score()
                over_at = elapsed
                state = State.OVER
        elif state != State.SPLASH:
            demo.update(dt)

        hits = Hits()
        if state == State.SPLASH:
            hits = draw_splash(screen, elapsed)
        elif state in (State.PLAY, State.OVER):
            renderer.draw(world, player, elapsed, session.effects)
            draw_hud(
                screen,
                world.display_score,
                ranking.best(),
                world.biscuits_taken,
                player.power_label,
                player.charge,
            )
            if state == State.OVER:
                hits = draw_game_over(
                    screen, world.display_score, ranking.best(), rank, saved_count, elapsed - over_at
                )
        else:
            backdrop.draw(demo.session.world, demo.session.player, elapsed, demo.session.effects)
            account = accounts.active()
            if state == State.MENU:
                hits = draw_menu(
                    screen,
                    ranking.top(),
                    elapsed,
                    None if account is None else account.name,
                    0 if account is None else account.biscuits,
                )
            elif state == State.ACCOUNTS:
                hits = draw_accounts(screen, accounts.list(), account, account_index)
            elif state == State.NAMING:
                hits = draw_naming(screen, name_buffer.text, name_error, elapsed)
            elif state == State.OPTIONS:
                hits = draw_options(screen, options.value, option_index, telemetry.today())
            elif state == State.CREDITS:
                hits = draw_credits(screen)
            elif account is None:
                hits = draw_accounts(screen, accounts.list(), None, account_index)
            else:
                hits = draw_upgrades(
                    screen, lines_for(account.levels), account.biscuits, account.name, shop_index, shop_note
                )

        pygame.display.flip()


if __name__ == "__main__":
    main()
