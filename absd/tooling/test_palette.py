import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import palette  # noqa: E402


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = palette.main(list(argv))
    return code, out.getvalue() + err.getvalue()


class ContrastTests(unittest.TestCase):
    def test_known_ratios(self):
        black, white = palette.parse_hex("#000000"), palette.parse_hex("#FFFFFF")
        self.assertAlmostEqual(palette.contrast(black, white), 21.0, places=2)
        self.assertAlmostEqual(palette.contrast(palette.parse_hex("#777777"), white), 4.48, places=2)
        self.assertAlmostEqual(palette.contrast(palette.parse_hex("#767676"), white), 4.54, places=2)

    def test_oklch_round_trip(self):
        for value in ("#C4553A", "#2F3A4A", "#F2EBDD", "#000000", "#FFFFFF"):
            rgb = palette.parse_hex(value)
            back = palette.in_gamut_srgb(*palette.to_oklch(rgb))
            self.assertEqual(palette.to_hex(back), value)

    def test_report_labels_every_pair(self):
        code, out = run("report", "--color", "bg=#F2EBDD", "--color", "ink=#2F3A4A", "--color", "sand=#D8C3A5")
        self.assertEqual(code, 0, out)
        self.assertIn("| bg / ink |", out)
        self.assertRegex(out, r"\| bg / ink \| [0-9.]+:1 \| text \|")
        self.assertRegex(out, r"\| bg / sand \| [0-9.]+:1 \| area \|")


class FitTests(unittest.TestCase):
    def check_fit(self, fg, bg, target):
        data = palette.fit(("fg", palette.parse_hex(fg)), ("bg", palette.parse_hex(bg)), target)
        self.assertTrue(data["reached"])
        self.assertTrue(data["changed"])
        after = palette.parse_hex(data["after"]["hex"])
        self.assertGreaterEqual(palette.contrast(after, palette.parse_hex(bg)), target)
        self.assertLessEqual(data["delta"]["hue"], 3.0)   # the hue is kept
        return data

    def test_darkens_on_a_light_background_keeping_the_hue(self):
        data = self.check_fit("#D97757", "#F2EBDD", 4.5)
        self.assertLess(data["delta"]["L"], 0)

    def test_lightens_on_a_dark_background_keeping_the_hue(self):
        data = self.check_fit("#5B6F3A", "#1E1E24", 4.5)
        self.assertGreater(data["delta"]["L"], 0)

    def test_a_passing_pair_is_unchanged(self):
        data = palette.fit(("fg", palette.parse_hex("#2F3A4A")), ("bg", palette.parse_hex("#F2EBDD")), 4.5)
        self.assertFalse(data["changed"])
        self.assertEqual(data["after"]["hex"], "#2F3A4A")

    def test_unreachable_target_exits_1(self):
        code, out = run("fit", "--fg", "a=#808080", "--bg", "b=#7A7A7A", "--min", "21")
        self.assertEqual(code, 1, out)
        self.assertIn("cannot reach", out)

    def test_json_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "fit.json")
            code, out = run("fit", "--fg", "accent=#D97757", "--bg", "bg=#F2EBDD", "--json", path)
            self.assertEqual(code, 0, out)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        self.assertEqual(data["fg"], "accent")
        self.assertGreaterEqual(data["after"]["ratio"], 4.5)


class InputTests(unittest.TestCase):
    def test_bad_inputs_exit_2(self):
        for argv in (("report", "--color", "bg=#F2EBD"),
                     ("report", "--color", "bg=#F2EBDD"),
                     ("report", "--color", "bg=#F2EBDD", "--color", "bg=#000000"),
                     ("report", "--color", "#F2EBDD", "--color", "x=#000000"),
                     ("fit", "--fg", "a=#000000", "--bg", "b=#FFFFFF", "--min", "30")):
            code, out = run(*argv)
            self.assertEqual(code, 2, argv)
            self.assertIn("palette:", out)


if __name__ == "__main__":
    unittest.main()
