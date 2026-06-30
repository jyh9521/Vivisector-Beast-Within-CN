from pathlib import Path
import argparse
import shutil
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_text_lossless(path: Path) -> str:
    return path.read_text(encoding="latin-1")


def write_text_lossless(path: Path, text: str) -> None:
    path.write_text(text, encoding="latin-1", newline="")


def ensure_assignment(path: Path, key: str, value: str, prefix: str = "") -> None:
    text = read_text_lossless(path)
    lines = text.splitlines(keepends=True)
    needle = f"{prefix}{key}"
    replaced = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(needle):
            ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
            lines[i] = f"{prefix}{key}={value}{ending}"
            replaced = True
            break
    if not replaced:
        if lines and not lines[-1].endswith(("\n", "\r\n")):
            lines[-1] += "\r\n"
        lines.append(f"{prefix}{key}={value}\r\n")
    write_text_lossless(path, "".join(lines))


def ensure_config_line(path: Path, key: str, line_value: str) -> None:
    text = read_text_lossless(path)
    lines = text.splitlines(keepends=True)
    replaced = False
    for i, line in enumerate(lines):
        if line.strip().startswith(key):
            ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
            lines[i] = f"{key} = {line_value}{ending}"
            replaced = True
            break
    if not replaced:
        if lines and not lines[-1].endswith(("\n", "\r\n")):
            lines[-1] += "\r\n"
        lines.append(f"{key} = {line_value}\r\n")
    write_text_lossless(path, "".join(lines))


def patch_menu_hint_font(path: Path) -> None:
    text = read_text_lossless(path)
    lines = text.splitlines(keepends=True)
    in_hint = False
    depth = 0
    changed = False
    for i, line in enumerate(lines):
        if "procedure Render_Hint" in line:
            in_hint = True
            depth = 0
        if in_hint:
            depth += line.count("{") - line.count("}")
            if line.strip().startswith("textsize "):
                ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
                indent = line[: len(line) - len(line.lstrip())]
                lines[i] = f"{indent}textsize 16, 16  {ending}"
                changed = True
                break
            if depth <= 0 and "}" in line:
                in_hint = False
    if not changed:
        raise SystemExit(f"Could not find Render_Hint textsize in {path}")
    write_text_lossless(path, "".join(lines))


def copy_translations(game_dir: Path) -> None:
    source_root = REPO_ROOT / "translations"
    if not source_root.exists():
        raise SystemExit(f"translations directory not found: {source_root}")
    for src in source_root.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(source_root)
        dst = game_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"copied: {rel}")


def run_tool(name: str, game_dir: Path) -> None:
    subprocess.check_call([sys.executable, str(REPO_ROOT / "tools" / name), "--game-dir", str(game_dir)])


def main() -> None:
    parser = argparse.ArgumentParser(description="Install the Vivisector Simplified Chinese patch.")
    parser.add_argument("--game-dir", type=Path, default=Path.cwd(), help="Vivisector game directory.")
    parser.add_argument("--skip-font", action="store_true", help="Skip NewFont.tga generation.")
    parser.add_argument("--skip-exe", action="store_true", help="Skip Vivisector.exe patching.")
    args = parser.parse_args()

    game_dir = args.game_dir.resolve()
    if not (game_dir / "Vivisector.exe").exists():
        raise SystemExit(f"Vivisector.exe not found in: {game_dir}")

    copy_translations(game_dir)

    init_cfg = game_dir / "DATA" / "Scripts" / "init.cfg"
    config_cfg = game_dir / "config.cfg"
    menu_s = game_dir / "DATA" / "Scripts" / "menu" / "menu.s"
    ensure_assignment(init_cfg, "d.checkfiles", "1")
    ensure_assignment(init_cfg, "v.fontsizex", "16")
    ensure_assignment(init_cfg, "v.fontsizey", "16")
    ensure_config_line(config_cfg, "@v.fontsizex", "16")
    ensure_config_line(config_cfg, "@v.fontsizey", "16")
    patch_menu_hint_font(menu_s)
    print("patched script settings")

    if not args.skip_exe:
        run_tool("patch_vivisector_cn.py", game_dir)
    if not args.skip_font:
        run_tool("make_gbk_font.py", game_dir)

    history = game_dir / "DATA" / "history.bin"
    if history.exists():
        backup = game_dir / "DATA" / "history.bin.pre-cnpatch"
        if not backup.exists():
            history.rename(backup)
            print("renamed DATA\\history.bin to DATA\\history.bin.pre-cnpatch")
        else:
            history.unlink()
            print("removed DATA\\history.bin")

    print("Chinese patch installed.")


if __name__ == "__main__":
    main()
