import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

import pygame

import config as cfg
from ui.theme import Theme, init_fonts
from ui.transformer_view import TransformerView
from ui.screens import AppState, IndexScreen, MainScreen


def configure_logging():
    """Write application errors to a rotating log file beside the project."""
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "application.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")],
    )
    return logging.getLogger(__name__)


def main():
    logger = logging.getLogger(__name__)
    pygame.init()
    init_fonts()
    flags = pygame.FULLSCREEN if cfg.FULLSCREEN else (
        pygame.RESIZABLE if cfg.RESIZABLE else 0
    )
    screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT), flags)
    pygame.display.set_caption("Transformer Learning Workbench")
    clock = pygame.time.Clock()

    theme = Theme()
    transformer_view = TransformerView()
    state = AppState()
    index_screen = IndexScreen(theme)
    main_screen = MainScreen(theme, transformer_view)

    running = True
    last_time = pygame.time.get_ticks() / 1000.0

    while running:
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - last_time
        last_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                if getattr(cfg, 'RESIZABLE', True):
                    size = (max(cfg.MIN_WINDOW_WIDTH, event.w), max(cfg.MIN_WINDOW_HEIGHT, event.h))
                    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state.help_visible:
                        state.help_visible = False
                        continue
                    running = False
                elif state.active_screen == "workbench" and event.key == pygame.K_r:
                    main_screen._reset(state)
                elif state.active_screen == "workbench" and event.key == pygame.K_m:
                    # toggle between step-up/step-down presets
                    if state.secondary_turns <= state.primary_turns:
                        main_screen._preset_step_up(state)
                    else:
                        main_screen._preset_step_down(state)
                elif state.active_screen == "workbench" and event.key == pygame.K_a:
                    state.animation_enabled = not state.animation_enabled
            try:
                active_screen = main_screen if state.active_screen == "workbench" else index_screen
                active_screen.handle_event(event, state)
            except Exception:
                logger.exception("Unhandled error while processing event: %r", event)

        # Update and render
        active_screen = main_screen if state.active_screen == "workbench" else index_screen
        active_screen.draw(screen, state, dt)
        pygame.display.flip()
        clock.tick(cfg.FPS)

    transformer_view.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    configure_logging()
    try:
        main()
    except Exception:
        logging.getLogger(__name__).exception("Application stopped because of an unhandled error")
        pygame.quit()
        raise
