#!/usr/bin/env python3
"""Render illustrative README GIFs and static previews; requires Pillow.

These are authored workflow simulations, never recordings or completed runs.
Pillow and a CJK font are development-only dependencies, not skill requirements.
"""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 900
BG = "#eef3f4"
INK = "#183138"
MUTED = "#526d76"
GREEN = "#08795d"
FONT = BOLD = None


def text(draw, xy, value, size=20, fill=INK, bold=False, max_width=None):
    font = ImageFont.truetype(str(BOLD if bold else FONT), size)
    box = draw.textbbox(xy, value, font=font)
    if max_width is not None and box[2] - box[0] > max_width:
        raise ValueError(f"Text exceeds {max_width}px: {value}")
    if box[2] > W - 20 or box[3] > H - 12:
        raise ValueError(f"Text outside canvas: {value}")
    draw.text(xy, value, font=font, fill=fill)


def wrapped(draw, xy, value, width, size=20, fill=INK, bold=False, line_height=34):
    font = ImageFont.truetype(str(BOLD if bold else FONT), size)
    line = ""
    y = xy[1]
    for char in value:
        if draw.textlength(line + char, font=font) > width and line:
            text(draw, (xy[0], y), line, size, fill, bold, width)
            y += line_height
            line = char
        else:
            line += char
    if line:
        text(draw, (xy[0], y), line, size, fill, bold, width)
    return y + line_height


def panel(draw, box, fill="white", outline="#d2dfe1", radius=16):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=1)


def base(case, stage):
    im = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, W, 110), fill="#112a30")
    text(draw, (44, 19), "SP / SKILL DYNAMIC SELECTOR", 19, "#8ce2c2", True)
    text(draw, (44, 52), case["title"], 30, "white", True)
    panel(draw, (806, 36, 1156, 77), "#244149", "#496069", 20)
    text(draw, (825, 44), "流程模拟演示 · 非真实客户端录屏", 17, "#d1e1e4", max_width=316)
    for index, label in enumerate(["01  提出任务", "02  罗列技能", "03  用户选择", "04  执行交接"]):
        x = 44 + index * 282
        active = index == stage
        panel(draw, (x, 132, x + 266, 184), GREEN if active else "#e1e9eb", None, 12)
        text(draw, (x + 25, 145), label, 20, "white" if active else MUTED, active)
    panel(draw, (44, 208, 1156, 324))
    panel(draw, (64, 225, 270, 255), "#e6f5ee", None, 7)
    text(draw, (77, 229), "skill-selector 已选中", 16, GREEN, max_width=180)
    text(draw, (294, 229), "你只需正常描述任务，无需再要求推荐技能", 16, MUTED)
    wrapped(draw, (64, 272), case["task"], 1068, 22, bold=True, line_height=30)
    text(draw, (44, 862), "示例技能需事先安装并启用；实际清单随任务与本地目录变化。", 16, MUTED)
    text(draw, (1034, 862), f"{stage + 1} / 4", 16, MUTED)
    return im, draw


def table(draw, case, selecting):
    text(draw, (46, 350), "本次大概率会用到的 Skills", 25, bold=True)
    text(draw, (828, 356), "按相关性罗列 · 不设固定数量", 17, MUTED, max_width=328)
    panel(draw, (44, 399, 1156, 797))
    draw.rounded_rectangle((45, 400, 1155, 441), radius=14, fill="#e4ecee")
    text(draw, (64, 409), "编号", 16, MUTED)
    text(draw, (126, 409), "本地技能", 16, MUTED)
    text(draw, (674, 409), "本次用途", 16, MUTED)
    text(draw, (997, 409), "使用关系", 16, MUTED)
    for index, (name, role, relation) in enumerate(case["candidates"], 1):
        y = 445 + (index - 1) * 49
        selected = selecting and index in case["selected"]
        conditional = selecting and index in case["conditional"]
        if selected or conditional:
            draw.rounded_rectangle((53, y + 2, 1147, y + 47), radius=7,
                                   fill="#e3f4ed" if selected else "#fff1db")
        draw.rounded_rectangle((65, y + 11, 94, y + 38), radius=6,
                               fill=GREEN if selected else "#dce7e9")
        text(draw, (73, y + 12), str(index), 17, "white" if selected else MUTED)
        text(draw, (126, y + 12), name, 19, GREEN if selected else INK, max_width=530)
        text(draw, (674, y + 12), role, 19, max_width=300)
        status = "已选择" if selected else "按需使用" if conditional else relation
        text(draw, (997, y + 12), status, 17, GREEN if selected else MUTED, max_width=139)
    count = len(case["candidates"])
    if count < 6:
        line = 445 + count * 49 + 21
        text(draw, (70, line), "本例仅做选题：不加入正文、配图、排版或发布环节。", 20, GREEN, True)
        text(draw, (70, line + 48), "有多少相关技能，就展示多少；不凑数，也不截断。", 18, MUTED)


def frame(case, stage):
    im, draw = base(case, stage)
    if stage == 0:
        text(draw, (48, 358), "正式执行之前，先看清可用能力。", 28, bold=True)
        for y, title, detail in [(425, "理解你的任务", case["scope"]),
                                 (536, "检查本地能力", "结合当前会话清单，核对技能用途与可用性"),
                                 (647, "把选择权交给你", "列出主流程、辅助技能与替代项，等你选择后再执行")]:
            panel(draw, (44, y, 1156, y + 93))
            text(draw, (70, y + 13), title, 23, GREEN, True)
            text(draw, (70, y + 51), detail, 21, MUTED, max_width=1050)
        text(draw, (48, 794), "下一步：展示本次任务大概率会用到的技能清单。", 20, MUTED)
    elif stage in (1, 2):
        table(draw, case, stage == 2)
        if stage == 1:
            text(draw, (48, 816), "等待你选择：可回复编号组合、技能名，或“按建议组合”。", 20, GREEN, True)
        else:
            text(draw, (48, 816), "你选择：" + case["reply"], 21, GREEN, True, max_width=1100)
    else:
        text(draw, (48, 350), "确认选择，准备交接执行。", 27, bold=True)
        selected = [(n, False) for n in case["selected"]] + [(n, True) for n in case["conditional"]]
        height = 63 if len(selected) > 3 else 82
        for offset, (number, conditional) in enumerate(selected):
            y = 405 + offset * (height + 10)
            panel(draw, (44, y, 1156, y + height), "#fff7e9" if conditional else "#e3f4ed")
            name, role, _ = case["candidates"][number - 1]
            text(draw, (65, y + 15), name, 21, GREEN, True, max_width=630)
            text(draw, (728, y + 18), ("按需：" if conditional else "已选：") + role, 19, MUTED, max_width=403)
        y = max(670, 405 + len(selected) * (height + 10) + 12)
        end = wrapped(draw, (49, y), "下一步：" + case["handoff"], 1098, 21, INK, line_height=34)
        text(draw, (49, max(802, end + 18)), "执行交接示意；没有声称已生成真实任务成品。", 18, MUTED)
    return im


def find_font(explicit, bold=False):
    if explicit:
        path = Path(explicit)
        if path.is_file():
            return path
        raise FileNotFoundError(path)
    candidates = [Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
                  Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")]
    for path in candidates:
        if path.is_file():
            return path
    raise RuntimeError("Provide a CJK font using --font and optionally --font-bold.")


def main():
    global FONT, BOLD
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=root / "assets" / "demos")
    parser.add_argument("--font")
    parser.add_argument("--font-bold")
    args = parser.parse_args()
    FONT = find_font(args.font)
    BOLD = find_font(args.font_bold, True) if args.font_bold or not args.font else FONT
    args.output.mkdir(parents=True, exist_ok=True)
    cases = json.loads((root / "examples" / "cases.json").read_text(encoding="utf-8"))
    for case in cases:
        frames = [frame(case, stage) for stage in range(4)]
        strip = Image.new("RGB", (W, H * len(frames)))
        for index, item in enumerate(frames):
            strip.paste(item, (0, H * index))
        palette = strip.quantize(colors=192, method=Image.Quantize.MEDIANCUT)
        quantized = [item.quantize(palette=palette, dither=Image.Dither.NONE) for item in frames]
        quantized[0].save(args.output / f"{case['id']}-demo.gif", save_all=True,
                          append_images=quantized[1:], duration=[3000, 6500, 4000, 4500],
                          loop=0, disposal=2, optimize=False,
                          comment=b"Illustrative workflow simulation. Not a live recording.")
        frames[1].save(args.output / f"{case['id']}-preview.png")
        frames[3].save(args.output / f"{case['id']}-handoff.png")
        print(f"Rendered {case['id']}: {len(case['candidates'])} candidates, 4 frames, 18 seconds")


if __name__ == "__main__":
    main()
