"""Hardware controller interface placeholder for future physical controls."""

# Hardware integration is isolated - no GPIO/ADC imports in desktop build

class HardwareController:
    """Abstract hardware controller interface for future physical controls."""
    def __init__(self):
        self.connected = False
        self.status = "Hardware Disconnected"

    def is_connected(self):
        return self.connected

    def connect(self):
        # Placeholder - actual hardware connection handled in future phase
        self.connected = False
        self.status = "Hardware Disconnected (not implemented)"
        return False

    def read_inputs(self):
        """Return current analog/digital input values."""
        # Stub - returns empty/neutral values
        return {
            'pot_vp': None,
            'pot_np': None,
            'pot_ns': None,
            'btn_mode': False,
            'btn_inc': False,
            'btn_dec': False,
        }

    def update(self):
        """Poll hardware inputs if connected."""
        pass

    def get_status(self):
        return self.status


def get_hardware_controller():
    try:
        # Future: import hardware-specific libraries here behind checks
        # import RPi.GPIO as GPIO  # example - not done in desktop
        pass
    except Exception:
        pass
    return HardwareController()
