"""Convert one or more OWASP ZAP JSON reports to SARIF 2.1.0."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any

SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
TAG_RE = re.compile(r"<[^>]+>")
URL_RE = re.compile(r"https?://[^\s<]+")
LEVELS = {"3": "error", "2": "warning", "1": "note", "0": "note"}
SECURITY_SEVERITY = {"3": "8.0", "2": "6.0", "1": "3.0", "0": "1.0"}


def plain_text(value: Any) -> str:
    text = TAG_RE.sub(" ", str(value or ""))
    return " ".join(html.unescape(text).split())


def first_url(value: Any) -> str | None:
    match = URL_RE.search(plain_text(value))
    return match.group(0).rstrip(".,)") if match else None


def fingerprint(rule_id: str, instance: dict[str, Any]) -> str:
    identity = "\x00".join(
        (
            rule_id,
            str(instance.get("uri", "")),
            str(instance.get("method", "")),
            str(instance.get("param", "")),
        )
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def convert_report(report: dict[str, Any], source_name: str) -> dict[str, Any]:
    rules: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []

    for site in report.get("site", []):
        for alert in site.get("alerts", []):
            rule_id = str(alert.get("pluginid") or alert.get("alertRef") or "unknown")
            risk = str(alert.get("riskcode", "0"))
            name = plain_text(alert.get("name") or alert.get("alert") or rule_id)
            description = plain_text(alert.get("desc"))
            solution = plain_text(alert.get("solution"))
            cwe = str(alert.get("cweid", "")).strip()
            tags = ["security", "external/cwe"]
            if cwe and cwe != "-1":
                tags.append(f"CWE-{cwe}")

            rule: dict[str, Any] = {
                "id": rule_id,
                "name": re.sub(r"[^A-Za-z0-9_.-]", "_", name),
                "shortDescription": {"text": name},
                "fullDescription": {"text": description or name},
                "help": {"text": solution or description or name},
                "properties": {
                    "tags": tags,
                    "security-severity": SECURITY_SEVERITY.get(risk, "1.0"),
                },
            }
            help_uri = first_url(alert.get("reference"))
            if help_uri:
                rule["helpUri"] = help_uri
            rules[rule_id] = rule

            instances = alert.get("instances") or [{}]
            for instance in instances:
                target = str(instance.get("uri") or site.get("@name") or "")
                method = str(instance.get("method") or "")
                parameter = str(instance.get("param") or "")
                instance_fingerprint = fingerprint(rule_id, instance)
                detail = description or name
                if target:
                    detail = f"{detail} Target: {method + ' ' if method else ''}{target}."

                result: dict[str, Any] = {
                    "ruleId": rule_id,
                    "level": LEVELS.get(risk, "warning"),
                    "message": {"text": detail},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": f"security-reports/{source_name}"
                                },
                                "region": {"startLine": 1},
                            },
                            "message": {"text": target or source_name},
                        }
                    ],
                    "partialFingerprints": {
                        "primaryLocationLineHash": instance_fingerprint,
                        "zapInstance/v1": instance_fingerprint,
                    },
                    "properties": {
                        "targetUrl": target,
                        "httpMethod": method,
                        "parameter": parameter,
                        "evidence": plain_text(instance.get("evidence")),
                        "confidence": plain_text(alert.get("confidence")),
                        "risk": plain_text(alert.get("riskdesc")),
                        "sourceReport": source_name,
                    },
                }
                results.append(result)

    version = str(report.get("@version") or "unknown")
    return {
        "tool": {
            "driver": {
                "name": "OWASP ZAP",
                "informationUri": "https://www.zaproxy.org/",
                "version": version,
                "rules": list(rules.values()),
            }
        },
        "automationDetails": {"id": f"zap/{Path(source_name).stem}/"},
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="ZAP JSON report(s)")
    parser.add_argument("-o", "--output", required=True, type=Path)
    args = parser.parse_args()

    runs = []
    for input_path in args.inputs:
        with input_path.open(encoding="utf-8") as report_file:
            runs.append(convert_report(json.load(report_file), input_path.name))

    sarif = {"$schema": SARIF_SCHEMA, "version": "2.1.0", "runs": runs}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as output_file:
        json.dump(sarif, output_file, ensure_ascii=False, indent=2)
        output_file.write("\n")


if __name__ == "__main__":
    main()
