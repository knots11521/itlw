
import math
import sys
import pygame

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Transformer Workbench - Pure Pygame 3D")
clock = pygame.time.Clock()

# Interface colors
BG = (243, 246, 249)
WHITE = (255, 255, 255)
BORDER = (211, 217, 224)
TEXT = (32, 39, 47)
MUTED = (105, 114, 125)
GREEN = (0, 195, 105)

# Wire materials
RED = (222, 48, 40)
RED_DARK = (113, 24, 24)
BLUE = (35, 115, 225)
BLUE_DARK = (13, 51, 111)

# Steel core
STEEL = (91, 101, 112)

title_font = pygame.font.SysFont("Arial", 17, bold=True)
body_font = pygame.font.SysFont("Arial", 13)
small_font = pygame.font.SysFont("Arial", 11)

# Model dimensions
CORE_W = 8.0
CORE_H = 5.6
CORE_D = 1.5
LEG_W = 1.25
BAR_H = 1.05

# Winding configuration
PRIMARY_TURNS = 12
SECONDARY_TURNS = 14
WIRE_RADIUS_PX = 5

# Camera
yaw = math.radians(-27)
pitch = math.radians(17)
zoom = 53.0
pan_x = 0.0
pan_y = 0.0

rotating = False
panning = False
last_mouse = (0, 0)

show_flux = True
show_laminations = True


def clamp(v, low, high):
    return max(low, min(high, v))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def normalize(v):
    length = math.sqrt(sum(x * x for x in v))
    if length < 1e-9:
        return (0, 0, 1)
    return tuple(x / length for x in v)


def shade(color, brightness):
    return tuple(
        int(clamp(c * brightness, 0, 255))
        for c in color
    )


def rotate3(p):
    """Rotate world coordinates into the camera orientation."""
    x, y, z = p

    cy, sy = math.cos(yaw), math.sin(yaw)
    x, z = x * cy - z * sy, x * sy + z * cy

    cp, sp = math.cos(pitch), math.sin(pitch)
    y, z = y * cp - z * sp, y * sp + z * cp

    return x, y, z


def project(p, center):
    """Orthographic 3D projection."""
    x, y, z = rotate3(p)
    return (
        int(center[0] + x * zoom + pan_x),
        int(center[1] - y * zoom + pan_y),
    )


def cuboid(center, size, color):
    """Generate shaded faces for an axis-aligned solid cuboid."""
    cx, cy, cz = center
    sx, sy, sz = (v / 2 for v in size)

    vertices = [
        (cx-sx, cy-sy, cz-sz),
        (cx+sx, cy-sy, cz-sz),
        (cx+sx, cy+sy, cz-sz),
        (cx-sx, cy+sy, cz-sz),
        (cx-sx, cy-sy, cz+sz),
        (cx+sx, cy-sy, cz+sz),
        (cx+sx, cy+sy, cz+sz),
        (cx-sx, cy+sy, cz+sz),
    ]

    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (3, 2, 6, 7),
        (0, 3, 7, 4),
        (1, 5, 6, 2),
    ]

    light = normalize((-0.45, 0.8, -0.65))
    result = []

    for face in faces:
        points = [vertices[i] for i in face]
        normal = normalize(
            cross(sub(points[1], points[0]),
                  sub(points[2], points[0]))
        )

        brightness = 0.42 + 0.58 * max(
            0, sum(normal[i] * light[i] for i in range(3))
        )

        result.append((points, shade(color, brightness)))

    return result


def core_geometry():
    """Four bars form the transformer's rectangular iron core."""
    middle_h = CORE_H - 2 * BAR_H

    left_x = -CORE_W / 2 + LEG_W / 2
    right_x = CORE_W / 2 - LEG_W / 2
    top_y = CORE_H / 2 - BAR_H / 2
    bottom_y = -CORE_H / 2 + BAR_H / 2

    bars = [
        ((0, top_y, 0), (CORE_W, BAR_H, CORE_D)),
        ((0, bottom_y, 0), (CORE_W, BAR_H, CORE_D)),
        ((left_x, 0, 0), (LEG_W, middle_h, CORE_D)),
        ((right_x, 0, 0), (LEG_W, middle_h, CORE_D)),
    ]

    faces = []
    for center, size in bars:
        faces.extend(cuboid(center, size, STEEL))

    return faces


def coil_segments(x_center, turns, color, dark_color, phase=0.0):
    """
    Construct one continuous wire path:
    start terminal -> helical winding -> end terminal.

    Each segment belongs to the same connected path. The wire is rendered
    as a thick, highlighted line with rounded joins.
    """
    y_min = -CORE_H / 2 + BAR_H + 0.22
    y_max = CORE_H / 2 - BAR_H - 0.22

    rx = LEG_W / 2 + 0.44
    rz = CORE_D / 2 + 0.40

    steps_per_turn = 72
    total_steps = turns * steps_per_turn

    start_angle = math.pi + phase
    end_angle = start_angle + turns * 2 * math.pi

    def helix_point(i):
        t = i / total_steps
        angle = start_angle + (end_angle - start_angle) * t
        y = y_min + (y_max - y_min) * t

        return (
            x_center + rx * math.cos(angle),
            y,
            rz * math.sin(angle),
        )

    coil_points = [
        helix_point(i)
        for i in range(total_steps + 1)
    ]

    # Connect both leads directly to the endpoints of the helix.
    first = coil_points[0]
    last = coil_points[-1]
    lead_length = 0.95

    start_terminal = (
        first[0] - lead_length,
        first[1],
        first[2],
    )

    end_terminal = (
        last[0] - lead_length,
        last[1],
        last[2],
    )

    # One continuous ordered path.
    path = [start_terminal] + coil_points + [end_terminal]

    segments = []

    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        z_mid = (a[2] + b[2]) / 2

        wire_color = color if z_mid > 0 else dark_color

        # Bright glint along the front-facing surface.
        if z_mid > rz * 0.70:
            wire_color = tuple(
                min(255, int(c * 1.18 + 12))
                for c in color
            )

        segments.append((a, b, wire_color, WIRE_RADIUS_PX))

    return {
        "path": path,
        "segments": segments,
        "start": start_terminal,
        "end": end_terminal,
        "color": color,
    }


def make_scene(elapsed):
    commands = []

    # Core polygons
    for points, color in core_geometry():
        depth = sum(rotate3(p)[2] for p in points) / len(points)
        commands.append(
            (depth, "polygon", points, color, 0)
        )

    # One connected coil on each core leg.
    left_x = -CORE_W / 2 + LEG_W / 2
    right_x = CORE_W / 2 - LEG_W / 2

    primary = coil_segments(
        left_x, PRIMARY_TURNS, RED, RED_DARK
    )
    secondary = coil_segments(
        right_x, SECONDARY_TURNS, BLUE, BLUE_DARK, 0.12
    )

    for winding in (primary, secondary):
        for a, b, color, width in winding["segments"]:
            depth = (rotate3(a)[2] + rotate3(b)[2]) / 2
            commands.append(
                (depth, "wire", (a, b), color, width)
            )

    # Subtle lamination seams
    if show_laminations:
        z = CORE_D / 2 + 0.018
        y = -CORE_H / 2 + BAR_H + 0.07

        while y < CORE_H / 2 - BAR_H:
            for x1, x2 in (
                (-CORE_W/2, -CORE_W/2 + LEG_W),
                (CORE_W/2 - LEG_W, CORE_W/2),
            ):
                a = (x1, y, z)
                b = (x2, y, z)
                depth = (rotate3(a)[2] + rotate3(b)[2]) / 2

                commands.append(
                    (depth, "line", (a, b), (137, 145, 153), 1)
                )

            y += 0.13

    # Animated flux arrows on the yokes
    if show_flux:
        pulse = 0.5 + 0.5 * math.sin(elapsed * 3)
        flux_color = (
            0,
            int(150 + 65 * pulse),
            int(80 + 30 * pulse),
        )

        arrows = [
            ((-2.7, CORE_H/2-BAR_H/2, CORE_D/2+0.045), 1),
            ((0.0, CORE_H/2-BAR_H/2, CORE_D/2+0.045), 1),
            ((2.3, CORE_H/2-BAR_H/2, CORE_D/2+0.045), 1),
            ((-2.3, -CORE_H/2+BAR_H/2, CORE_D/2+0.045), -1),
            ((0.0, -CORE_H/2+BAR_H/2, CORE_D/2+0.045), -1),
            ((2.7, -CORE_H/2+BAR_H/2, CORE_D/2+0.045), -1),
        ]

        for start, direction in arrows:
            end = (
                start[0] + direction * 0.38,
                start[1],
                start[2],
            )

            depth = (rotate3(start)[2] + rotate3(end)[2]) / 2
            commands.append(
                (depth, "line", (start, end), flux_color, 3)
            )

            for dy in (-0.10, 0.10):
                head = (
                    end[0] - direction * 0.13,
                    end[1] + dy,
                    end[2],
                )
                commands.append(
                    (
                        rotate3(end)[2],
                        "line",
                        (end, head),
                        flux_color,
                        2,
                    )
                )

    commands.sort(key=lambda item: item[0])
    return commands, primary, secondary


def draw_wire(surface, a, b, color, width, center):
    """Draw a thick, rounded wire with a darker edge and highlight."""
    pa = project(a, center)
    pb = project(b, center)

    # Outer shadow/rim
    pygame.draw.line(
        surface, shade(color, 0.48),
        pa, pb, width + 4
    )

    # Main body
    pygame.draw.line(
        surface, color,
        pa, pb, width
    )

    # Narrow highlight, offset slightly upward on screen
    highlight = shade(color, 1.30)
    offset = max(1, width // 4)
    ha = (pa[0], pa[1] - offset)
    hb = (pb[0], pb[1] - offset)

    pygame.draw.line(
        surface, highlight,
        ha, hb, max(1, width // 4)
    )

    # Rounded ends and joints
    radius = max(2, width // 2)

    pygame.draw.circle(surface, color, pa, radius)
    pygame.draw.circle(surface, color, pb, radius)

    pygame.draw.circle(
        surface, highlight, ha, max(1, radius // 3)
    )


def draw_scene(surface, viewport, elapsed):
    center = (viewport.centerx, viewport.centery - 5)

    pygame.draw.rect(
        surface, (250, 251, 253),
        viewport, border_radius=8
    )
    pygame.draw.rect(
        surface, (229, 234, 239),
        viewport, 1, border_radius=8
    )

    old_clip = surface.get_clip()
    surface.set_clip(viewport.inflate(-2, -2))

    # Soft screen-space ground shadow
    sw = max(20, int(zoom * 7.5))
    sh = max(12, int(zoom * 0.8))
    shadow = pygame.Surface((sw, sh), pygame.SRCALPHA)

    pygame.draw.ellipse(
        shadow, (45, 52, 60, 30), shadow.get_rect()
    )

    shadow_rect = shadow.get_rect(
        center=(
            center[0] + int(pan_x),
            center[1] + int(zoom * 2.3) + int(pan_y),
        )
    )
    surface.blit(shadow, shadow_rect)

    commands, primary, secondary = make_scene(elapsed)

    for command in commands:
        _, kind, geometry, color, width = command

        if kind == "polygon":
            points = [project(p, center) for p in geometry]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(
                surface, shade(color, 0.70), points, 1
            )

        elif kind == "wire":
            a, b = geometry
            draw_wire(surface, a, b, color, width, center)

        else:
            a, b = geometry
            pygame.draw.line(
                surface, color,
                project(a, center),
                project(b, center),
                max(1, width),
            )

    # Draw terminal labels at the real 3D endpoints of each winding.
    for winding, labels in (
        (primary, ("P1", "P2")),
        (secondary, ("S1", "S2")),
    ):
        for point, label in (
            (winding["start"], labels[0]),
            (winding["end"], labels[1]),
        ):
            pos = project(point, center)
            pygame.draw.circle(
                surface, winding["color"], pos, 5
            )
            pygame.draw.circle(
                surface, WHITE, pos, 2
            )

            label_image = small_font.render(
                label, True, winding["color"]
            )
            surface.blit(
                label_image, (pos[0] - 8, pos[1] + 7)
            )

    surface.set_clip(old_clip)


def draw_text(surface, value, font, color, position):
    surface.blit(font.render(value, True, color), position)


def draw_ui(surface, elapsed):
    w, h = surface.get_size()
    surface.fill(BG)

    panel = pygame.Rect(25, 20, w - 50, h - 40)
    pygame.draw.rect(surface, WHITE, panel, border_radius=9)
    pygame.draw.rect(surface, BORDER, panel, 1, border_radius=9)

    draw_text(
        surface, "01  TRANSFORMER MODEL WORKBENCH",
        title_font, TEXT, (panel.x + 20, panel.y + 14)
    )
    draw_text(
        surface,
        "Pure Pygame 3D | Drag to rotate | Scroll to zoom",
        body_font, MUTED, (panel.x + 20, panel.y + 40)
    )

    view = pygame.Rect(
        panel.x + 170,
        panel.y + 78,
        max(260, panel.width - 340),
        max(240, panel.height - 190),
    )

    draw_scene(surface, view, elapsed)

    pygame.draw.circle(
        surface, GREEN, (panel.x + 25, panel.y + 65), 5
    )
    draw_text(
        surface, "MAGNETIC FLUX",
        small_font, MUTED, (panel.x + 37, panel.y + 59)
    )
    draw_text(
        surface, "F: Flux  L: Laminations  R: Reset  Esc: Quit",
        small_font, MUTED, (panel.right - 255, panel.y + 59)
    )

    card_y = view.bottom + 10
    card_w = (view.width - 10) // 2
    card_h = max(52, panel.bottom - card_y - 34)

    pcard = pygame.Rect(view.left, card_y, card_w, card_h)
    scard = pygame.Rect(
        view.left + card_w + 10, card_y, card_w, card_h
    )

    for rect in (pcard, scard):
        pygame.draw.rect(
            surface, (249, 250, 252), rect, border_radius=6
        )
        pygame.draw.rect(surface, BORDER, rect, 1, border_radius=6)

    pygame.draw.rect(
        surface, RED,
        (pcard.x + 9, pcard.y + 9, 4, max(30, card_h - 18)),
        border_radius=2
    )
    draw_text(
        surface, "PRIMARY WINDING",
        body_font, TEXT, (pcard.x + 20, pcard.y + 7)
    )
    draw_text(
        surface, "Vp INPUT  12.0 V",
        small_font, MUTED, (pcard.x + 20, pcard.y + 28)
    )
    draw_text(
        surface, "Np  100 TURNS",
        small_font, MUTED, (pcard.x + 20, pcard.y + 42)
    )

    pygame.draw.rect(
        surface, BLUE,
        (scard.x + 9, scard.y + 9, 4, max(30, card_h - 18)),
        border_radius=2
    )
    draw_text(
        surface, "SECONDARY WINDING",
        body_font, TEXT, (scard.x + 20, scard.y + 7)
    )
    draw_text(
        surface, "Vs OUTPUT  24.00 V",
        small_font, MUTED, (scard.x + 20, scard.y + 28)
    )
    draw_text(
        surface, "Ns  200 TURNS",
        small_font, MUTED, (scard.x + 20, scard.y + 42)
    )

    draw_text(
        surface,
        "Illustrative 3D geometry. Displayed winding turns are symbolic.",
        small_font, MUTED, (panel.x + 20, panel.bottom - 19)
    )


def reset_camera():
    global yaw, pitch, zoom, pan_x, pan_y
    yaw = math.radians(-27)
    pitch = math.radians(17)
    zoom = 53.0
    pan_x = 0.0
    pan_y = 0.0


def main():
    global yaw, pitch, zoom, pan_x, pan_y
    global rotating, panning, last_mouse
    global show_flux, show_laminations

    elapsed = 0.0
    running = True

    while running:
        elapsed += clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_f:
                    show_flux = not show_flux
                elif event.key == pygame.K_l:
                    show_laminations = not show_laminations
                elif event.key == pygame.K_r:
                    reset_camera()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    rotating = True
                    last_mouse = event.pos

                elif event.button == 3:
                    panning = True
                    last_mouse = event.pos

                elif event.button == 4:
                    zoom = clamp(zoom * 1.08, 22, 90)

                elif event.button == 5:
                    zoom = clamp(zoom / 1.08, 22, 90)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    rotating = False
                elif event.button == 3:
                    panning = False

            elif event.type == pygame.MOUSEWHEEL:
                zoom = clamp(zoom * (1 + event.y * 0.08), 22, 90)

            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                dx = mx - last_mouse[0]
                dy = my - last_mouse[1]

                if rotating:
                    yaw += dx * 0.009
                    pitch = clamp(
                        pitch + dy * 0.008,
                        math.radians(-65),
                        math.radians(65),
                    )

                elif panning:
                    pan_x += dx
                    pan_y += dy

                last_mouse = event.pos

        draw_ui(screen, elapsed)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
