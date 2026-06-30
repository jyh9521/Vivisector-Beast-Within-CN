from pathlib import Path
import argparse
import struct


IMAGE_BASE = 0x400000


def rel32(src_va: int, dst_va: int) -> bytes:
    return struct.pack("<i", dst_va - (src_va + 5))


def patch_at(buf: bytearray, off: int, expected: bytes, replacement: bytes, name: str) -> None:
    current = bytes(buf[off : off + len(expected)])
    if current == replacement[: len(expected)] and len(replacement) == len(expected):
        print(f"{name}: already patched")
        return
    if current != expected:
        raise SystemExit(
            f"{name}: unexpected bytes at 0x{off:X}: "
            f"{current.hex(' ')} != {expected.hex(' ')}"
        )
    buf[off : off + len(replacement)] = replacement
    print(f"{name}: patched")


def build_gbk_cave(cave_va: int, update_saved_index: bool = True) -> bytes:
    draw_va = 0x004A6B76
    color_va = 0x004A6A9C

    code = bytearray()
    # eax = current byte. ecx is the byte index and ebp points at the string.
    code += bytes.fromhex("0F B6 04 29")  # movzx eax, byte ptr [ecx+ebp]
    ascii_offset = 46 if update_saved_index else 42
    code += bytes.fromhex("3C 80")        # cmp al, 80h
    code += bytes([0x72, ascii_offset - 8])        # jb ascii
    code += bytes.fromhex("3C FE")        # cmp al, FEh
    code += bytes([0x77, ascii_offset - 12])       # ja ascii
    code += bytes.fromhex("0F B6 54 29 01")  # movzx edx, byte ptr [ecx+ebp+1]
    code += bytes.fromhex("84 D2")        # test dl, dl
    code += bytes([0x74, ascii_offset - 21])       # jz ascii
    code += bytes.fromhex("80 FA 40")     # cmp dl, 40h
    code += bytes([0x72, ascii_offset - 26])       # jb ascii
    code += bytes.fromhex("80 FA FE")     # cmp dl, FEh
    code += bytes([0x77, ascii_offset - 31])       # ja ascii
    code += bytes.fromhex("C1 E0 08")     # shl eax, 8
    code += bytes.fromhex("0B C2")        # or eax, edx
    code += bytes.fromhex("41")           # inc ecx; loop increment consumes trail byte
    if update_saved_index:
        code += bytes.fromhex("89 4C 24 24")  # mov [esp+24h], ecx
    code += b"\xE9" + rel32(cave_va + len(code), draw_va)

    ascii_va = cave_va + len(code)
    assert ascii_va == cave_va + ascii_offset
    code += bytes.fromhex("8B 94 24 D0 00 00 00")  # mov edx, [esp+D0h]
    code += bytes.fromhex("85 D2")                 # test edx, edx
    code += b"\x0F\x84" + struct.pack("<i", draw_va - (cave_va + len(code) + 6))
    code += bytes.fromhex("83 F8 5E")              # cmp eax, '^'
    code += b"\x0F\x85" + struct.pack("<i", draw_va - (cave_va + len(code) + 6))
    code += b"\xE9" + rel32(cave_va + len(code), color_va)
    return bytes(code)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Patch Vivisector.exe to render GBK Chinese text.")
    parser.add_argument(
        "--game-dir",
        type=Path,
        default=Path.cwd(),
        help="Vivisector game directory. Defaults to the current working directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.game_dir.resolve()
    exe = root / "Vivisector.exe"
    backup = root / "Vivisector.exe.pre-cnpatch"
    if not exe.exists():
        raise SystemExit(f"Vivisector.exe not found: {exe}")

    data = bytearray(exe.read_bytes())
    if not backup.exists():
        backup.write_bytes(data)
        print(f"backup: {backup.name}")
    else:
        print(f"backup: {backup.name} already exists")

    patch_at(
        data,
        0x0208,
        struct.pack("<I", 0x000EF690),
        struct.pack("<I", 0x000F0000),
        ".text virtual size",
    )

    cave_off = 0x0F06A6
    cave_va = IMAGE_BASE + cave_off
    cave = build_gbk_cave(cave_va)
    old_cave = build_gbk_cave(cave_va, update_saved_index=False)
    cave_expected = b"\x00" * len(cave)
    if bytes(data[cave_off : cave_off + len(cave)]) == cave:
        print("gbk parser cave: already patched")
    elif (
        bytes(data[cave_off : cave_off + len(old_cave)]) == old_cave
        and bytes(data[cave_off + len(old_cave) : cave_off + len(cave)]) == b"\x00" * (len(cave) - len(old_cave))
    ):
        data[cave_off : cave_off + len(cave)] = cave
        print("gbk parser cave: upgraded")
    else:
        patch_at(data, cave_off, cave_expected, cave, "gbk parser cave")

    hook_off = 0x0A6A80
    hook_va = IMAGE_BASE + hook_off
    original_hook = bytes.fromhex(
        "8B 94 24 D0 00 00 00 85 D2 0F B6 04 29 0F 84 E3 00 00 00 "
        "83 F8 5E 0F 85 DA 00 00 00"
    )
    hook = b"\xE9" + rel32(hook_va, cave_va) + b"\x90" * (len(original_hook) - 5)
    patch_at(data, hook_off, original_hook, hook, "text loop hook")

    # Change glyph grid from 16 columns to 256 columns:
    #   col = glyph & 0xff, row = glyph >> 8.
    patch_at(data, 0x0A6B7F, bytes.fromhex("83 E1 0F"), bytes.fromhex("0F B6 C8"), "glyph column")
    patch_at(data, 0x0A6B97, bytes.fromhex("C1 F8 04"), bytes.fromhex("C1 F8 08"), "glyph row")

    # In this function only, change UV scale from 1/256 to 1/4096.
    old_const = struct.pack("<I", 0x004F1E88)
    new_const = struct.pack("<I", 0x004F1F58)
    for off in (0x0A6BE1, 0x0A6BF8, 0x0A6C5C, 0x0A6CBB):
        patch_at(data, off, old_const, new_const, f"uv scale 0x{off:X}")

    exe.write_bytes(data)
    print("done")


if __name__ == "__main__":
    main()
