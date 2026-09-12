"""Fail full-analysis CI if tests were silently skipped."""

import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
cases = list(root.iter("testcase"))
if not cases or any(case.find("skipped") is not None for case in cases):
    raise SystemExit("Full-analysis CI requires executed tests with no skips")
print(f"Confirmed {len(cases)} executed tests with no skips")
