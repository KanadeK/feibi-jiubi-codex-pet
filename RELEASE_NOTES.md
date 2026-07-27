# 菲比啾比发布说明

## v1.0.1

这个补丁版本修复 Codex Desktop 无法识别宠物包的问题：

- 将 1536 × 1872、8 × 9 图集正确声明为 Sprite v1
- 同步修正 README 与预览站的一键安装深链
- 让验证器按 Sprite 版本检查对应图集尺寸
- 增加 v2 元数据与 v1 图集不匹配的回归测试
- 在 CI 重建资源前验证已提交的 `checksums.txt`
- 支持通过 `FEIBI_JIUBI_SOURCE_ROOT` 在本地测试 Bash 安装器

## v1.0.0

这个版本提供一个可直接加载到 Codex Desktop 的完整宠物包。

## 包含内容

- 9 种 Codex 原生状态动画
- 1536 × 1872 透明 lossless WebP 图集
- `spriteVersionNumber: 1` 元数据
- Windows、macOS 和 Linux 安装脚本
- SHA-256 下载校验与升级备份
- 可复现的素材构建脚本
- 图集结构、透明度与帧数测试
- 动画预览页与完整来源说明

安装完成后，在 Settings > Pets 中刷新并选择“菲比啾比”。
