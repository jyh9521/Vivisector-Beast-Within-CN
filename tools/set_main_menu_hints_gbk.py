from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MENU = ROOT / "DATA" / "Scripts" / "text" / "EN" / "interface" / "menu.cfg"


REPLACEMENTS = {
    "Click to play story-driven single player game.": "\u70b9\u51fb\u5f00\u59cb\u5267\u60c5\u6a21\u5f0f\u3002",
    "Load previously saved games.": "\u8f7d\u5165\u5df2\u4fdd\u5b58\u7684\u6e38\u620f\u3002",
    "Load selected game.": "\u8f7d\u5165\u9009\u4e2d\u7684\u5b58\u6863\u3002",
    "Save current game.": "\u4fdd\u5b58\u5f53\u524d\u6e38\u620f\u3002",
    "Customize your controls, video, audio and game settings.": "\u8c03\u6574\u64cd\u4f5c\u3001\u753b\u9762\u3001\u97f3\u9891\u548c\u6e38\u620f\u8bbe\u7f6e\u3002",
    "Game credits.": "\u5236\u4f5c\u4eba\u5458\u540d\u5355\u3002",
    "Click to quit the game.": "\u70b9\u51fb\u9000\u51fa\u6e38\u620f\u3002",
    "Easy difficulty.": "\u7b80\u5355\u96be\u5ea6\u3002",
    "Medium difficulty.": "\u666e\u901a\u96be\u5ea6\u3002",
    "Hard difficulty.": "\u56f0\u96be\u96be\u5ea6\u3002",
    "Extreme difficulty.": "\u6781\u9650\u96be\u5ea6\u3002",
    "Click to start the game.": "\u70b9\u51fb\u5f00\u59cb\u6e38\u620f\u3002",
    "Back to Main menu.": "\u8fd4\u56de\u4e3b\u83dc\u5355\u3002",
}


def main() -> None:
    text = MENU.read_bytes().decode("gbk")
    changed = 0
    for old, new in REPLACEMENTS.items():
        if old in text:
            text = text.replace(old, new)
            changed += 1
    MENU.write_bytes(text.encode("gbk"))
    print(f"updated {changed} strings in {MENU}")


if __name__ == "__main__":
    main()
