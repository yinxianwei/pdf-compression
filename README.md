# PDF 压缩工具

Windows 桌面小工具（Python + tkinter），批量压缩 PDF：重采样图片、子集化字体、清理冗余对象。压缩后文件保存在原目录，文件名加 `_压缩`，原文件不动。

## 使用

1. 打开 `PDF压缩工具.exe`。
2. 点「选择 PDF 文件…」，可多选，也可把文件拖到 exe 上直接打开。
3. 选压缩强度后点「开始压缩」。

| 强度 | 图片判定 DPI | 目标 DPI | JPEG 质量 |
| --- | --- | --- | --- |
| 轻度（清晰优先） | 200 | 150 | 80 |
| 标准（推荐） | 150 | 120 | 65 |
| 强力（体积优先） | 100 | 72 | 45 |

若压缩后体积反而变大，会原样复制一份输出文件，不破坏原文件。

## 下载

到 [Releases](https://github.com/yinxianwei/pdf-compression/releases) 下载最新 `PDF压缩工具.exe`，单文件、免安装。

## 源码运行

```bash
uv sync
uv run pdfzip.py
```

## 自己打包

```bash
uv sync --dev
uv run pyinstaller --noconfirm --clean "PDF压缩工具.spec"
```

产物在 `dist/PDF压缩工具.exe`。

## 自动发布

发布流程由 `.github/workflows/release.yml` 负责，在 Windows runner 上打包：

1. 在 GitHub 上创建 release（打 tag，如 `v1.0.0`）并点 Publish。
2. Actions 自动构建，把 `PDF压缩工具.exe` 附加到该 release 供下载。
3. 也可手动触发 `Build EXE` workflow，产物在 Actions 的 Artifacts 里下载。
