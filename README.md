# Interactive Transformer Learning Workbench

A desktop Pygame learning tool for demonstrating the ideal single-phase transformer turns-ratio principle. It presents a Panda3D-rendered 3D transformer model alongside editable primary voltage (`Vp`), primary turns (`Np`), and secondary turns (`Ns`).

> **Important:** this is a simulation. Every output reading is a calculated ideal value, not a live electrical-meter measurement. It does not connect to, measure, or control physical equipment.

## Raspberry Pi 4 deployment

This project is configured for a Raspberry Pi 4 Model B with 2 GB RAM and a
64-bit Raspberry Pi OS installation. The default frame rate is 30 FPS and the
Panda3D model renders off-screen at a Pi-friendly resolution before it is
scaled into the dashboard.

Use a reliable 5 V / 3 A USB-C power supply and active cooling for sustained
3D rendering. Use 720p display output for the smoothest presentation. Copy the
entire project folder, excluding `.venv`, `__pycache__`, and `Panda3D-1.10`;
those files are machine-generated and are not part of the transfer package.

On Raspberry Pi OS Bookworm or later, use a 64-bit installation and run:

```bash
cd transformer_workbench
bash scripts/install_raspberry_pi.sh
bash scripts/run_raspberry_pi.sh
```

The launcher starts the workbench full-screen. To run in a resizable window
instead, use `TRANSFORMER_FULLSCREEN=0 .venv/bin/python main.py`.

If the display setup needs more performance, lower `RENDER_SIZE` in
`ui/transformer_view.py`. The application has no GPIO or ADC dependency; the
hardware controller remains an unconnected future-extension interface.

## Run in VS Code

1. Open the `transformer_workbench` folder in VS Code.
2. Select a Python 3 interpreter from the status bar.
3. In the VS Code terminal, install the required dependency:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Run the application:

   ```powershell
   python main.py
   ```

The app is designed for a 1280 × 720 desktop window and supports resizing down to 900 × 620. Close the window, or press `Esc` when help is not open, to exit.

The launch page includes live local-time and calendar widgets, plus placeholders for a project document and demo tutorial. Select **Open Workbench** or press `Enter` to launch the simulator. Press `Home` in the simulator to return to the launch page.


## How to use it

Change `Vp`, `Np`, or `Ns` with the on-screen `−` and `+` buttons. The results panel immediately calculates:

`Vs = Vp × (Ns / Np)`

`Ns > Np` is **STEP-UP**, `Ns < Np` is **STEP-DOWN**, and equal turns are **1:1 RATIO**. Inputs are constrained to safe configured ranges, so desktop UI interaction cannot create zero or negative turn counts.

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| `Tab` / `Shift+Tab` | Focus next / previous control |
| Arrow keys | Increase or decrease the focused numeric input |
| `M` | Toggle Step-Up and Step-Down presets |
| `R` | Reset to 12 V, Np = 100, Ns = 200 |
| `A` | Toggle flux animation |
| `H` | Show or hide the shortcut help panel |
| `Esc` | Close help; otherwise exit the app |

Hover over a control for a short description. The header also keeps the `Press H for Help` legend visible.

## Architecture

```text
transformer_workbench/
├── main.py                  # Pygame startup, event loop, resize and shutdown
├── config.py                # Defaults, ranges, sizing, palette and feature flags
├── core/transformer.py      # Pure ideal-transformer calculation and classification
├── ui/theme.py              # Shared fonts and semantic color theme
├── ui/components.py         # Reusable buttons and numeric spin boxes
├── ui/screens.py            # Responsive dashboard, help overlay and results view
├── ui/transformer_view.py   # Panda3D off-screen 3D core and helix windings
└── controllers/
    ├── keyboard.py          # Reusable keyboard/mouse controller abstraction
    └── hardware.py          # Future hardware interface stub; no GPIO dependency
```

## Configuration

Edit `config.py` to adjust the window dimensions, minimum resize size, FPS, numeric defaults/ranges/increments, display precision, color palette, font sizes, and feature flags. Important settings include:

- `FEATURE_SHOW_FLUX_ANIMATION`, `ANIMATION_ENABLED_DEFAULT`, and `ANIMATION_SPEED_DEFAULT` for flux visualization.
- `FPS` for presentation performance; it is set to 30 for the target Pi 4.
- `Vp_*`, `Np_*`, and `Ns_*` for safe input ranges, defaults, and step sizes.
- `COLOR_*`, font-size constants, `MIN_WINDOW_WIDTH`, and `MIN_WINDOW_HEIGHT` for visual customization.

## Scope and limitations

- The model uses the ideal equation only; it does not model losses, current, power, efficiency, magnetic saturation, temperature, waveform distortion, or physical-transformer safety behavior.
- Winding loops in the graphic are illustrative density cues, not literal turn counts.
- The desktop build has no hardware-controller, GPIO, ADC, or live-meter integration. `controllers/hardware.py` deliberately remains an isolated placeholder for future work.
- The simulation runs offline. Pygame provides the application shell and Panda3D renders the 3D transformer model off-screen inside it.
