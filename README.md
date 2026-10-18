# 《Vivisector: Beast Within》简体中文汉化

Vivisector: Beast Within 的简体中文翻译与补丁工具工程。源码仓库保存译文、可执行文件补丁脚本与字库生成工具；玩家安装包见下方 Release，不含完整游戏。

## 支持环境与当前状态

已发布 **[v1.0 汉化补丁](https://github.com/jyh9521/Vivisector-Beast-Within-CN/releases/tag/v1.0)**（2026-10-18）。Windows 玩家可下载现成安装包，直接覆盖安装，**无需安装 Python 或 Pillow**；自行构建补丁时仍可使用下方源码安装方式。两种方式均需自行准备游戏本体。

Release 包含已修改的 `Vivisector.exe`，尚未提供适用于所有游戏发行版本的兼容性结论。源码补丁依赖可执行文件的具体字节布局，脚本会检查目标指令，匹配失败时应核对版本，不跳过检测继续写入。仓库尚未提供完整通关验收结论。

## 安装 / 使用

### Release 安装（推荐玩家使用）

1. 下载 **[v1.0.7z](https://github.com/jyh9521/Vivisector-Beast-Within-CN/releases/download/v1.0/v1.0.7z)**，或从 [Releases 页面](https://github.com/jyh9521/Vivisector-Beast-Within-CN/releases)选择版本；不要将 GitHub 自动生成的 `Source code` 压缩包当作玩家安装包。
2. 退出游戏，备份完整游戏目录，尤其是 `Vivisector.exe`、`config.cfg` 和 `DATA` 下将被覆盖的文件。
3. 解压 `v1.0.7z`，将包内文件复制到包含 `Vivisector.exe` 的游戏根目录，合并 `DATA` 文件夹并覆盖同名文件。补丁包含程序、中文文本、中文字库及显示配置，不必再运行源码安装脚本。
4. 使用 `Vivisector.exe` 启动游戏。包内 `config.cfg` 会覆盖原有设置，安装后按需重新调整分辨率、音量等选项。

Release 覆盖安装不会自动处理旧缓存；如果已有 `DATA\history.bin`，可在退出游戏后将其改名为 `history.bin.pre-cnpatch` 并保留备份，与源码安装器的缓存处理保持一致。

### 源码安装（开发 / 自行构建）

需要 Windows、Python 3、Pillow，以及自行安装或解包的游戏。

先备份完整游戏目录，尤其是脚本、配置与将被覆盖的文本。下载或克隆本仓库，在仓库根目录运行：

```powershell
python -m pip install Pillow
python tools\install_cn_patch.py --game-dir "D:\Games\Vivisector - Beast Within"
```

安装脚本会复制中文文本、修改 `Vivisector.exe`、生成 `NewFont.tga`、调整字体尺寸与菜单脚本，并处理旧缓存 `DATA\history.bin`。完成后使用游戏原入口启动，安装工具不代替游戏本体。

## 技术摘要

原游戏使用单字节位图字体。本补丁将脚本文本按 **GBK / CP936** 编码写入，并修改文字渲染逻辑，将双字节字符作为一个字形读取；字库工具利用本机中文字体生成 **4096×4096** 的 `NewFont.tga`。

这套编码是当前引擎适配约束，不应直接替换为 UTF-8，也不代表其他语言必须采用同样的编码方案。

## 分步构建

需要单独检查程序与字库时，可使用：

```powershell
python tools\patch_vivisector_cn.py --game-dir "D:\Games\Vivisector - Beast Within"
python tools\make_gbk_font.py --game-dir "D:\Games\Vivisector - Beast Within"
```

然后将 `translations\DATA` 复制到游戏目录。分步命令不会代替一键安装器里的配置、菜单尺寸与缓存处理，完整安装优先使用 `install_cn_patch.py`。

## 备份与恢复

### Release 覆盖安装

直接复制文件不会自动生成备份。恢复时退出游戏，还原安装前的完整目录备份，包括原程序、配置、文本和字库；若曾改名缓存，也一并恢复。不要仅还原 `Vivisector.exe` 后继续混用汉化字库或脚本。

### 源码安装

工具按对应文件是否存在生成备份：

- `Vivisector.exe.pre-cnpatch`
- `DATA\Textures\Interface\Text\EN\NewFont.tga.orig`
- `DATA\history.bin.pre-cnpatch`

这些只覆盖部分修改，**不是完整卸载备份**；译文、`config.cfg`、`init.cfg` 和 `menu.s` 等仍需依靠安装前备份恢复。恢复时退出游戏，优先还原完整目录备份，避免混用不同安装版本的文件。

## 仓库结构与维护

| 路径 | 内容 |
| --- | --- |
| `translations/` | GBK / CP936 游戏译文与脚本 |
| `tools/install_cn_patch.py` | 一键安装入口 |
| `tools/patch_vivisector_cn.py` | 可执行文件文字路径补丁 |
| `tools/make_gbk_font.py` | 中文位图字库生成 |
| `tools/set_main_menu_hints_gbk.py` | 菜单提示文本处理 |

译文保持原编码与控制语法，不用 UTF-8 重存。`.gitattributes` 将 `translations/**` 视为二进制，避免 Git 自动转换行尾或编码。

修改后分别检查程序指令匹配、字库生成、文本编码及游戏内菜单 / 字幕显示；脚本成功不等于完整实机验收。

## 来源与许可

原游戏、程序、素材及系统字体归各自权利人所有。仓库当前未提供项目级 `LICENSE`，不额外宣称统一开源许可。

游戏 EXE / DLL、完整 DATA、原版或生成字库、日志和备份不提交源码仓库。Release 安装包与源码仓库内容不同，v1.0 包含已修改程序及生成字库。使用者需自行准备游戏；从源码生成字库时还需准备可用的中文字体。
