#!/usr/bin/env python3
"""Normalize Semgrep and OWASP ZAP reports into a small JSONL data lake."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SEVERITY_ORDER = {
    "critical": "critical",
    "high": "high",
    "error": "high",
    "medium": "medium",
    "warning": "medium",
    "warn": "medium",
    "low": "low",
    "note": "low",
    "info": "informational",
    "informational": "informational",
    "none": "informational",
}


def normalize_severity(value: Any) -> str:
    raw = str(value or "informational").split(" ", 1)[0].strip("()").lower()
    return SEVERITY_ORDER.get(raw, "informational")


def discover(paths: Iterable[Path]) -> list[Path]:
    reports: set[Path] = set()
    for path in paths:
        if path.is_dir():
            reports.update(item for item in path.rglob("*") if item.suffix.lower() in {".json", ".sarif"})
        elif path.is_file():
            reports.add(path)
    return sorted(reports)


def base_record(source: Path, scanner: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "scanner": scanner,
        "source_report": source.name,
    }


def parse_semgrep_json(data: dict[str, Any], source: Path) -> list[dict[str, Any]]:
    findings = []
    for result in data.get("results", []):
        extra = result.get("extra", {})
        metadata = extra.get("metadata", {})
        start = result.get("start", {})
        record = base_record(source, "semgrep")
        record.update(
            {
                "rule_id": result.get("check_id", "semgrep.unknown"),
                "title": extra.get("message") or result.get("check_id", "Semgrep finding"),
                "severity": normalize_severity(extra.get("severity")),
                "confidence": str(metadata.get("confidence", "unknown")).lower(),
                "target": result.get("path", ""),
                "location": {
                    "path": result.get("path", ""),
                    "line": start.get("line"),
                    "column": start.get("col"),
                },
                "category": metadata.get("category", "sast"),
                "references": metadata.get("references", []),
            }
        )
        findings.append(record)
    return findings


def parse_sarif(data: dict[str, Any], source: Path) -> list[dict[str, Any]]:
    findings = []
    for run in data.get("runs", []):
        driver = run.get("tool", {}).get("driver", {})
        scanner = str(driver.get("name", "sarif")).lower()
        rules = {rule.get("id"): rule for rule in driver.get("rules", [])}
        for result in run.get("results", []):
            rule_id = result.get("ruleId", "sarif.unknown")
            rule = rules.get(rule_id, {})
            message = result.get("message", {}).get("text", "")
            locations = result.get("locations") or [{}]
            physical = locations[0].get("physicalLocation", {})
            artifact = physical.get("artifactLocation", {})
            region = physical.get("region", {})
            target = artifact.get("uri", "")
            record = base_record(source, scanner)
            record.update(
                {
                    "rule_id": rule_id,
                    "title": rule.get("shortDescription", {}).get("text") or message or rule_id,
                    "severity": normalize_severity(result.get("level")),
                    "confidence": "unknown",
                    "target": target,
                    "location": {
                        "path": target,
                        "line": region.get("startLine"),
                        "column": region.get("startColumn"),
                    },
                    "category": "sast" if "semgrep" in scanner else "security",
                    "references": [
                        rule["helpUri"]
                    ] if rule.get("helpUri") else [],
                }
            )
            findings.append(record)
    return findings


def parse_zap_json(data: dict[str, Any], source: Path) -> list[dict[str, Any]]:
    findings = []
    for site in data.get("site", []):
        site_name = site.get("@name") or site.get("@host", "")
        for alert in site.get("alerts", []):
            instances = alert.get("instances") or [{}]
            for instance in instances:
                target = instance.get("uri") or site_name
                record = base_record(source, "owasp-zap")
                record.update(
                    {
                        "rule_id": str(alert.get("pluginid") or alert.get("alertRef") or "zap.unknown"),
                        "title": alert.get("name") or alert.get("alert", "ZAP finding"),
                        "severity": normalize_severity(alert.get("riskdesc") or alert.get("riskcode")),
                        "confidence": str(alert.get("confidence", "unknown")).lower(),
                        "target": target,
                        "location": {
                            "uri": target,
                            "method": instance.get("method"),
                            "parameter": instance.get("param"),
                        },
                        "category": "dast",
                        "references": [alert["reference"]] if alert.get("reference") else [],
                    }
                )
                findings.append(record)
    return findings


def parse_report(path: Path) -> tuple[str, list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if "runs" in data and str(data.get("version", "")).startswith("2.1"):
        return "sarif", parse_sarif(data, path)
    if "site" in data and ("@programName" in data or "ZAP" in str(data)):
        return "owasp-zap-json", parse_zap_json(data, path)
    if "results" in data and "errors" in data:
        return "semgrep-json", parse_semgrep_json(data, path)
    return "unsupported", []


def write_lake(inputs: list[Path], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    findings: list[dict[str, Any]] = []
    report_manifest = []

    for report in discover(inputs):
        report_type, parsed = parse_report(report)
        if report_type == "unsupported":
            continue
        findings.extend(parsed)
        report_manifest.append(
            {
                "file": report.name,
                "type": report_type,
                "finding_instances": len(parsed),
            }
        )

    findings.sort(
        key=lambda item: (
            item["scanner"],
            item["severity"],
            item["rule_id"],
            item["target"],
        )
    )
    generated_at = datetime.now(timezone.utc).isoformat()
    with (output_dir / "findings.jsonl").open("w", encoding="utf-8", newline="\n") as stream:
        for finding in findings:
            finding["ingested_at"] = generated_at
            stream.write(json.dumps(finding, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "reports": report_manifest,
        "totals": {
            "reports": len(report_manifest),
            "finding_instances": len(findings),
            "by_scanner": dict(sorted(Counter(item["scanner"] for item in findings).items())),
            "by_severity": dict(sorted(Counter(item["severity"] for item in findings).items())),
        },
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="Report files or directories")
    parser.add_argument("--output-dir", type=Path, default=Path("security-data-lake"))
    args = parser.parse_args()
    summary = write_lake(args.inputs, args.output_dir)
    print(json.dumps(summary["totals"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
