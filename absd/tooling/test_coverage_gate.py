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


def cobertura(classes, sources=()):
    """classes: list of (name, filename, [hits per line]); sources: the report's <source> roots"""
    roots = "".join(f"<source>{root}</source>" for root in sources)
    parts = [f'<?xml version="1.0"?><coverage><sources>{roots}</sources><packages><package name="p"><classes>']
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

    def test_unqualified_class_names_are_units_within_their_file(self):
        # gocover-cobertura: package functions are class "-", methods are the receiver type; grcov: the file stem
        self.write("a/coverage.xml", cobertura([
            ("-", "pkg/cart/cart.go", [1] * 4), ("Service", "pkg/cart/service.go", [1] * 4),
            ("-", "pkg/pay/pay.go", [0] * 5), ("Service", "pkg/pay/service.go", [0] * 3),
            ("mod", "src/net/mod.rs", [1] * 2), ("mod", "src/db/mod.rs", [0] * 2),
        ]))
        code, out = self.run_gate("--min-total", "0", "--min-lines", "1", "--untested-allowlist", self.write("allow.txt", ""))
        self.assertEqual(code, 1, out)
        for unit in ("pkg/pay/pay.go::-", "pkg/pay/service.go::Service", "src/db/mod.rs::mod"):
            self.assertIn(unit, out)
        self.assertNotIn("pkg/cart/cart.go::-", out)

    def test_monorepo_reports_resolve_filenames_against_their_source_roots(self):
        for package, hits in (("a", [1, 1]), ("b", [0, 0])):
            self.write(f"packages/{package}/src/index.ts", "export {}\n")
            self.write(f"reports/{package}.xml", cobertura([("index.ts", "src/index.ts", hits)],
                                                          [os.path.join(self.root, "packages", package)]))
        code, out = self.run_gate("--min-total", "0", "--min-lines", "1", "--untested-allowlist", self.write("allow.txt", ""))
        self.assertEqual(code, 1, out)
        self.assertIn("packages/b/src/index.ts", out)
        self.assertIn("50.0%", out)

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

    def test_stale_allowlist_entries_fail_with_fail_on_stale(self):
        self.write("a/coverage.xml", cobertura([("Shop.Cart", "src/Cart.cs", [1] * 6)]))
        allow = self.write("allow.txt", "Shop.Cart  # was untested\nShop.Gone  # deleted since\n")
        code, out = self.run_gate("--min-total", "0", "--untested-allowlist", allow, "--fail-on-stale")
        self.assertEqual(code, 1, out)
        self.assertIn("::error::Now tested or gone — remove from", out)
        self.assertIn("Shop.Cart, Shop.Gone", out)

    def test_units_below_min_lines_are_not_gated(self):
        self.write("a/coverage.xml", cobertura([("Shop.Constants", "src/Constants.cs", [0] * 4)]))
        allow = self.write("allow.txt", "")
        code, out = self.run_gate("--min-total", "0", "--untested-allowlist", allow, "--min-lines", "5")
        self.assertEqual(code, 0, out)

    def test_compiler_generated_nested_types_fold_into_their_class(self):
        # the async state machine, the lambda display class and the anonymous class ran, so their classes are not untested
        self.write("a/coverage.xml", cobertura([
            ("Shop.Reader", "src/Reader.cs", [0, 0, 0]),
            ("Shop.Reader/<ReadAsync>d__2", "src/Reader.cs", [1, 0, 0]),
            ("Shop.Reader/<>c", "src/Reader.cs", [0, 0, 0]),
            ("Shop.Job", "src/Job.java", [0] * 3),
            ("Shop.Job$1", "src/Job.java", [1, 0, 0]),
            ("Shop.Job$$Lambda$7", "src/Job.java", [0, 0, 0]),
        ]))
        allow = self.write("allow.txt", "")
        code, out = self.run_gate("--min-total", "0", "--untested-allowlist", allow, "--min-lines", "3")
        self.assertEqual(code, 0, out)

    def test_named_nested_types_are_units_of_their_own(self):
        self.write("a/coverage.xml", cobertura([
            ("Shop.Reader", "src/Reader.cs", [1, 1, 1]),
            ("Shop.Reader/Parser", "src/Reader.cs", [0] * 6),
            ("Shop.Job", "src/Job.java", [1, 1, 1]),
            ("Shop.Job$Inner", "src/Job.java", [0] * 6),
        ]))
        allow = self.write("allow.txt", "")
        code, out = self.run_gate("--min-total", "0", "--untested-allowlist", allow)
        self.assertEqual(code, 1)
        self.assertIn("Shop.Reader/Parser (6 lines)", out)
        self.assertIn("Shop.Job$Inner (6 lines)", out)

    def test_classes_named_after_their_file_are_keyed_by_path(self):
        # coverage.py and istanbul name each "class" after its file: two index.ts are two units
        self.write("a/coverage.xml", cobertura([
            ("index.ts", "src/cart/index.ts", [1] * 6),
            ("index.ts", "src/billing/index.ts", [0] * 6),
            ("cart.py", "shop/cart.py", [1] * 6),
        ]))
        allow = self.write("allow.txt", "")
        code, out = self.run_gate("--min-total", "0", "--untested-allowlist", allow)
        self.assertEqual(code, 1)
        self.assertIn("src/billing/index.ts (6 lines)", out)
        self.assertNotIn("src/cart/index.ts (", out)

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
        self.assertIn("no coverage report found for", out)

    def test_every_reports_glob_must_match(self):
        self.write("unit/coverage.xml", cobertura([("Shop.Cart", "src/Cart.cs", [1] * 6)]))
        out = io.StringIO()
        with redirect_stdout(out):
            code = coverage_gate.main(["--reports", os.path.join(self.root, "unit", "*.xml"),
                                       "--reports", os.path.join(self.root, "web", "lcov.info"), "--min-total", "0"])
        self.assertEqual(code, 2)   # the web suite left no report: it did not run
        self.assertIn("no coverage report found for: " + os.path.join(self.root, "web", "lcov.info"), out.getvalue())

    def test_reports_without_coverable_lines_are_an_input_error(self):
        self.write("a/coverage.xml", cobertura([]))
        code, out = self.run_gate("--min-total", "0")
        self.assertEqual(code, 2)
        self.assertIn("no coverable lines in the coverage reports for", out)

    def test_every_glob_must_contribute_coverable_lines(self):
        self.write("unit/coverage.xml", cobertura([("Shop.Cart", "src/Cart.cs", [1] * 6)]))
        self.write("web/lcov.info", "TN:\nend_of_record\n")   # the web suite ran no instrumented code
        out = io.StringIO()
        with redirect_stdout(out):
            code = coverage_gate.main(["--reports", os.path.join(self.root, "unit", "*.xml"),
                                       "--reports", os.path.join(self.root, "web", "lcov.info"), "--min-total", "0"])
        self.assertEqual(code, 2)
        self.assertIn("no coverable lines in the coverage reports for: " + os.path.join(self.root, "web", "lcov.info"),
                      out.getvalue())
        out = io.StringIO()
        with redirect_stdout(out):   # two globs over the same file both count it
            code = coverage_gate.main(["--reports", os.path.join(self.root, "unit", "*.xml"),
                                       "--reports", os.path.join(self.root, "unit", "coverage.xml"), "--min-total", "0"])
        self.assertEqual(code, 0, out.getvalue())

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

    def test_layer_floors(self):
        self.write("a/coverage.xml", cobertura([
            ("Shop.Domain.Price", "src/Domain/Price.cs", [1, 1, 1, 0]),
            ("Shop.Api.Controller", "src/Api/Controller.cs", [1, 1]),
        ]))
        layers = ("--layer", "Domain=/Domain/", "--layer", "Api=/Api/")
        code, out = self.run_gate("--min-total", "0", *layers, "--min-layer", "Domain=75")
        self.assertEqual(code, 0, out)
        code, out = self.run_gate("--min-total", "0", *layers, "--min-layer", "Domain=80")
        self.assertEqual(code, 1)
        self.assertIn("Layer Domain line coverage 75.0% is below its 80% minimum.", out)
        code, out = self.run_gate("--min-total", "0", "--layer", "Money=/Money/", "--min-layer", "Money=50")
        self.assertEqual(code, 1)
        self.assertIn("Layer Money has no coverable lines", out)
        code, out = self.run_gate("--min-total", "0", *layers, "--min-layer", "Billing=50")
        self.assertEqual(code, 2)   # a floor for an undeclared layer is a usage error

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
