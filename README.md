# Vivisector - Beast Within 简体中文补丁

这是《Vivisector - Beast Within》的简体中文补丁工程。

本仓库只包含中文翻译文本和补丁工具，不包含游戏本体、原版资源、改好的 `Vivisector.exe`，也不包含生成后的 `NewFont.tga`。

## 补丁原理

游戏原本使用单字节位图字体。补丁会做三件事：

1. 将中文文本按 GBK/CP936 编码放入原脚本目录。
2. 修改 `Vivisector.exe` 的文字渲染逻辑，让它把 GBK 双字节当作一个字符读取。
3. 使用本机中文字体生成 4096x4096 的 `NewFont.tga` 位图字库。

## 安装方法

准备：

- 自备已经安装或解包好的游戏目录。
- Windows 系统。
- Python 3。
- Pillow：

```bat
pip install pillow
```

一键安装：

```bat
python tools\install_cn_patch.py --game-dir "D:\Games\Vivisector - Beast Within"
```

如果你已经在游戏根目录打开命令行，也可以这样运行：

```bat
python "D:\Path\To\Vivisector-CN-Patch\tools\install_cn_patch.py"
```

安装脚本会自动：

- 复制 `translations` 里的中文文本。
- 修改 `Vivisector.exe`。
- 生成中文 `NewFont.tga`。
- 调整 `config.cfg`、`DATA\Scripts\init.cfg`、`DATA\Scripts\menu\menu.s` 里的字体尺寸设置。
- 处理旧脚本缓存 `DATA\history.bin`。

## 手动安装

也可以分步运行：

```bat
python tools\patch_vivisector_cn.py --game-dir "D:\Games\Vivisector - Beast Within"
python tools\make_gbk_font.py --game-dir "D:\Games\Vivisector - Beast Within"
```

然后把 `translations` 目录里的 `DATA` 文件夹复制到游戏根目录，覆盖同名文件。

## 编码说明

`translations` 目录下的游戏文本文件必须保持 GBK/CP936 编码。  
不要用 UTF-8 重新保存这些文件，否则游戏里会乱码或报错。

仓库里的 `.gitattributes` 已经将 `translations/**` 标记为二进制，避免 Git 自动改行尾或编码。

## 备份

工具会在游戏目录中生成这些备份：

- `Vivisector.exe.pre-cnpatch`
- `DATA\Textures\Interface\Text\EN\NewFont.tga.orig`
- `DATA\history.bin.pre-cnpatch`

这些文件用于回滚或重新生成补丁，不需要上传到 GitHub Release。

## 不建议上传的文件

请不要把这些文件提交到仓库：

- `Vivisector.exe`
- `*.dll`
- `DATA\Textures\Interface\Text\EN\NewFont.tga`
- 完整游戏 `DATA` 目录
- 日志文件
- 备份文件

## 免责声明

本项目只提供中文翻译和技术补丁工具。使用者需要自行拥有游戏本体。
