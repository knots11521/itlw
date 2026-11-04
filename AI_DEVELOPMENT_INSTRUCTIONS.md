# AI Development Instructions — Interactive Transformer Learning Workbench

## 1. Role and objective

Act as a senior Python desktop-application developer and UI/UX engineer. Help build a polished, modular **Interactive Transformer Learning Workbench** using **Python and Pygame**.

Develop and test the application locally in **Visual Studio Code**. Python and Pygame are already installed. Do not provide Raspberry Pi setup instructions or assume the application is being run on Raspberry Pi during this development stage.

Build the software as an educational simulation of a single-phase transformer. The application must help learners explore step-up and step-down voltage behavior by changing the input voltage and winding turns, then observing the calculated output and a clear visual transformer representation.

## 2. Source of truth and scope

Use the thesis document titled *Design and Development of Interactive Transformer Learning Machine for Demonstrating Step-Up and Step-Down Voltage Applications* as the primary requirements reference.

The thesis specifies that the software model should:
- Display a digital representation of a single-phase transformer.
- Let the user select or adjust primary/input voltage.
- Let the user adjust primary turns (`Np`) and secondary turns (`Ns`).
- Calculate and display expected output voltage.
- Identify step-up, step-down, or equal-turns operation.
- Display the selected values and results clearly.
- Support an educational demonstration of the turns-ratio principle.
- Be evaluated for functionality, calculation consistency, safety, and usability.

The thesis scope is a **software-based ideal transformer demonstration**, not a physical transformer measurement system. Do not claim the program measures real voltage, current, power, efficiency, or magnetic quantities. Make it clear in the UI that output values are calculated/simulated.

## 3. Technology and development constraints

- Language: Python 3.
- Graphics and event loop: Pygame.
- IDE: Visual Studio Code.
- Python and Pygame are already installed.
- The program must work offline and must not require a web server.
- Do not introduce a web framework or another GUI framework unless explicitly requested.
- Prefer Pygame drawing primitives for the transformer, coils, core, flux indicators, charts, buttons, cards, sliders, and knobs. External image assets should be optional, not required for the main interface.
- Keep dependencies minimal.
- Use clear, maintainable, typed Python where practical.
- Do not add hardware-specific GPIO or ADC dependencies in the initial desktop version. Hardware integration is a later phase and should remain isolated behind a controller interface.

## 4. Modular architecture

Keep responsibilities separated. Use this structure, adjusting only when there is a clear technical reason:

```text
transformer_workbench/
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── core/
│   ├── __init__.py
│   └── transformer.py
├── ui/
│   ├── __init__.py
│   ├── theme.py
│   ├── components.py
│   ├── screens.py
│   └── transformer_view.py
├── controllers/
│   ├── __init__.py
│   ├── keyboard.py
│   └── hardware.py
└── assets/
    └── fonts/
```

### Module responsibilities

- `main.py`: initialize Pygame, create the window, run the event loop, update state, render the current screen, and shut down cleanly.
- `config.py`: central settings for window size, FPS, fullscreen/resizable behavior, default values, valid ranges, increments, colors, typography, spacing, radii, animation, and feature flags.
- `core/transformer.py`: pure calculation and classification functions, with no Pygame dependencies.
- `ui/theme.py`: shared palette, fonts, and drawing helpers.
- `ui/components.py`: reusable buttons, value controls, sliders, knobs, cards, toggles, and other interface components.
- `ui/screens.py`: screen composition, application state, navigation, and user-facing content.
- `ui/transformer_view.py`: draw the transformer core, primary and secondary coils, labels, magnetic-flux visualization, and other transformer-specific graphics.
- `controllers/keyboard.py`: keyboard and mouse input.
- `controllers/hardware.py`: a placeholder or interface for future physical controls. It must not be required to run the desktop app and must not import GPIO/ADC libraries in the initial version.
- `README.md`: local setup, run instructions, keyboard shortcuts, project architecture, configuration guidance, and limitations.

Avoid putting the entire application in one file. Avoid duplicated calculations, hard-coded style values scattered throughout the UI, and circular imports.

## 5. Visual design direction

Create a polished, professional engineering-laboratory interface—not a basic school exercise or generic game menu.

Design goals:
- Full-screen-ready, responsive layout that also works in a resizable desktop window.
- Clear visual hierarchy and generous spacing.
- A modern technical dashboard with a restrained color palette.
- High-contrast text, readable labels, and consistent typography.
- Reusable cards and controls with consistent corner radii, padding, borders, and hover/focus states.
- A large central digital transformer illustration.
- Distinct visual colors for primary winding, secondary winding, core, and magnetic flux.
- A clearly visible results area.
- Smooth but restrained animations, with a setting to disable them.
- No decorative clutter that makes the engineering information harder to understand.
- Avoid relying on color alone to communicate operating mode; also show text labels.
- Keep all essential controls and values visible at the target window size without overlapping.

### Main simulator layout

The main screen should include:

1. **Header**
   - Application title: `Transformer Learning Workbench`.
   - Short subtitle describing the interactive transformer simulation.
   - A small `SIMULATION` or `READY` status indicator.

2. **Transformer visualization**
   - A clear, labeled single-phase transformer with a core and two windings.
   - Primary/input side and secondary/output side.
   - Animated or static magnetic-flux indicator through the core.
   - Clearly mark the illustration as a model/simulation.
   - Winding loop count may be illustrative; do not imply that a handful of drawn loops represents the exact numerical number of turns.

3. **Input controls**
   - Input/primary voltage (`Vp`).
   - Primary turns (`Np`).
   - Secondary turns (`Ns`).
   - A mode/operation selector for step-up and step-down demonstrations.
   - Reset control.
   - All controls must be usable by mouse and keyboard.

4. **Results**
   - Input voltage.
   - Primary turns.
   - Secondary turns.
   - Calculated output voltage (`Vs`).
   - Turns ratio.
   - Actual classification derived from the selected turns.
   - A brief explanation of why the result is step-up, step-down, or 1:1.
   - Make calculated/simulated values visibly distinct from actual electrical measurements.

5. **Navigation and help**
   - A concise help view, overlay, or visible shortcut hints.
   - Clear way to return to the simulator or home screen if a home screen is implemented.

The controls must be part of the **same application window and same monitor view** as the transformer graphic. Do not design the software around a separate physical control panel or a second display.

## 6. Control methods

Implement keyboard and mouse controls first. Keep input handling abstracted so a future physical controller can use the same application state.

### Keyboard/mouse mode

Provide a visible and understandable way to:
- Select which value is being edited.
- Increase or decrease the selected value.
- Click on-screen plus/minus controls or sliders.
- Select an operation/demo mode.
- Reset values.
- Open help or view keyboard shortcuts.

Suggested defaults (centralize in `config.py` and document them):
- `Tab`: select the next editable value.
- Arrow keys: adjust the selected value.
- `M`: switch the demonstration mode.
- `R`: reset values.
- `H`: show help.
- `Esc`: close an overlay or return to the previous screen; handle application exit deliberately.

Do not let keyboard shortcuts conflict with text input. Use consistent focus and selection feedback.

### Future physical-controller compatibility

The physical control concept includes:
- Black 3-pin potentiometer: input voltage.
- Blue 3-pin potentiometer: primary turns.
- Red 3-pin potentiometer: secondary turns.
- Green push button: operation selection/confirmation.
- Red and blue push buttons: decrease/increase or navigation, subject to the final control mapping.

In the initial desktop build:
- These controls are represented on screen and can be operated by mouse/keyboard.
- Do not require physical hardware to run.
- Do not pretend that the physical controls are connected or functioning.
- Keep a documented, optional hardware-controller interface for later.
- Ordinary 3-pin potentiometers provide analog signals; future integration will require a compatible ADC. Do not add or assume a specific ADC driver until the hardware is confirmed.
- Keep hardware logic separate from calculations and rendering.

If a controller-mode selector is included, distinguish `Keyboard/Mouse` from `Physical Controller (not connected)` until hardware integration is implemented.

## 7. Transformer calculations and correctness

Use the ideal transformer turns-ratio relationship:

`Vs = Vp * (Ns / Np)`

Where:
- `Vp`: primary/input voltage.
- `Vs`: calculated secondary/output voltage.
- `Np`: primary winding turns.
- `Ns`: secondary winding turns.

Classification:
- `Ns > Np`: `STEP-UP`.
- `Ns < Np`: `STEP-DOWN`.
- `Ns == Np`: `1:1 — NO VOLTAGE CHANGE`.

Requirements:
- Reject or safely handle zero/negative primary turns.
- Keep values within configured minimum and maximum ranges.
- Recalculate results whenever any relevant input changes.
- Avoid inconsistent displayed mode. The calculated classification must follow the turns ratio.
- If the user selects a step-up or step-down demonstration preset, make the selected turns consistent with that mode, or explain clearly when the selected turns produce a different result.
- Use predictable rounding for display without rounding the internal calculation prematurely.
- Put calculations in `core/transformer.py` and reuse those functions everywhere.
- Add simple tests or a validation checklist for representative step-up, step-down, and equal-turn cases.

Example:
- `Vp = 12 V`
- `Np = 100`
- `Ns = 200`
- `Vs = 24 V`
- Classification: `STEP-UP`.

## 8. Configuration and styling

The app should be easy to customize without editing many modules.

Centralize settings for:
- Window dimensions and minimum size.
- FPS and fullscreen/resizable behavior.
- Default input voltage, primary turns, and secondary turns.
- Minimum, maximum, and increment for each editable parameter.
- Theme palette and semantic colors.
- Font family and sizes.
- Component radii, margins, padding, gaps, and borders.
- Animation on/off and animation speed.
- Default control method.
- Display precision for voltage and ratio.
- Optional feature flags.

Avoid magic numbers in drawing and layout code where practical. Use shared theme helpers and reusable components. A style change should not require rewriting transformer calculations.

## 9. Interaction, rendering, and robustness

- Use a single clear Pygame event loop.
- Separate event handling, state updates, calculations, and rendering.
- Use `pygame.time.Clock` to control frame rate.
- Handle window resizing and recompute layouts correctly.
- Keep the interface responsive without unnecessary work each frame.
- Use `pygame.Rect` or equivalent geometry for reliable click targets.
- Ensure buttons work on click and show hover/focus feedback.
- Keep all interactive controls inside the visible window at supported sizes.
- Do not recreate fonts and other expensive objects every frame.
- Handle unexpected or invalid values gracefully.
- Use readable function and class names, docstrings where useful, and focused modules.
- Do not claim features are implemented unless the code actually implements them.
- Do not leave broken placeholder buttons or controls that appear functional but do nothing.
- When adding a placeholder for future hardware, label it clearly as not yet connected.

## 10. Development workflow for the AI

Work incrementally and verify each stage.

### Stage 1 — Inspect and plan
- Review the existing project files before editing them.
- Preserve any working code that already satisfies requirements.
- Identify missing features, bugs, duplicated code, and architectural problems.
- State the proposed file changes briefly.

### Stage 2 — Core model
- Implement and validate the transformer calculation functions.
- Test step-up, step-down, equal-turns, and invalid-input cases.
- Keep this module independent of Pygame.

### Stage 3 — Main UI
- Implement the application shell, responsive layout, reusable components, theme, and transformer illustration.
- Keep all controls on the same screen.

### Stage 4 — Keyboard and mouse interaction
- Wire all controls to shared application state.
- Ensure the displayed results update immediately.
- Implement help and reset behavior.

### Stage 5 — Visual refinement
- Improve spacing, alignment, contrast, typography, and interaction states.
- Confirm the UI fits at the configured window dimensions and at smaller supported sizes.
- Keep style settings centralized.

### Stage 6 — Validation
- Run the program where execution is available.
- Fix syntax errors, import errors, broken interactions, and layout problems.
- If execution is unavailable, state that clearly and provide exact manual verification steps.
- Do not claim that code was tested if it was not run.

### Stage 7 — Documentation
- Update `README.md` when controls, setup, configuration, or architecture changes.
- Explain which files changed and why.
- Give concise VS Code run instructions.

When asked to implement a feature, make the actual code changes rather than only describing the changes. Provide complete contents for files that need replacement, or create/update the project files directly when tools permit. Avoid giving partial snippets that leave the user unsure where they belong.

## 11. Acceptance checklist

The app is ready for its initial desktop prototype when:

- [ ] It launches locally in VS Code with Python and Pygame.
- [ ] The window can be resized without overlapping critical content.
- [ ] The transformer illustration has labeled primary and secondary sides.
- [ ] Input voltage, primary turns, and secondary turns can be adjusted with mouse and keyboard.
- [ ] Output voltage updates correctly using the ideal turns-ratio equation.
- [ ] Step-up, step-down, and 1:1 classifications are correct.
- [ ] Invalid values are handled safely.
- [ ] The same screen displays the transformer, inputs, and calculated results.
- [ ] Theme and layout settings are centralized and easy to modify.
- [ ] The app works without any physical controller attached.
- [ ] Future hardware support is isolated and clearly marked as unimplemented.
- [ ] The README documents how to run, operate, and configure the application.
- [ ] Any untested behavior is disclosed honestly.

## 12. Response style expected from the AI

Be practical, direct, and technically accurate. Prioritize working code and clear file-level instructions. Explain design decisions briefly when they affect maintainability, safety, or correctness. Do not unnecessarily introduce unrelated technologies or hardware setup. Do not assume physical controls are connected. Keep the implementation aligned with the thesis scope and the desktop-first workflow.
