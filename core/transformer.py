"""Pure transformer calculation logic with no Pygame dependencies."""

try:
    from config import PRECISION_RATIO
except Exception:
    PRECISION_RATIO = 3

from dataclasses import dataclass
from typing import Tuple, Dict, Any


@dataclass
class TransformerState:
    """Input state for transformer calculations."""
    primary_voltage: float
    primary_turns: int
    secondary_turns: int
    frequency: float = 60.0


@dataclass
class TransformerResult:
    """Result from transformer calculations."""
    secondary_voltage: float
    turns_ratio: float
    classification: str
    classification_detail: str
    primary_voltage: float = 0.0
    primary_turns: int = 0
    secondary_turns: int = 0


def _clamp_primary_turns(np: int) -> int:
    """Prevent division by zero and handle invalid primary turns."""
    if np is None or np <= 0:
        return 1
    return np


def calculate_turns_ratio(np: int, ns: int) -> float:
    """Calculate turns ratio (Ns/Np)."""
    np_c = _clamp_primary_turns(np)
    return ns / np_c if np_c != 0 else 0.0


def calculate_output_voltage(vp: float = None, np: int = None, ns: int = None, state: TransformerState = None) -> TransformerResult:
    """
    Calculate secondary voltage using ideal transformer turns-ratio.

    Vs = Vp * (Ns / Np)
    Accepts either individual parameters or a TransformerState object.
    """
    if state is not None:
        np_count = state.primary_turns
        ns_count = state.secondary_turns
        vp_val = state.primary_voltage
    else:
        np_count = np
        ns_count = ns
        vp_val = vp

    # Safety: reject zero or negative primary turns
    if np_count is None or np_count <= 0:
        np_count_clamped = 1
    else:
        np_count_clamped = np_count

    if ns_count is None:
        ns_count = np_count_clamped

    if vp_val is None:
        vp_val = 0.0

    # Calculate turns ratio
    ratio = ns_count / np_count_clamped if np_count_clamped != 0 else 0

    # Calculate secondary voltage
    vs = vp_val * ratio

    # Classify operation mode
    if np_count is None or np_count <= 0:
        classification = "INVALID"
        detail = "Primary turns must be > 0"
    elif ns_count > np_count:
        classification = "STEP-UP"
        detail = f"Ns ({ns_count}) > Np ({np_count}) — Vs ({vs:.4g}) > Vp ({vp_val:.4g})"
    elif ns_count < np_count:
        classification = "STEP-DOWN"
        detail = f"Ns ({ns_count}) < Np ({np_count}) — Vs ({vs:.4g}) < Vp ({vp_val:.4g})"
    else:
        classification = "1:1 RATIO"
        detail = f"Ns ({ns_count}) == Np ({np_count}) — Vs == Vp ({vp_val:.4g})"

    return TransformerResult(
        secondary_voltage=round(vs, 4),
        turns_ratio=round(ratio, PRECISION_RATIO),
        classification=classification,
        classification_detail=detail,
        primary_voltage=vp_val,
        primary_turns=np_count if np_count is not None and np_count > 0 else 0,
        secondary_turns=ns_count,
    )


def classify_turns(ns: int, np: int) -> Tuple[str, str]:
    """
    Classify transformer operation based on turns ratio.

    Returns (classification, detail) tuple.
    """
    if np is None or np <= 0:
        return "INVALID", "Primary turns must be > 0"

    ratio = ns / np

    if ns > np:
        return "STEP-UP", f"Ns ({ns}) > Np ({np}) (ratio={ratio:.3g})"
    elif ns < np:
        return "STEP-DOWN", f"Ns ({ns}) < Np ({np}) (ratio={ratio:.3g})"
    else:
        return "1:1 RATIO", f"Ns ({ns}) == Np ({np}) (ratio={ratio:.3g})"
