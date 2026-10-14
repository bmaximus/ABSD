"""Tests for coverage_gate.py — run: python3 -m unittest discover -s absd/tooling -p 'test_*.py'"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from xml.sax.saxutils import quoteattr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coverage_gate  # noqa: E402


def cobertura(classes):
    """classes: list of (name, filename, [hits per line])"""
    parts = ['<?xml version="1.0"?><coverage><packages><package name="p"><classes>']
    for name, filename, hits in classes:
        lines = "".join(f'<line number="{i + 1}" hits="{h}"/>' for i, h in enumerate(hits))
        parts.append(f'<class name={quoteattr(name)} filename={quoteattr(filename)}><lines>{lines}</lines></class>')
    parts.append("</classes></package></packages></coverage>")
    return "".join(parts)


class CoverageGateTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = self.dir.name
        os.environ.pop("GITHUB_STEP_SUMMARY", None)

    def tearDown(self):
        self.dir.cleanup()

    def write(self, relative, text):
        path = os.path.join(self.root, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def run_gate(self, *args):
        return self.run_gate_with("**/*.xml", *args)

    def run_gate_with(self, pattern, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = coverage_gate.main(["--reports", os.path.join(self.root, *pattern.split("/")), *args])
        return code, out.getvalue()

    def test_passes_when_total_meets_the_minimum(self):
        self.write("a/coverage.xml", cobertura([("Shop.Cart", "src/Cart.cs", [1, 1, 1, 0])]))
        code, out = self.run_gate("--min-total", "75")
        self.assertEqual(code, 0, out)
        self.assertIn("75.0%", out)

    def test_fails_just_below_the_minimum(self):
        self.write("a/coverage.xml", cobertura([("Shop.Cart", "src/Cart.cs", [1, 1, 1, 0])]))
        code, out = self.run_gate("--min-total", "75.1")
        self.assertEqual(code, 1)
        self.assertIn("below the 75.1% minimum", out)

    def test_a_line_hit_by_any_report_counts_as_covered(self):
        self.write("unit/coverage.xml", cobertura([("Shop.Cart", "src/Cart.cs", [1, 0])]))
        self.write("api/coverage.xml", cobertura([("Shop.Cart", "src/Cart.cs", [0, 1])]))
        code, out = self.run_gate("--min-total", "100")
        self.assertEqual(code, 0, out)

    def test_a_unit_no_test_runs_fails_the_gate(self):
        self.write("a/coverage.xml", cobertura([
            ("Shop.Cart", "src/Cart.cs", [1] * 10),
            ("Shop.ResultsReader", "src/ResultsReader.cs", [0] * 6),
        ]))
        allow = self.write("allow.txt", "")
        code, out = self.run_gate("--min-total", "0", "--untested-allowlist", allow)
        self.assertEqual(code, 1)
        self.assertIn("Shop.ResultsReader (6 lines)", out)

    def test_a_listed_unit_with_a_reason_is_allowed(self):
        self.write("a/coverage.xml", cobertura([("Shop.PaymentSeam", "src/PaymentSeam.cs", [0] * 6)]))
        allow = self.write("allow.txt", "Shop.PaymentSeam   # schema seam, no behaviour yet\n")
        code, out = self.run_gate("--min-total", "0", "--untested-allowlist", allow)
        self.assertEqual(code, 0, out)

    def test_an_allowlist_entry_without_a_reason_is_an_error(self):
        self.write("a/coverage.xml", cobertura([("Shop.PaymentSeam", "src/PaymentSeam.cs", [0] * 6)]))
        allow = self.write("allow.txt", "Shop.PaymentSeam\n")
        code, out = self.run_gate("--min-total", "0", "--untested-allowlist", allow)
        self.assertEqual(code, 1)
        self.assertIn("has no reason", out)

    def test_stale_allowlist_entries_warn_but_do_not_fail(self):
        self.write("a/coverage.xml", cobertura([("Shop.Cart", "src/Cart.cs", [1] * 6)]))
        allow = self.write("allow.txt", "Shop.Cart  # was untested\n")
        code, out = self.run_gate("--min-total", "0", "--untested-allowlist", allow)
        self.assertEqual(code, 0, out)
        self.assertIn("::warning::", out)
        self.assertIn("Shop.Cart", out)

    def test_units_below_min_lines_are_not_gated(self):
        self.write("a/coverage.xml", cobertura([("Shop.Constants", "src/Constants.cs", [0] * 4)]))
        allow = self.write("allow.txt", "")
        code, out = self.run_gate("--min-total", "0", "--untested-allowlist", allow, "--min-lines", "5")
        self.assertEqual(code, 0, out)

    def test_compiler_generated_nested_types_fold_into_their_class(self):
        # the async state machine ran, so the class is not "untested"
        self.write("a/coverage.xml", cobertura([
            ("Shop.Reader", "src/Reader.cs", [0, 0, 0]),
            ("Shop.Reader/<ReadAsync>d__2", "src/Reader.cs", [1, 0, 0]),
            ("Shop.Job$Inner", "src/Job.java", [0] * 6),
        ]))
        allow = self.write("allow.txt", "")
        code, out = self.run_gate("--min-total", "0", "--untested-allowlist", allow, "--min-lines", "3")
        self.assertEqual(code, 1)
        self.assertIn("Shop.Job (6 lines)", out)
        self.assertNotIn("Shop.Reader (", out)

    def test_generic_type_names_fold_into_their_class(self):
        self.write("a/coverage.xml", cobertura([
            ("Shop.Repo", "src/Repo.cs", [0] * 6),
            ("Shop.Repo<T>", "src/Repo.cs", [1]),
            ("Shop.Cache", "src/Cache.cs", [0] * 6),
            ("Shop.Cache`1", "src/Cache.cs", [1]),
        ]))
        allow = self.write("allow.txt", "")
        code, out = self.run_gate("--min-total", "0", "--untested-allowlist", allow)
        self.assertEqual(code, 0, out)

    def test_file_units_for_stacks_without_classes(self):
        self.write("a/coverage.xml", cobertura([("cart.py", "shop/cart.py", [0] * 5)]))
        allow = self.write("allow.txt", "")
        code, out = self.run_gate("--min-total", "0", "--untested-allowlist", allow, "--unit", "file")
        self.assertEqual(code, 1)
        self.assertIn("shop/cart.py", out)

    def test_excluded_paths_are_left_out(self):
        self.write("a/coverage.xml", cobertura([
            ("Shop.Cart", "src/Cart.cs", [1] * 5),
            ("Shop.Init", "src/Migrations/Init.cs", [0] * 50),
        ]))
        code, out = self.run_gate("--min-total", "100", "--exclude", "/Migrations/")
        self.assertEqual(code, 0, out)

    def test_lcov_reports_count_files_as_units(self):
        self.write("js/lcov.info", "TN:\nSF:src/cart.ts\nDA:1,1\nDA:2,0\nend_of_record\nSF:src/reader.ts\nDA:1,0\nDA:2,0\nDA:3,0\nDA:4,0\nDA:5,0\nend_of_record\n")
        allow = self.write("allow.txt", "")
        out_json = os.path.join(self.root, "cov.json")
        code, out = self.run_gate_with("**/*.info", "--min-total", "0", "--untested-allowlist", allow, "--json", out_json)
        self.assertEqual(code, 1)
        self.assertIn("src/reader.ts (5 lines)", out)
        with open(out_json, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["total"], round(100 / 7, 1))

    def test_lcov_and_cobertura_merge(self):
        self.write("js/lcov.info", "SF:src/cart.ts\nDA:1,0\nDA:2,1\nend_of_record\n")
        self.write("x/coverage.xml", cobertura([("cart", "src/cart.ts", [1, 0])]))
        code, out = self.run_gate_with("**/*", "--min-total", "100", "--unit", "file")
        self.assertEqual(code, 0, out)

    def test_ratchet_notice_when_well_above_the_minimum(self):
        self.write("a/coverage.xml", cobertura([("Shop.Cart", "src/Cart.cs", [1, 1, 1, 0])]))
        code, out = self.run_gate("--min-total", "70")
        self.assertEqual(code, 0)
        self.assertIn("raise the minimum from 70% to 75%", out)
        code, out = self.run_gate("--min-total", "74.5")
        self.assertNotIn("ratchet", out.lower())

    def test_no_reports_is_an_input_error(self):
        code, out = self.run_gate("--min-total", "0")
        self.assertEqual(code, 2)
        self.assertIn("No Cobertura", out)

    def test_layers_and_json_output(self):
        self.write("a/coverage.xml", cobertura([
            ("Shop.Domain.Price", "src/Domain/Price.cs", [1, 1]),
            ("Shop.Api.Controller", "src/Api/Controller.cs", [1, 0]),
        ]))
        out_json = os.path.join(self.root, "cov.json")
        code, out = self.run_gate("--min-total", "0", "--layer", "Domain=/Domain/", "--layer", "Api=/Api/", "--json", out_json)
        self.assertEqual(code, 0, out)
        with open(out_json, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["layers"]["Domain"], {"covered": 2, "lines": 2})
        self.assertEqual(data["layers"]["Api"], {"covered": 1, "lines": 2})
        self.assertEqual(data["total"], 75.0)

    def test_malformed_report_is_an_input_error(self):
        self.write("a/coverage.xml", "<coverage><class name='x'")
        code, out = self.run_gate("--min-total", "0")
        self.assertEqual(code, 2)
        self.assertIn("cannot read", out)

    def test_bad_layer_spec_is_an_input_error(self):
        self.write("a/coverage.xml", cobertura([("Shop.Cart", "src/Cart.cs", [1])]))
        code, out = self.run_gate("--min-total", "0", "--layer", "nolayer")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
