import json
import tempfile
import unittest
from pathlib import Path

from scripts.security.aggregate_security_reports import write_lake


class AggregateSecurityReportsTests(unittest.TestCase):
    def test_normalizes_semgrep_and_zap(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            semgrep = {
                "results": [
                    {
                        "check_id": "python.test",
                        "path": "src/example.py",
                        "start": {"line": 4, "col": 2},
                        "extra": {
                            "message": "Example SAST finding",
                            "severity": "ERROR",
                            "metadata": {"confidence": "HIGH", "category": "security"},
                        },
                    }
                ],
                "errors": [],
            }
            zap = {
                "@programName": "ZAP",
                "site": [
                    {
                        "@name": "http://frontend:3000",
                        "alerts": [
                            {
                                "pluginid": "10020",
                                "name": "Missing header",
                                "riskdesc": "Medium (High)",
                                "confidence": "3",
                                "instances": [
                                    {
                                        "uri": "http://frontend:3000/",
                                        "method": "GET",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
            (root / "semgrep.json").write_text(json.dumps(semgrep), encoding="utf-8")
            (root / "zap.json").write_text(json.dumps(zap), encoding="utf-8")

            summary = write_lake([root], root / "lake")

            self.assertEqual(summary["totals"]["finding_instances"], 2)
            self.assertEqual(summary["totals"]["by_scanner"]["semgrep"], 1)
            self.assertEqual(summary["totals"]["by_scanner"]["owasp-zap"], 1)
            rows = [
                json.loads(line)
                for line in (root / "lake" / "findings.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual({row["severity"] for row in rows}, {"high", "medium"})


if __name__ == "__main__":
    unittest.main()
