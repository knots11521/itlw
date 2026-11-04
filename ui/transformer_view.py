"""Pure-Pygame 3D-style transformer illustration for the dashboard."""

from __future__ import annotations

import math

import pygame

from core.transformer import calculate_output_voltage


class PygameTransformerRenderer:
    """Draw a shaded orthographic transformer model without a 3D engine."""

    CORE_WIDTH, CORE_HEIGHT, CORE_DEPTH = 5.5, 4.5, 1.50
    LIMB_WIDTH, YOKE_THICKNESS = 0.84, 0.68
    LIMB_CENTER_X, YOKE_CENTER_Y = 2.18, 2.25
    COIL_HEIGHT, COIL_RADIUS = 3.25, 0.73
    PRIMARY, SECONDARY, FLUX, STEEL = (232, 46, 42), (31, 96, 224), (28, 166, 72), (95, 103, 112)

    def __init__(self):
        self.flow_phase = 0.0
        self.visual_turns = (5, 5)
        self.turn_signature: tuple[int, int] | None = None

    @staticmethod
    def _clamp(value, lower, upper):
        return max(lower, min(upper, value))

    @classmethod
    def _shade(cls, color, brightness):
        return tuple(int(cls._clamp(channel * brightness, 0, 255)) for channel in color)

    @staticmethod
    def _sub(a, b):
        return tuple(left - right for left, right in zip(a, b))

    @staticmethod
    def _cross(a, b):
        return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

    @staticmethod
    def _normalise(vector):
        length = math.sqrt(sum(component * component for component in vector))
        return (0, 0, 1) if length < 1e-9 else tuple(component / length for component in vector)

    @staticmethod
    def _coil_turns(turns: int, maximum: int) -> int:
        """Map electrical turns to a readable symbolic winding density."""
        return max(5, min(11, round(5 + 6 * turns / max(maximum, 1))))

    def set_turns(self, primary_turns: int, secondary_turns: int):
        signature = (primary_turns, secondary_turns)
        if signature != self.turn_signature:
            self.turn_signature = signature
            maximum = max(primary_turns, secondary_turns, 1)
            self.visual_turns = (self._coil_turns(primary_turns, maximum), self._coil_turns(secondary_turns, maximum))

    @staticmethod
    def _rotate(point):
        """Centered elevated camera, matching the original Panda3D view."""
        x, y, z = point
        # The original camera was centred on the core (x=0), not angled from
        # either side.  Keeping x unchanged preserves the core's symmetry.
        # A modest elevation exposes the top and side planes without skewing
        # either limb left or right.
        cosine, sine = math.cos(math.radians(23)), math.sin(math.radians(23))
        return x, y * cosine - z * sine, y * sine + z * cosine

    def _project(self, point, center, zoom):
        x, y, _ = self._rotate(point)
        return round(center[0] + x * zoom), round(center[1] - y * zoom)

    def _cuboid_faces(self, center, size, color):
        cx, cy, cz = center
        sx, sy, sz = (dimension / 2 for dimension in size)
        vertices = [(cx-sx, cy-sy, cz-sz), (cx+sx, cy-sy, cz-sz), (cx+sx, cy+sy, cz-sz), (cx-sx, cy+sy, cz-sz), (cx-sx, cy-sy, cz+sz), (cx+sx, cy-sy, cz+sz), (cx+sx, cy+sy, cz+sz), (cx-sx, cy+sy, cz+sz)]
        faces = ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (3, 2, 6, 7), (0, 3, 7, 4), (1, 5, 6, 2))
        light, result = self._normalise((-0.45, 0.8, -0.65)), []
        for face in faces:
            points = [vertices[index] for index in face]
            normal = self._normalise(self._cross(self._sub(points[1], points[0]), self._sub(points[2], points[0])))
            brightness = 0.42 + 0.58 * max(0, sum(normal[index] * light[index] for index in range(3)))
            depth = sum(self._rotate(point)[2] for point in points) / len(points)
            result.append((depth, "polygon", points, self._shade(color, brightness), 0))
        return result

    def _core_commands(self):
        # The limbs meet the *inner faces* of the yokes.  Ending them at a
        # yoke centreline made the lower member look like a detached base.
        limb_height = 2 * (self.YOKE_CENTER_Y - self.YOKE_THICKNESS / 2)
        bars = (((0, self.YOKE_CENTER_Y, 0), (self.CORE_WIDTH, self.YOKE_THICKNESS, self.CORE_DEPTH)), ((0, -self.YOKE_CENTER_Y, 0), (self.CORE_WIDTH, self.YOKE_THICKNESS, self.CORE_DEPTH)), ((-self.LIMB_CENTER_X, 0, 0), (self.LIMB_WIDTH, limb_height, self.CORE_DEPTH)), ((self.LIMB_CENTER_X, 0, 0), (self.LIMB_WIDTH, limb_height, self.CORE_DEPTH)))
        return [command for center, size in bars for command in self._cuboid_faces(center, size, self.STEEL)]

    def _coil(self, center_x, turns, color, phase, outward):
        steps, start_y, end_y = turns * 42, -self.COIL_HEIGHT / 2, self.COIL_HEIGHT / 2
        points = []
        for index in range(steps + 1):
            progress = index / steps
            angle = phase + math.tau * turns * progress
            points.append((center_x + self.COIL_RADIUS * math.cos(angle), start_y + (end_y - start_y) * progress, self.COIL_RADIUS * math.sin(angle)))
        first, last = points[0], points[-1]
        lead = 0.82 * outward
        path = [(first[0] + lead, first[1], first[2])] + points + [(last[0] + lead, last[1], last[2])]
        commands = []
        for first, last in zip(path, path[1:]):
            depth = (self._rotate(first)[2] + self._rotate(last)[2]) / 2
            z_mid = (first[2] + last[2]) / 2
            wire_color = color if z_mid > 0 else self._shade(color, 0.52)
            if z_mid > self.COIL_RADIUS * 0.68:
                wire_color = self._shade(color, 1.14)
            commands.append((depth, "wire", (first, last), wire_color, 5))
        return commands, path[0], path[-1]

    def _flux_point(self, progress):
        progress, side = progress % 1.0, (progress % 1.0) * 4
        x, y, front = self.LIMB_CENTER_X, self.YOKE_CENTER_Y, self.CORE_DEPTH / 2 + 0.05
        if side < 1:
            return -x + 2*x*side, y, front
        if side < 2:
            return x, y - 2*y*(side-1), front
        if side < 3:
            return x - 2*x*(side-2), -y, front
        return -x, -y + 2*y*(side-3), front

    def _marker_position(self, center_x, turns, progress, phase):
        """Position a moving signal marker on a symbolic winding."""
        progress %= 1.0
        angle = phase + math.tau * turns * progress
        return center_x + self.COIL_RADIUS * math.cos(angle), -self.COIL_HEIGHT / 2 + self.COIL_HEIGHT * progress, self.COIL_RADIUS * math.sin(angle)

    def render(self, width, height, primary_turns, secondary_turns, primary_voltage, time_delta, animation_enabled):
        self.set_turns(primary_turns, secondary_turns)
        if animation_enabled:
            self.flow_phase = (self.flow_phase + time_delta * (0.18 + self._clamp(primary_voltage, 0, 240) / 240 * 0.42)) % 1.0
        image = pygame.Surface((max(1, width), max(1, height)), pygame.SRCALPHA)
        viewport = image.get_rect().inflate(-8, -30)
        pygame.draw.rect(image, (250, 251, 253), viewport, border_radius=5)
        pygame.draw.rect(image, (226, 230, 234), viewport, 1, border_radius=5)
        old_clip = image.get_clip()
        image.set_clip(viewport.inflate(-2, -2))
        center = viewport.centerx, viewport.centery + round(viewport.height * .05)
        zoom = max(12, min(viewport.width / 9.8, viewport.height / 7.1))
        shadow = pygame.Surface((max(20, round(zoom*5.8)), max(10, round(zoom*.68))), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (40, 47, 56, 32), shadow.get_rect())
        image.blit(shadow, shadow.get_rect(center=(center[0], center[1] + round(zoom*2.55))))
        core_commands = self._core_commands()
        primary, p_start, p_end = self._coil(-self.LIMB_CENTER_X, self.visual_turns[0], self.PRIMARY, math.pi, -1)
        secondary, s_start, s_end = self._coil(self.LIMB_CENTER_X, self.visual_turns[1], self.SECONDARY, 0, 1)
        windings = primary + secondary

        def draw_winding(commands):
            for _, _, geometry, color, line_width in commands:
                first, last = (self._project(point, center, zoom) for point in geometry)
                width_px = max(2, round(line_width * zoom / 52))
                pygame.draw.line(image, self._shade(color, .45), first, last, width_px + 3)
                pygame.draw.line(image, color, first, last, width_px)

        # A winding wraps around a limb.  Rendering its rear half first and
        # its front half last makes the iron visibly pass through the coil,
        # while retaining an unbroken, consistent helical path.
        rear_windings = [command for command in windings if sum(point[2] for point in command[2]) / 2 < 0]
        front_windings = [command for command in windings if sum(point[2] for point in command[2]) / 2 >= 0]
        draw_winding(rear_windings)
        for _, _, geometry, color, _ in sorted(core_commands, key=lambda command: command[0]):
            points = [self._project(point, center, zoom) for point in geometry]
            pygame.draw.polygon(image, color, points)
            pygame.draw.polygon(image, self._shade(color, .65), points, 1)
        for y_tenths in range(-15, 16, 3):
            for x1, x2 in ((-2.75, -1.76), (1.76, 2.75)):
                pygame.draw.line(image, (133, 141, 149), self._project((x1, y_tenths/10, self.CORE_DEPTH/2+.015), center, zoom), self._project((x2, y_tenths/10, self.CORE_DEPTH/2+.015), center, zoom), 1)
        draw_winding(front_windings)
        for terminal, color in ((p_start, self.PRIMARY), (p_end, self.PRIMARY), (s_start, self.SECONDARY), (s_end, self.SECONDARY)):
            point = self._project(terminal, center, zoom)
            pygame.draw.circle(image, color, point, max(3, round(zoom/14)))
            pygame.draw.circle(image, (255, 255, 255), point, max(1, round(zoom/35)))
        for index in range(8):
            pygame.draw.circle(image, self.FLUX, self._project(self._flux_point(self.flow_phase*.55 + index/8), center, zoom), max(2, round(zoom/21)))
        if animation_enabled:
            for center_x, turns, phase, direction in ((-self.LIMB_CENTER_X, self.visual_turns[0], math.pi, 1), (self.LIMB_CENTER_X, self.visual_turns[1], 0, -1)):
                for offset in (0, .25, .5, .75):
                    point = self._marker_position(center_x, turns, self.flow_phase*direction + offset*direction, phase)
                    pygame.draw.circle(image, (255, 255, 255), self._project(point, center, zoom), max(2, round(zoom/19)))
        image.set_clip(old_clip)
        return image

    def destroy(self):
        """Compatibility lifecycle hook; Pygame has no external render context."""


class TransformerView:
    """Pygame-only bridge used by the workbench's transformer panel."""

    def __init__(self):
        self.renderer = PygameTransformerRenderer()

    def draw(self, surface, x, y, width, height, state, theme=None, time_delta=.016):
        panel = pygame.Rect(x, y, width, height)
        if panel.width <= 0 or panel.height <= 0:
            return
        image = self.renderer.render(panel.width, panel.height, int(state.primary_turns), int(state.secondary_turns), float(state.primary_voltage), time_delta, bool(getattr(state, "animation_enabled", True)))
        surface.blit(image, panel.topleft)
        if theme:
            self._draw_terminal_labels(surface, panel, state, theme)
            self._draw_model_notices(surface, panel, theme)

    @staticmethod
    def _draw_terminal_labels(surface, panel, state, theme):
        label_font, detail_font = theme.get_font(10, bold=True), theme.get_font(10)
        result = calculate_output_voltage(state.primary_voltage, state.primary_turns, state.secondary_turns)
        primary = ("PRIMARY WINDING", f"Vp INPUT  {state.primary_voltage:.1f} V", f"Np  {state.primary_turns} TURNS")
        secondary = ("SECONDARY WINDING", f"Vs OUTPUT  {result.secondary_voltage:.2f} V", f"Ns  {state.secondary_turns} TURNS")
        label_y = panel.centery - 34
        for index, text in enumerate(primary):
            label = (label_font if index == 0 else detail_font).render(text, True, theme.colors["text"] if index == 0 else theme.colors["text_subtle"])
            surface.blit(label, (panel.left + 14, label_y + index * 14))
        for index, text in enumerate(secondary):
            label = (label_font if index == 0 else detail_font).render(text, True, theme.colors["text"] if index == 0 else theme.colors["text_subtle"])
            surface.blit(label, (panel.right - 14 - label.get_width(), label_y + index * 14))

    @staticmethod
    def _draw_model_notices(surface, panel, theme):
        subtle = theme.colors["text_subtle"]
        flux_label = theme.render_text("GREEN MARKERS = MAGNETIC FLUX PATH THROUGH THE IRON CORE", 10, subtle, True)
        disclaimer = theme.render_text("SOFTWARE MODEL / SIMULATION — NOT A PHYSICAL MEASUREMENT TOOL", 10, subtle, True)
        symbolic = theme.render_text("DRAWN WINDING LOOPS ARE SYMBOLIC; TURN COUNTS ARE SHOWN IN THE LABELS.", 10, subtle)
        surface.blit(flux_label, flux_label.get_rect(midtop=(panel.centerx, panel.top + 8)))
        surface.blit(disclaimer, disclaimer.get_rect(midbottom=(panel.centerx, panel.bottom - 23)))
        surface.blit(symbolic, symbolic.get_rect(midbottom=(panel.centerx, panel.bottom - 8)))

    def close(self):
        self.renderer.destroy()
