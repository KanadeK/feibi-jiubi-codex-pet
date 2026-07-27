# 菲比啾比 Codex Pet

<p align="center">
  <img src="media/showcase.gif" alt="菲比啾比九种 Codex 状态动画" width="240">
</p>

<p align="center">
  一个可直接加载到 Codex Desktop 的原创同人桌面宠物包。
</p>

<p align="center">
  <a href="https://kanadek.github.io/feibi-jiubi-codex-pet/">动画预览</a> |
  <a href="https://learn.chatgpt.com/docs/pets">Codex Pets 官方说明</a> |
  <a href="NOTICE.md">版权与来源说明</a>
</p>

## 安装

### 一键打开 Codex 安装页

[在 Codex 中安装菲比啾比](codex://pets/install?name=%E8%8F%B2%E6%AF%94%E5%95%BE%E6%AF%94&imageUrl=https%3A%2F%2Fraw.githubusercontent.com%2FKanadeK%2Ffeibi-jiubi-codex-pet%2Fmain%2Fpet%2Fspritesheet.webp&spriteVersionNumber=1)

如果浏览器不允许打开 `codex://` 链接，可使用下列脚本或手动安装。

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/KanadeK/feibi-jiubi-codex-pet/main/scripts/install.ps1 | iex
```

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/KanadeK/feibi-jiubi-codex-pet/main/scripts/install.sh | sh
```

安装器会校验 SHA-256。已有同 ID 宠物会先备份到 `~/.codex/pet-backups/`，不会直接删除。

### 手动安装

把这两个文件放入 `~/.codex/pets/feibi-jiubi/`：

```text
pet/pet.json
pet/spritesheet.webp
```

然后打开 **Settings > Pets**，选择 **Refresh**，再选择 **菲比啾比**。使用 `/pet` 或 **Wake Pet** 唤醒她。

## 九种动作

| Codex 状态 | 动画 |
| --- | --- |
| 空闲陪伴 | ![空闲](media/actions/idle.gif) |
| 向右奔跑 | ![向右奔跑](media/actions/running-right.gif) |
| 向左奔跑 | ![向左奔跑](media/actions/running-left.gif) |
| 挥手问候 | ![挥手](media/actions/waving.gif) |
| 开心跳跃 | ![跳跃](media/actions/jumping.gif) |
| 任务受阻 | ![任务受阻](media/actions/failed.gif) |
| 等你回复 | ![等待](media/actions/waiting.gif) |
| 忙碌工作 | ![忙碌](media/actions/running.gif) |
| 等你验收 | ![验收](media/actions/review.gif) |

## 官方格式

- 图集：`1536 × 1872` lossless WebP
- 网格：`8 × 9`
- 单格：`192 × 208`
- 背景：透明 RGBA
- 元数据：`pet.json`
- Sprite 版本：`1`
- 文件大小：小于官方 20 MiB 上传限制

`scripts/validate_pet.py` 会逐格检查已用帧、空白帧、透明度、尺寸、文件类型和元数据。

## 从源码构建

```powershell
uv venv .venv
uv pip install --python .venv\Scripts\python.exe -r requirements-dev.txt
.venv\Scripts\python.exe scripts\build_assets.py
.venv\Scripts\python.exe scripts\validate_pet.py
.venv\Scripts\python.exe -m pytest -q
```

macOS / Linux 将 Python 路径改为 `.venv/bin/python`。

生成流程只依赖仓库内的透明九姿势角色板。构建脚本会裁切姿势、生成状态动效、打包图集、输出 GIF 预览并更新校验和。

## 素材来源

- 用户提供的参考图只用于视觉方向，不在仓库中分发。
- 角色板由 OpenAI 内置图像生成工具重新绘制。
- 透明背景由本地图像处理辅助脚本生成。
- 动作帧、图集、GIF 和校验和由仓库脚本确定性生成。
- 本项目没有复制其他菲比啾比仓库的图片、脚本或提交历史。

完整生成提示词见 [artwork/PROMPT.md](artwork/PROMPT.md)。版权边界与非官方声明见 [NOTICE.md](NOTICE.md)。

## 贡献者

首个公开版本由 [KanadeK](https://github.com/KanadeK) 提交和发布。项目没有添加自动生成的 `Co-authored-by` 条目，也没有继承其他仓库的 Git 历史。完整名单见 [AUTHORS.md](AUTHORS.md)。

## English

Feibi Jiubi is an unofficial, non-commercial Codex Desktop pet package with nine native status animations. The package contains an original generated pose board, a reproducible atlas builder, validation tests, install scripts, and a small preview site.

## License

Original code and documentation are released under the [MIT License](LICENSE). Character names, recognizable character traits, and third-party rights are not relicensed. See [NOTICE.md](NOTICE.md).
