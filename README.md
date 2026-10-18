# 《Vivisector: Beast Within》简体中文汉化

Vivisector: Beast Within 的简体中文翻译与补丁工具工程。仓库保存译文、可执行文件补丁脚本与字库生成工具，不提供完整游戏或已修改的游戏程序。

## 支持环境与当前状态

当前提供**源码安装方式**，尚无 GitHub Release 玩家安装包。需要 Windows、Python 3、Pillow，以及自行安装或解包的游戏。

补丁依赖游戏可执行文件的具体字节布局，不能视为适配所有发行版本；脚本会检查目标指令，匹配失败时应核对版本，不跳过检测继续写入。仓库尚未提供完整通关验收结论。

## 安装 / 使用

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

游戏 EXE / DLL、完整 DATA、原版或生成字库、日志和备份不提交源码仓库。使用者需自行准备游戏和可用于字库生成的字体。
