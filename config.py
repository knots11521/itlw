"""Centralized configuration for Transformer Learning Workbench."""

import os

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FULLSCREEN = os.getenv("TRANSFORMER_FULLSCREEN", "0") == "1"
# Raspberry Pi 4 (2 GB) deployment profile: 30 FPS keeps the Pygame UI and
# its pure-Pygame transformer renderer responsive while reducing CPU load.
FPS = 30
RESIZABLE = not FULLSCREEN
MIN_WINDOW_WIDTH = 900
MIN_WINDOW_HEIGHT = 620

# Physical parameter limits and defaults
Vp_DEFAULT = 12.0
Vp_MIN = 1.0
Vp_MAX = 240.0
Vp_STEP = 1.0

Np_DEFAULT = 100
Np_MIN = 10
Np_MAX = 1000
Np_STEP = 10

Ns_DEFAULT = 200
Ns_MIN = 10
Ns_MAX = 1000
Ns_STEP = 10

Simulated_Frequency_DEFAULT = 60
Simulated_Frequency_OPTIONS = [50, 60]

# Theme palette - monochrome desktop system
# Keep the simulator deliberately quiet: white workspace, black type and
# neutral greys only. Functional state remains explicit in the UI labels.
COLOR_BACKGROUND = (255, 255, 255)
COLOR_CARD = (255, 255, 255)
COLOR_ACCENT_PRIMARY = (18, 18, 18)
COLOR_ACCENT_SECONDARY = (18, 18, 18)
COLOR_CORE = (228, 228, 228)
COLOR_FLUX = (0, 0, 0)
COLOR_TEXT = (12, 12, 12)
COLOR_TEXT_SUBTLE = (90, 90, 90)
COLOR_BORDER = (190, 190, 190)
COLOR_BUTTON_HOVER = (242, 242, 242)
COLOR_BUTTON_PRESSED = (225, 225, 225)

# Font settings
FONT_FAMILY = "Segoe UI"
FONT_SIZE_SMALL = 14
FONT_SIZE_MEDIUM = 16
FONT_SIZE_LARGE = 20
FONT_SIZE_TITLE = 32

# Component styling
CORNER_RADIUS = 3
PADDING_SMALL = 8
PADDING_MEDIUM = 12
PADDING_LARGE = 16
GAP_SMALL = 6
GAP_MEDIUM = 12
GAP_LARGE = 20
BORDER_WIDTH = 1

# Animation settings
ANIMATION_ENABLED_DEFAULT = True
ANIMATION_SPEED_DEFAULT = 1.0

# Feature flags
FEATURE_SHOW_FLUX_ANIMATION = True
FEATURE_SHOW_TURNS_RATIO = True
FEATURE_KEYBOARD_CONTROLS = True

# Display precision
PRECISION_VOLTAGE = 2
PRECISION_RATIO = 3

# Default control method
CONTROL_METHOD = "Keyboard/Mouse"

# Suggested keyboard defaults (centralized)
KEYBINDING_SELECT_NEXT = "Tab"
KEYBINDING_ADJUST_INCREMENT = "ArrowUp, ArrowDown, Left, Right"
KEYBINDING_TOGGLE_MODE = "M"
KEYBINDING_RESET = "R"
KEYBINDING_HELP = "H"
KEYBINDING_TOGGLE_ANIMATION = "A"
