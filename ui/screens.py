"""Responsive monochrome desktop composition and user-facing help."""
from __future__ import annotations

import calendar
from datetime import datetime
from pathlib import Path

import pygame

import config as cfg
from core.transformer import calculate_output_voltage
from ui.components import Button, SpinBox


class AppState:
    def __init__(self):
        self.primary_voltage = cfg.Vp_DEFAULT
        self.primary_turns = cfg.Np_DEFAULT
        self.secondary_turns = cfg.Ns_DEFAULT
        self.frequency = cfg.Simulated_Frequency_DEFAULT
        self.mode = cfg.CONTROL_METHOD
        self.animation_enabled = cfg.ANIMATION_ENABLED_DEFAULT
        self.selected_control = 0
        self.help_visible = False
        self.active_screen = "index"


class IndexScreen:
    """Two-column launch dashboard with project widgets and system status."""

    def __init__(self, theme):
        self.theme = theme
        self.last_size = None
        self.open_workbench: Button | None = None

    def _layout(self, surface, state):
        width, height = surface.get_size()
        margin, gap = 24, 16
        footer_height = 38
        widget_top = margin
        usable_width = width - margin * 2
        left_width = int(usable_width * 0.43)
        right_width = usable_width - left_width - gap
        widget_height = max(150, height - widget_top - margin - footer_height)
        self.title_rect = pygame.Rect(margin, widget_top, left_width, 146)
        self.time_rect = pygame.Rect(margin, self.title_rect.bottom + gap, left_width, 112)
        self.calendar_rect = pygame.Rect(margin, self.time_rect.bottom + gap, left_width, widget_height - self.title_rect.height - self.time_rect.height - gap * 2)
        right_x = self.title_rect.right + gap
        self.document_rect = pygame.Rect(right_x, widget_top, right_width, (widget_height - gap) // 2)
        self.tutorial_rect = pygame.Rect(right_x, self.document_rect.bottom + gap, right_width, widget_height - self.document_rect.height - gap)
        self.footer_rect = pygame.Rect(0, height - footer_height, width, footer_height)
        if self.last_size != (width, height):
            self.last_size = (width, height)
            self.open_workbench = Button((self.title_rect.left + 18, self.title_rect.bottom - 48, 194, 32), "OPEN WORKBENCH", lambda: setattr(state, "active_screen", "workbench"), "Open the interactive transformer simulator.")

    def _panel(self, surface, rect):
        pygame.draw.rect(surface, self.theme.colors["card"], rect, border_radius=cfg.CORNER_RADIUS)
        pygame.draw.rect(surface, self.theme.colors["border"], rect, 1, border_radius=cfg.CORNER_RADIUS)

    def _text(self, surface, text, position, size=14, color=None, bold=False):
        surface.blit(self.theme.render_text(text, size, color, bold), position)

    def handle_event(self, event, state):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            state.active_screen = "workbench"
            return
        if self.open_workbench:
            self.open_workbench.handle_event(event)

    def draw(self, surface, state, dt=0.016):
        self._layout(surface, state)
        colors = self.theme.colors
        now = datetime.now()
        surface.fill(colors["bg"])
        self._draw_title_widget(surface)
        self._draw_document_widget(surface)
        self._draw_tutorial_widget(surface)
        self._draw_time_widget(surface, now)
        self._draw_calendar_widget(surface, now)
        self._draw_footer(surface)

    def _draw_title_widget(self, surface):
        self._panel(surface, self.title_rect)
        colors = self.theme.colors
        self._text(surface, "TRANSFORMER", (self.title_rect.left + 18, self.title_rect.top + 18), 24, bold=True)
        self._text(surface, "LEARNING WORKBENCH", (self.title_rect.left + 18, self.title_rect.top + 45), 24, bold=True)
        self._text(surface, "Interactive transformer study environment", (self.title_rect.left + 19, self.title_rect.top + 78), 12, colors["text_subtle"])
        self.open_workbench.rect.topleft = (self.title_rect.left + 18, self.title_rect.bottom - 48)
        self.open_workbench.draw(surface, self.theme)
        self._text(surface, "ENTER  OPEN", (self.title_rect.left + 222, self.title_rect.bottom - 36), 10, colors["text_subtle"], True)

    def _draw_document_widget(self, surface):
        self._panel(surface, self.document_rect)
        colors = self.theme.colors
        self._text(surface, "01  PROJECT DOCUMENT", (self.document_rect.left + 18, self.document_rect.top + 17), 12, bold=True)
        self._text(surface, "DOCUMENT WIDGET / PLACEHOLDER", (self.document_rect.left + 18, self.document_rect.top + 42), 10, colors["text_subtle"], True)
        self._text(surface, "Attach your thesis, learning guide, or laboratory worksheet here.", (self.document_rect.left + 18, self.document_rect.top + 68), 13, colors["text_subtle"])
        self._text(surface, "NO DOCUMENT CONNECTED", (self.document_rect.left + 18, self.document_rect.bottom - 32), 11, colors["text"], True)

    def _draw_tutorial_widget(self, surface):
        self._panel(surface, self.tutorial_rect)
        colors = self.theme.colors
        self._text(surface, "02  DEMO TUTORIAL", (self.tutorial_rect.left + 18, self.tutorial_rect.top + 17), 12, bold=True)
        self._text(surface, "TUTORIAL WIDGET / PLACEHOLDER", (self.tutorial_rect.left + 18, self.tutorial_rect.top + 42), 10, colors["text_subtle"], True)
        steps = ("1. Set Vp, Np, and Ns.", "2. Observe the calculated Vs.", "3. Compare step-up and step-down modes.")
        for index, step in enumerate(steps):
            self._text(surface, step, (self.tutorial_rect.left + 18, self.tutorial_rect.top + 70 + index * 22), 12, colors["text_subtle"])

    def _draw_time_widget(self, surface, now):
        self._panel(surface, self.time_rect)
        colors = self.theme.colors
        self._text(surface, "03  LOCAL TIME", (self.time_rect.left + 18, self.time_rect.top + 16), 11, bold=True)
        time_image = self.theme.render_text(now.strftime("%H:%M:%S"), 29, colors["text"], True)
        surface.blit(time_image, (self.time_rect.left + 18, self.time_rect.top + 40))
        self._text(surface, now.strftime("%A, %d %B %Y"), (self.time_rect.left + 20, self.time_rect.bottom - 21), 11, colors["text_subtle"])

    def _draw_calendar_widget(self, surface, now):
        self._panel(surface, self.calendar_rect)
        colors = self.theme.colors
        self._text(surface, "04  CALENDAR", (self.calendar_rect.left + 18, self.calendar_rect.top + 16), 11, bold=True)
        month_title = now.strftime("%B %Y").upper()
        self._text(surface, month_title, (self.calendar_rect.left + 18, self.calendar_rect.top + 40), 14, colors["text"], True)
        calendar_data = calendar.Calendar(firstweekday=0).monthdayscalendar(now.year, now.month)
        grid_left, grid_top = self.calendar_rect.left + 18, self.calendar_rect.top + 70
        grid_width = self.calendar_rect.width - 36
        cell_width = grid_width / 7
        for index, weekday in enumerate(("MO", "TU", "WE", "TH", "FR", "SA", "SU")):
            header = self.theme.render_text(weekday, 9, colors["text_subtle"], True)
            surface.blit(header, header.get_rect(center=(grid_left + cell_width * (index + 0.5), grid_top)))
        for row, week in enumerate(calendar_data):
            for column, day in enumerate(week):
                if not day:
                    continue
                center = (int(grid_left + cell_width * (column + 0.5)), grid_top + 25 + row * 25)
                if day == now.day:
                    marker = pygame.Rect(0, 0, 24, 20)
                    marker.center = center
                    pygame.draw.rect(surface, colors["text"], marker, border_radius=2)
                    day_color = colors["bg"]
                else:
                    day_color = colors["text"]
                day_image = self.theme.render_text(str(day), 11, day_color, day == now.day)
                surface.blit(day_image, day_image.get_rect(center=center))

    @staticmethod
    def _battery_status() -> str:
        """Read a Linux battery percentage when one exists; Pi 4 has no battery."""
        for capacity_file in Path("/sys/class/power_supply").glob("BAT*/capacity"):
            try:
                return f"BATTERY {int(capacity_file.read_text().strip())}%"
            except (OSError, ValueError):
                pass
        return "POWER EXTERNAL"

    @staticmethod
    def _cpu_temperature() -> str:
        """Read the Raspberry Pi thermal sensor without adding a dependency."""
        try:
            value = int(Path("/sys/class/thermal/thermal_zone0/temp").read_text().strip())
            return f"CPU {value / 1000:.1f}°C"
        except (OSError, ValueError):
            return "CPU --°C"

    def _draw_footer(self, surface):
        colors = self.theme.colors
        pygame.draw.rect(surface, (245, 245, 245), self.footer_rect)
        pygame.draw.line(surface, colors["border"], self.footer_rect.topleft, self.footer_rect.topright)
        self._text(surface, "TRANSFORMER LEARNING WORKBENCH  /  READY", (18, self.footer_rect.top + 13), 10, colors["text_subtle"], True)

        cpu_text, battery_text = self._cpu_temperature(), self._battery_status()
        battery_x = self.footer_rect.right - 178
        cpu_x = battery_x - 145
        # Battery outline and charge bar.
        battery_icon = pygame.Rect(battery_x, self.footer_rect.top + 11, 18, 12)
        pygame.draw.rect(surface, colors["text"], battery_icon, 1)
        pygame.draw.rect(surface, colors["text"], (battery_icon.right, battery_icon.top + 4, 2, 4))
        if battery_text.startswith("BATTERY"):
            pygame.draw.rect(surface, colors["text"], battery_icon.inflate(-5, -5))
        self._text(surface, battery_text, (battery_x + 27, self.footer_rect.top + 13), 10, colors["text_subtle"], True)
        # Thermometer icon and the live Pi thermal-sensor value.
        pygame.draw.line(surface, colors["text"], (cpu_x + 7, self.footer_rect.top + 10), (cpu_x + 7, self.footer_rect.top + 21), 2)
        pygame.draw.circle(surface, colors["text"], (cpu_x + 7, self.footer_rect.top + 23), 4)
        self._text(surface, cpu_text, (cpu_x + 18, self.footer_rect.top + 13), 10, colors["text_subtle"], True)


class MainScreen:
    """Single-window workstation screen with deliberately restrained surfaces."""

    def __init__(self, theme, transformer_view):
        self.theme = theme
        self.transformer_view = transformer_view
        self.controls: list[Button | SpinBox] = []
        self.last_size = None
        self.tooltip = ""
        self.home_btn: Button | None = None

    def _build_controls(self, state):
        panel, x, width = self.control_rect, self.control_rect.left + 18, self.control_rect.width - 36
        self.vp_spin = SpinBox((x, panel.top + 70, width, 38), state.primary_voltage, cfg.Vp_MIN, cfg.Vp_MAX, cfg.Vp_STEP, lambda value: setattr(state, "primary_voltage", float(value)), "vp", "Ideal primary input voltage. Arrow keys adjust the focused control.")
        self.np_spin = SpinBox((x, panel.top + 142, width, 38), state.primary_turns, cfg.Np_MIN, cfg.Np_MAX, cfg.Np_STEP, lambda value: setattr(state, "primary_turns", int(value)), "np", "Primary turns. This input is kept positive for safe calculations.")
        self.ns_spin = SpinBox((x, panel.top + 214, width, 38), state.secondary_turns, cfg.Ns_MIN, cfg.Ns_MAX, cfg.Ns_STEP, lambda value: setattr(state, "secondary_turns", int(value)), "ns", "Secondary turns used by the ideal turns-ratio equation.")
        preset_y, half = panel.top + 278, (width - 8) // 2
        self.mode_up = Button((x, preset_y, half, 34), "STEP-UP", lambda: self._preset_step_up(state), "Sets Np = 100 and Ns = 200.")
        self.mode_down = Button((x + half + 8, preset_y, width - half - 8, 34), "STEP-DOWN", lambda: self._preset_step_down(state), "Sets Np = 200 and Ns = 100.")
        self.reset_btn = Button((x, preset_y + 44, width, 32), "RESET DEFAULTS  /  R", lambda: self._reset(state), "Restores 12 V, Np 100, and Ns 200.")
        self.controls = [self.vp_spin, self.np_spin, self.ns_spin, self.mode_up, self.mode_down, self.reset_btn]
        self._set_focus(state.selected_control)

    def _layout(self, surface, state):
        width, height = surface.get_size()
        margin, header_h, results_h, gap = 20, 76, 132, 16
        content_top, content_bottom = header_h + margin, height - results_h - margin
        control_w = max(300, min(370, int(width * 0.31)))
        panel_h = max(360, content_bottom - content_top)
        self.control_rect = pygame.Rect(width - margin - control_w, content_top, control_w, panel_h)
        self.transformer_rect = pygame.Rect(margin, content_top, max(260, self.control_rect.left - margin - gap), panel_h)
        self.results_rect = pygame.Rect(margin, height - results_h, width - margin * 2, results_h - margin)
        if self.last_size != (width, height):
            self.last_size = (width, height)
            self.home_btn = Button((width - 230, 22, 76, 25), "HOME", lambda: setattr(state, "active_screen", "index"), "Return to the launch page.")
            self._build_controls(state)

    def _sync_controls(self, state):
        if self.controls:
            self.vp_spin.value = state.primary_voltage
            self.np_spin.value = state.primary_turns
            self.ns_spin.value = state.secondary_turns

    def _set_focus(self, index):
        if not self.controls:
            return
        for control in self.controls:
            control.focused = False
        self.controls[index % len(self.controls)].focused = True

    def _preset_step_up(self, state):
        state.primary_turns, state.secondary_turns = 100, 200
        self._sync_controls(state)

    def _preset_step_down(self, state):
        state.primary_turns, state.secondary_turns = 200, 100
        self._sync_controls(state)

    def _reset(self, state):
        state.primary_voltage = cfg.Vp_DEFAULT
        state.primary_turns = cfg.Np_DEFAULT
        state.secondary_turns = cfg.Ns_DEFAULT
        self._sync_controls(state)

    def handle_event(self, event, state):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_HOME:
                state.active_screen = "index"
                return
            if event.key == pygame.K_h:
                state.help_visible = not state.help_visible
                return
            if state.help_visible and event.key == pygame.K_ESCAPE:
                state.help_visible = False
                return
            if event.key == pygame.K_TAB:
                direction = -1 if event.mod & pygame.KMOD_SHIFT else 1
                state.selected_control = (state.selected_control + direction) % len(self.controls)
                self._set_focus(state.selected_control)
                return
            if event.key in (pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT):
                control = self.controls[state.selected_control]
                if isinstance(control, SpinBox):
                    control.adjust(1 if event.key in (pygame.K_UP, pygame.K_RIGHT) else -1)
                return
        if self.home_btn:
            self.home_btn.handle_event(event)
        for index, control in enumerate(self.controls):
            if control.handle_event(event):
                state.selected_control = index
                self._set_focus(index)
        self.tooltip = next((control.tooltip for control in self.controls if getattr(control, "hovered", False)), "")

    def _text(self, surface, text, position, size=14, color=None, bold=False):
        surface.blit(self.theme.render_text(text, size, color, bold), position)

    def _panel(self, surface, rect):
        colors = self.theme.colors
        pygame.draw.rect(surface, colors["card"], rect, border_radius=cfg.CORNER_RADIUS)
        pygame.draw.rect(surface, colors["border"], rect, 1, border_radius=cfg.CORNER_RADIUS)

    def draw(self, surface, state, dt=0.016):
        self._layout(surface, state)
        colors = self.theme.colors
        surface.fill(colors["bg"])

        self._text(surface, "TRANSFORMER LEARNING WORKBENCH", (24, 19), 22, bold=True)
        self._text(surface, "Single-phase ideal transformer simulation", (24, 48), 13, colors["text_subtle"])
        pygame.draw.line(surface, colors["border"], (24, 76), (surface.get_width() - 24, 76))
        status = pygame.Rect(surface.get_width() - 146, 22, 122, 25)
        pygame.draw.rect(surface, colors["bg"], status, border_radius=2)
        pygame.draw.rect(surface, colors["text"], status, 1, border_radius=2)
        label = self.theme.render_text("SIMULATION READY", 10, colors["text"], True)
        surface.blit(label, label.get_rect(center=status.center))
        if self.home_btn:
            self.home_btn.rect.topleft = (surface.get_width() - 230, 22)
            self.home_btn.draw(surface, self.theme)
        self._text(surface, "HOME  INDEX  /  H  HELP", (surface.get_width() - 205, 55), 10, colors["text_subtle"], True)

        self._panel(surface, self.transformer_rect)
        self._text(surface, "01  TRANSFORMER DIAGRAM", (self.transformer_rect.left + 18, self.transformer_rect.top + 16), 12, colors["text"], True)
        self._text(surface, "Illustrative winding density — calculated values shown below", (self.transformer_rect.left + 18, self.transformer_rect.top + 36), 11, colors["text_subtle"])
        pygame.draw.line(surface, colors["border"], (self.transformer_rect.left + 18, self.transformer_rect.top + 58), (self.transformer_rect.right - 18, self.transformer_rect.top + 58))
        self.transformer_view.draw(surface, self.transformer_rect.x, self.transformer_rect.y + 61, self.transformer_rect.width, self.transformer_rect.height - 61, state, self.theme, dt)

        self._panel(surface, self.control_rect)
        self._text(surface, "02  INPUTS", (self.control_rect.left + 18, self.control_rect.top + 16), 12, colors["text"], True)
        self._text(surface, "Use Tab and arrow keys, or the stepper buttons.", (self.control_rect.left + 18, self.control_rect.top + 37), 11, colors["text_subtle"])
        labels = (("PRIMARY VOLTAGE  /  Vp", f"{cfg.Vp_MIN:g}–{cfg.Vp_MAX:g} V", 52), ("PRIMARY TURNS  /  Np", f"{cfg.Np_MIN}–{cfg.Np_MAX}", 124), ("SECONDARY TURNS  /  Ns", f"{cfg.Ns_MIN}–{cfg.Ns_MAX}", 196))
        for label_text, range_text, y in labels:
            self._text(surface, label_text, (self.control_rect.left + 18, self.control_rect.top + y), 10, colors["text"], True)
            range_image = self.theme.render_text(range_text, 10, colors["text_subtle"])
            surface.blit(range_image, (self.control_rect.right - 18 - range_image.get_width(), self.control_rect.top + y))
        self._text(surface, "DEMONSTRATION PRESETS", (self.control_rect.left + 18, self.control_rect.top + 260), 10, colors["text_subtle"], True)
        for control in self.controls:
            control.draw(surface, self.theme)

        self._draw_results(surface, state)
        if self.tooltip:
            self._text(surface, self.tooltip, (24, surface.get_height() - 17), 10, colors["text_subtle"])
        if state.help_visible:
            self._draw_help(surface)

    def _draw_results(self, surface, state):
        colors = self.theme.colors
        result = calculate_output_voltage(state.primary_voltage, state.primary_turns, state.secondary_turns)
        self._panel(surface, self.results_rect)
        self._text(surface, "03  CALCULATED IDEAL VALUES", (self.results_rect.left + 18, self.results_rect.top + 13), 11, colors["text"], True)
        self._text(surface, "SIMULATED — NOT LIVE METER READINGS", (self.results_rect.right - 247, self.results_rect.top + 13), 10, colors["text_subtle"], True)
        divider_y = self.results_rect.top + 34
        pygame.draw.line(surface, colors["border"], (self.results_rect.left + 18, divider_y), (self.results_rect.right - 18, divider_y))
        columns = (("OUTPUT VOLTAGE  /  Vs", f"{result.secondary_voltage:.{cfg.PRECISION_VOLTAGE}f} V"), ("TURNS RATIO  /  Ns : Np", f"{result.turns_ratio:.{cfg.PRECISION_RATIO}f} : 1"), ("OPERATING MODE", result.classification))
        column_width = (self.results_rect.width - 36) // 3
        for index, (label_text, value) in enumerate(columns):
            x = self.results_rect.left + 18 + index * column_width
            if index:
                pygame.draw.line(surface, colors["border"], (x - 18, divider_y + 13), (x - 18, self.results_rect.bottom - 35))
            self._text(surface, label_text, (x, self.results_rect.top + 48), 10, colors["text_subtle"], True)
            self._text(surface, value, (x, self.results_rect.top + 68), 21, colors["text"], True)
        self._text(surface, result.classification_detail, (self.results_rect.left + 18, self.results_rect.bottom - 22), 11, colors["text_subtle"])

    def _draw_help(self, surface):
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 72))
        surface.blit(overlay, (0, 0))
        width, height = min(600, surface.get_width() - 48), min(400, surface.get_height() - 48)
        panel = pygame.Rect((surface.get_width() - width) // 2, (surface.get_height() - height) // 2, width, height)
        pygame.draw.rect(surface, self.theme.colors["card"], panel, border_radius=cfg.CORNER_RADIUS)
        pygame.draw.rect(surface, self.theme.colors["text"], panel, 2, border_radius=cfg.CORNER_RADIUS)
        self._text(surface, "KEYBOARD & MOUSE HELP", (panel.left + 24, panel.top + 23), 18, bold=True)
        pygame.draw.line(surface, self.theme.colors["border"], (panel.left + 24, panel.top + 55), (panel.right - 24, panel.top + 55))
        lines = [
            "Tab / Shift+Tab       Select next / previous control",
            "Arrow keys            Increase or decrease selected value",
            "M                     Toggle step-up and step-down presets",
            "R                     Restore the default demonstration values",
            "A                     Toggle magnetic-flux animation",
            "H / Esc               Close this panel",
            "",
            "All displayed readings are calculated ideal values.",
            "This desktop prototype does not measure physical equipment.",
        ]
        for index, line in enumerate(lines):
            color = self.theme.colors["text"] if index < 6 else self.theme.colors["text_subtle"]
            self._text(surface, line, (panel.left + 24, panel.top + 76 + index * 27), 13, color)
