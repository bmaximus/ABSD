#!/usr/bin/env python3
"""Palette check for a design system seeded from a colour-combination catalogue (ABSD playbook DSN-22).

A curated combination gives colours that belong together, chosen for areas and mood, not for text contrast. This tool
says which pairs of a palette can carry text, and fits a colour to a contrast target by changing only its lightness
(and chroma where the lighter or darker colour would leave the sRGB gamut) — never its hue — so the combination keeps
its character while passing DSN-15. It reads no catalogue: the product supplies the colours and records their source.

Contrast is the WCAG 2.x ratio over sRGB relative luminance. Lightness, chroma and hue are OKLCH (OKLab, Ottosson).
Verdicts per pair: text (≥ 4.5:1), large (≥ 3:1: large text and UI parts), area (below 3:1: never text or a
control boundary, only adjacent areas).

usage:
  palette.py report --color bg=#F2EBDD --color ink=#2F3A4A --color accent=#C4553A [--json out.json]
  palette.py fit --fg accent=#C4553A --bg bg=#F2EBDD [--min 4.5] [--json out.json]

`fit` keeps the background and moves the foreground away from it in lightness (darker on a light background, lighter
on a dark one) until the ratio reaches --min. Exit codes: 0 done, 1 `fit` cannot reach the target at any lightness,
2 bad input.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys

sys.dont_write_bytecode = True   # no __pycache__ in the kit: an untracked file breaks every clean-tree hand-off

HEX = re.compile(r"^#?([0-9A-Fa-f]{6})$")
NAME = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,39}$")
TEXT, LARGE = 4.5, 3.0


class InputError(Exception):
    pass


def parse_hex(value: str) -> tuple[float, float, float]:
    match = HEX.match(value.strip())
    if not match:
        raise InputError(f"{value!r} is not a colour: use #RRGGBB")
    digits = match.group(1)
    return tuple(int(digits[i:i + 2], 16) / 255 for i in (0, 2, 4))


def to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(min(1.0, max(0.0, c)) * 255):02X}" for c in rgb)


def parse_named(value: str) -> tuple[str, tuple[float, float, float]]:
    name, sep, colour = value.partition("=")
    if not sep or not NAME.match(name):
        raise InputError(f"{value!r}: use name=#RRGGBB (name: letters, digits, . _ -)")
    return name, parse_hex(colour)


def linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def gamma(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def luminance(rgb) -> float:
    r, g, b = (linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def verdict(ratio: float) -> str:
    return "text" if ratio >= TEXT else "large" if ratio >= LARGE else "area"


def to_oklch(rgb) -> tuple[float, float, float]:
    r, g, b = (linear(c) for c in rgb)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360


def from_oklch(L: float, C: float, H: float) -> tuple[float, float, float]:
    """Linear-light sRGB, unclamped (out of gamut when any channel is outside 0..1)."""
    A, B = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def in_gamut_srgb(L: float, C: float, H: float) -> tuple[float, float, float]:
    """The colour at lightness L and hue H with the most chroma up to C that sRGB can show (gamma-encoded)."""
    lo, hi = 0.0, C
    best = from_oklch(L, 0.0, H)
    if all(-1e-9 <= c <= 1 + 1e-9 for c in from_oklch(L, C, H)):
        best = from_oklch(L, C, H)
    else:
        for _ in range(40):
            mid = (lo + hi) / 2
            candidate = from_oklch(L, mid, H)
            if all(-1e-9 <= c <= 1 + 1e-9 for c in candidate):
                lo, best = mid, candidate
            else:
                hi = mid
    return tuple(gamma(min(1.0, max(0.0, c))) for c in best)


def describe(rgb) -> dict:
    L, C, H = to_oklch(rgb)
    return {"hex": to_hex(rgb), "oklch": [round(L, 4), round(C, 4), round(H, 2)]}


def report(colours: list[tuple[str, tuple]]) -> dict:
    pairs = []
    for i, (name_a, a) in enumerate(colours):
        for name_b, b in colours[i + 1:]:
            ratio = contrast(a, b)
            pairs.append({"a": name_a, "b": name_b, "ratio": round(ratio, 2), "use": verdict(ratio)})
    return {"colours": {name: describe(rgb) for name, rgb in colours}, "pairs": pairs}


def fit(fg: tuple[str, tuple], bg: tuple[str, tuple], target: float) -> dict:
    (fg_name, fg_rgb), (bg_name, bg_rgb) = fg, bg
    L, C, H = to_oklch(fg_rgb)
    before = contrast(fg_rgb, bg_rgb)
    result = {"fg": fg_name, "bg": bg_name, "min": target, "before": {**describe(fg_rgb), "ratio": round(before, 2)}}
    if before >= target:
        return {**result, "after": result["before"], "changed": False, "reached": True}
    darker = luminance(bg_rgb) >= 0.18   # move away from the background: down on light, up on dark
    end = 0.0 if darker else 1.0
    if contrast(in_gamut_srgb(end, C, H), bg_rgb) < target:
        return {**result, "after": None, "changed": False, "reached": False}
    lo, hi = (end, L) if darker else (L, end)
    for _ in range(50):   # the ratio rises monotonically as L moves towards `end`
        mid = (lo + hi) / 2
        passes = contrast(in_gamut_srgb(mid, C, H), bg_rgb) >= target
        if darker:
            lo, hi = (mid, hi) if passes else (lo, mid)
        else:
            lo, hi = (lo, mid) if passes else (mid, hi)
    new = in_gamut_srgb(lo if darker else hi, C, H)
    # rounding to 8-bit channels can drop the ratio a hair: step on until the rounded colour passes
    step = -0.001 if darker else 0.001
    L_new = lo if darker else hi
    while contrast(parse_hex(to_hex(new)), bg_rgb) < target and 0.0 <= L_new <= 1.0:
        L_new += step
        new = in_gamut_srgb(min(1.0, max(0.0, L_new)), C, H)
    new = parse_hex(to_hex(new))
    after = {**describe(new), "ratio": round(contrast(new, bg_rgb), 2)}
    L2, C2, H2 = to_oklch(new)
    hue_shift = abs((H2 - H + 180) % 360 - 180) if C2 > 0.02 and C > 0.02 else 0.0
    return {**result, "after": after, "changed": True, "reached": True,
            "delta": {"L": round(L2 - L, 4), "C": round(C2 - C, 4), "hue": round(hue_shift, 2)}}


def print_report(data: dict) -> None:
    print("| Colour | Hex | OKLCH (L, C, H) |")
    print("|---|---|---|")
    for name, c in data["colours"].items():
        print(f"| {name} | {c['hex']} | {c['oklch'][0]}, {c['oklch'][1]}, {c['oklch'][2]} |")
    print()
    print("| Pair | Ratio | Use |")
    print("|---|---|---|")
    for p in data["pairs"]:
        print(f"| {p['a']} / {p['b']} | {p['ratio']}:1 | {p['use']} |")


def print_fit(data: dict) -> None:
    before = data["before"]
    head = f"{data['fg']} on {data['bg']} (min {data['min']}:1): {before['hex']} {before['ratio']}:1"
    if not data["reached"]:
        print(f"{head} → cannot reach {data['min']}:1 at any lightness of this hue; choose another pair")
    elif not data["changed"]:
        print(f"{head} → passes unchanged")
    else:
        after, delta = data["after"], data["delta"]
        print(f"{head} → {after['hex']} {after['ratio']}:1 (ΔL {delta['L']:+}, ΔC {delta['C']:+}, hue shift "
              f"{delta['hue']}°)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    rep = sub.add_parser("report", help="contrast and use of every pair")
    rep.add_argument("--color", action="append", required=True, metavar="NAME=#RRGGBB")
    rep.add_argument("--json")
    fit_p = sub.add_parser("fit", help="lightness-only fit of a foreground to a contrast target")
    fit_p.add_argument("--fg", required=True, metavar="NAME=#RRGGBB")
    fit_p.add_argument("--bg", required=True, metavar="NAME=#RRGGBB")
    fit_p.add_argument("--min", type=float, default=TEXT)
    fit_p.add_argument("--json")
    args = parser.parse_args(argv)
    try:
        if args.command == "report":
            colours = [parse_named(v) for v in args.color]
            names = [n for n, _ in colours]
            if len(set(names)) != len(names):
                raise InputError("each colour name once")
            if len(colours) < 2:
                raise InputError("give at least two colours")
            data = report(colours)
            print_report(data)
            code = 0
        else:
            if not 1.0 <= args.min <= 21.0:
                raise InputError("--min is a contrast ratio between 1 and 21")
            data = fit(parse_named(args.fg), parse_named(args.bg), args.min)
            print_fit(data)
            code = 0 if data["reached"] else 1
    except InputError as error:
        print(f"palette: {error}", file=sys.stderr)
        return 2
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
