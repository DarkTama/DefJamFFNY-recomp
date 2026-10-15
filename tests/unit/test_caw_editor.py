"""Unit tests for CAW Editor crypto, directory hashing, and profile serialization."""

import os
import sys

# Ensure repository root is on path so tools module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tools.caw_editor.crypto import calculate_save_dir, sign_save, verify_save
from tools.caw_editor.profile import FighterProfile


def test_calculate_save_dir_darkon():
    """Verify that DARKON produces the exact 12-character folder hash."""
    assert calculate_save_dir("DARKON") == "0FF70F4A1334"


def test_calculate_save_dir_options():
    """Verify Options directory hash."""
    assert calculate_save_dir("Options") == "1A3F1B2E4ADD"


def test_3tier_sign_save_verification():
    """Verify that 3-tier save signing generates verifiable seals."""
    data = bytearray(b"\x00" * 22928)
    data[0:4] = b"20CM"
    data[0x4C:0x5C] = b"DJFFNY::User"
    data[0x8C:0x92] = b"TESTER"

    signed = sign_save(data)
    assert verify_save(signed) is True

    # Corrupting payload should fail verification
    corrupted = bytearray(signed)
    corrupted[0x00A0] ^= 0xFF
    assert verify_save(corrupted) is False


def test_profile_json_roundtrip():
    """Verify profile can serialize to and from JSON preset dict."""
    prof = FighterProfile()
    prof.name = "CHAMPION"
    prof.cash = 999999
    prof.dev_points = 12345
    prof.upper_strength = 99
    prof.female_model = "CARMEN"

    preset = prof.to_dict()
    assert preset["name"] == "CHAMPION"
    assert preset["cash"] == 999999
    assert preset["dev_points"] == 12345
    assert preset["stats"]["upper_strength"] == 99
    assert preset["female_model"] == "CARMEN"

    new_prof = FighterProfile()
    new_prof.from_dict(preset)
    assert new_prof.name == "CHAMPION"
    assert new_prof.cash == 999999
    assert new_prof.dev_points == 12345
    assert new_prof.upper_strength == 99
    assert new_prof.female_model == "CARMEN"
