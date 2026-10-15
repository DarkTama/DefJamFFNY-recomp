"""Cryptographic utilities and folder hashing for Def Jam: Fight for NY save files."""

import hmac
import hashlib


def calculate_save_dir(name: str) -> str:
    """Calculate the 12-character hexadecimal save folder name for a given profile name.
    Matches the original Xbox hashing algorithm and recomp defjam_save_directory_name().
    """
    hex_chars = "0123456789ABCDEF"
    hash_val = 0
    modulus = 0xFFFFFFFFFFC5

    for ch in name:
        hash_val = (hash_val * 65536 + ord(ch)) % modulus

    out = [""] * 12
    for i in range(12):
        out[11 - i] = hex_chars[(hash_val >> (4 * i)) & 15]
    return "".join(out)


def sign_save(data: bytearray, key: bytes = b"\x00" * 16) -> bytearray:
    """Sign a 22,928-byte Def Jam save file using the 3-tier HMAC-SHA1 architecture.
    
    Tier 1 (Seal 1 @ 0x10..0x23): HMAC-SHA1 of metadata block (0x4C..0x8B).
    Tier 2 (Seal 2 @ 0x24..0x37): HMAC-SHA1 of profile payload (0x8C..end).
    Tier 3 (Master Seal 3 @ 0x38..0x4B): HMAC-SHA1 of file header (0x00..0x37).
    """
    if len(data) < 0x8C:
        raise ValueError(f"Save data too small: {len(data)} bytes (minimum 0x8C required)")

    # Seal 1: Metadata block
    sig1 = hmac.new(key, data[0x4C:0x8C], hashlib.sha1).digest()
    data[0x10:0x24] = sig1

    # Seal 2: Fighter profile payload
    sig2 = hmac.new(key, data[0x8C:], hashlib.sha1).digest()
    data[0x24:0x38] = sig2

    # Seal 3: Master Seal over header
    sig3 = hmac.new(key, data[:0x38], hashlib.sha1).digest()
    data[0x38:0x4C] = sig3

    return data


def verify_save(data: bytes, key: bytes = b"\x00" * 16) -> bool:
    """Verify all 3 HMAC-SHA1 seals on a Def Jam save file."""
    if len(data) < 0x8C:
        return False

    v_sig1 = hmac.new(key, data[0x4C:0x8C], hashlib.sha1).digest()
    v_sig2 = hmac.new(key, data[0x8C:], hashlib.sha1).digest()
    v_sig3 = hmac.new(key, data[:0x38], hashlib.sha1).digest()

    return (
        data[0x10:0x24] == v_sig1
        and data[0x24:0x38] == v_sig2
        and data[0x38:0x4C] == v_sig3
    )
