"""Profile model representing a Def Jam: Fight for NY character and career state."""

import json
import os
import shutil
import struct
from typing import Dict, Any, Optional

from .crypto import calculate_save_dir, sign_save, verify_save


class FighterProfile:
    """Represents a playable fighter profile and career state in 20CM format."""

    def __init__(self, raw_data: Optional[bytearray] = None):
        if raw_data is not None:
            self.raw_data = bytearray(raw_data)
            self._parse()
        else:
            self.raw_data = bytearray()
            self._init_defaults()

    def _init_defaults(self):
        self.name = "NEW_FIGHTER"
        self.cash = 1000
        self.dev_points = 100
        self.total_dev_points = 100
        self.voice_id = 4
        self.body_type_upper = 2
        self.body_type_lower = 1
        self.fighting_style_1 = 0x1B000003
        self.fighting_style_2 = 0x1B00001C
        self.upper_strength = 35
        self.lower_strength = 35
        self.speed = 35
        self.toughness = 35
        self.charisma = 35
        self.female_model = "NONE"

    def _parse(self):
        d = self.raw_data
        if len(d) < 0x200:
            raise ValueError(f"Invalid save data size: {len(d)}")

        # Fighter name (at 0x8C, max 16 chars)
        raw_name = d[0x8C:0xA0]
        null_idx = raw_name.find(b"\x00")
        if null_idx != -1:
            raw_name = raw_name[:null_idx]
        self.name = raw_name.decode("ascii", errors="replace")

        # Career Economy
        self.cash = struct.unpack_from("<I", d, 0x00A0)[0]
        self.dev_points = struct.unpack_from("<I", d, 0x00A8)[0]
        self.total_dev_points = struct.unpack_from("<I", d, 0x00AC)[0]

        # Body Types & Voice
        self.body_type_upper = struct.unpack_from("<I", d, 0x00B0)[0]
        self.body_type_lower = struct.unpack_from("<I", d, 0x00B4)[0]
        self.voice_id = struct.unpack_from("<I", d, 0x00BC)[0]

        # Fighting Styles
        self.fighting_style_1 = struct.unpack_from("<I", d, 0x00C0)[0]
        self.fighting_style_2 = struct.unpack_from("<I", d, 0x00C4)[0]

        # Core Combat Attributes
        self.upper_strength = struct.unpack_from("<I", d, 0x017C)[0]
        self.lower_strength = struct.unpack_from("<I", d, 0x0180)[0]
        self.speed = struct.unpack_from("<I", d, 0x0184)[0]
        self.toughness = struct.unpack_from("<I", d, 0x0188)[0]
        self.charisma = struct.unpack_from("<I", d, 0x018C)[0]

        self.female_model = "NONE"

    def apply_to_binary(self) -> bytearray:
        """Apply modified fields into self.raw_data and return resigned binary."""
        if not self.raw_data:
            raise ValueError("No base binary save template loaded")

        d = self.raw_data

        # Name
        encoded_name = self.name.encode("ascii", errors="replace")[:15]
        name_block = encoded_name + b"\x00" * (20 - len(encoded_name))
        d[0x8C:0xA0] = name_block

        # Career Economy
        struct.pack_into("<I", d, 0x00A0, self.cash)
        struct.pack_into("<I", d, 0x01E8, self.cash)
        struct.pack_into("<I", d, 0x00A8, self.dev_points)
        struct.pack_into("<I", d, 0x00AC, self.total_dev_points)

        # Body & Voice
        struct.pack_into("<I", d, 0x00B0, self.body_type_upper)
        struct.pack_into("<I", d, 0x00B4, self.body_type_lower)
        struct.pack_into("<I", d, 0x00BC, self.voice_id)

        # Fighting Styles
        struct.pack_into("<I", d, 0x00C0, self.fighting_style_1)
        struct.pack_into("<I", d, 0x00C4, self.fighting_style_2)

        # Attributes
        struct.pack_into("<I", d, 0x017C, self.upper_strength)
        struct.pack_into("<I", d, 0x0180, self.lower_strength)
        struct.pack_into("<I", d, 0x0184, self.speed)
        struct.pack_into("<I", d, 0x0188, self.toughness)
        struct.pack_into("<I", d, 0x018C, self.charisma)

        # Re-sign all 3 seals
        return sign_save(d)

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to serializable JSON preset."""
        return {
            "name": self.name,
            "cash": self.cash,
            "dev_points": self.dev_points,
            "total_dev_points": self.total_dev_points,
            "voice_id": self.voice_id,
            "body_type_upper": self.body_type_upper,
            "body_type_lower": self.body_type_lower,
            "fighting_style_1": self.fighting_style_1,
            "fighting_style_2": self.fighting_style_2,
            "stats": {
                "upper_strength": self.upper_strength,
                "lower_strength": self.lower_strength,
                "speed": self.speed,
                "toughness": self.toughness,
                "charisma": self.charisma,
            },
            "female_model": self.female_model,
        }

    def from_dict(self, data: Dict[str, Any]):
        """Load values from JSON preset dictionary."""
        self.name = data.get("name", self.name)
        self.cash = data.get("cash", self.cash)
        self.dev_points = data.get("dev_points", self.dev_points)
        self.total_dev_points = data.get("total_dev_points", self.total_dev_points)
        self.voice_id = data.get("voice_id", self.voice_id)
        self.body_type_upper = data.get("body_type_upper", self.body_type_upper)
        self.body_type_lower = data.get("body_type_lower", self.body_type_lower)
        self.fighting_style_1 = data.get("fighting_style_1", self.fighting_style_1)
        self.fighting_style_2 = data.get("fighting_style_2", self.fighting_style_2)

        stats = data.get("stats", {})
        self.upper_strength = stats.get("upper_strength", self.upper_strength)
        self.lower_strength = stats.get("lower_strength", self.lower_strength)
        self.speed = stats.get("speed", self.speed)
        self.toughness = stats.get("toughness", self.toughness)
        self.charisma = stats.get("charisma", self.charisma)
        self.female_model = data.get("female_model", "NONE")

    @classmethod
    def load_from_file(cls, filepath: str) -> "FighterProfile":
        with open(filepath, "rb") as f:
            data = bytearray(f.read())
        return cls(data)

    def save_to_directory(self, base_user_data_dir: str):
        """Save profile and metadata to the appropriate hashed Xbox folder."""
        folder_hash = calculate_save_dir(self.name)
        save_folder = os.path.join(base_user_data_dir, folder_hash)
        os.makedirs(save_folder, exist_ok=True)

        # 1. Write signed binary profile
        signed_data = self.apply_to_binary()
        profile_path = os.path.join(save_folder, self.name)
        with open(profile_path, "wb") as f:
            f.write(signed_data)

        # 2. Write SaveMeta.xbx (UTF-16LE with BOM)
        meta_path = os.path.join(save_folder, "SaveMeta.xbx")
        meta_content = f"Name={self.name}\r\n".encode("utf-16")
        with open(meta_path, "wb") as f:
            f.write(meta_content)

        return save_folder
