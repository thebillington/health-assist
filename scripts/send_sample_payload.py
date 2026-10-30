#!/usr/bin/env python3
"""Send realistic Apple Health payloads to a Home Assistant webhook.

This is a development/QA helper, not part of the integration. It uses only the
Python standard library.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime


def build_payload(device_id: str, device_name: str) -> dict:
    """Build a realistic daily payload with a few changing values."""
    return {
        "device_id": device_id,
        "device_name": device_name,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "metrics": {
            "weight": {"value": round(random.uniform(71.0, 74.0), 1), "unit": "kg"},
            "body_fat": {"value": round(random.uniform(17.0, 20.0), 1), "unit": "%"},
            "steps": {"value": random.randint(3000, 14000), "unit": "steps"},
            "distance": {"value": random.randint(2000, 11000), "unit": "m"},
            "active_energy": {"value": random.randint(200, 900), "unit": "kcal"},
            "resting_heart_rate": {"value": random.randint(50, 70), "unit": "bpm"},
            "heart_rate": {"value": random.randint(60, 120), "unit": "bpm"},
            "heart_rate_variability": {"value": random.randint(20, 90), "unit": "ms"},
            "respiratory_rate": {
                "value": round(random.uniform(12.0, 18.0), 1),
                "unit": "breaths/min",
            },
            "blood_oxygen": {"value": random.randint(95, 100), "unit": "%"},
            "sleep_total": {"value": round(random.uniform(5.5, 8.5), 1), "unit": "h"},
            "sleep_deep": {"value": round(random.uniform(0.8, 2.0), 1), "unit": "h"},
            "sleep_rem": {"value": round(random.uniform(1.0, 2.5), 1), "unit": "h"},
            "water_intake": {"value": random.randint(500, 2500), "unit": "mL"},
            "flights_climbed": {"value": random.randint(0, 20), "unit": "flights"},
            "stand_hours": {"value": random.randint(4, 12), "unit": "h"},
        },
    }


def post(url: str, payload: dict, secret: str | None, insecure: bool) -> tuple[int, str]:
    """POST one JSON payload and return the status and response body."""
    headers = {"Content-Type": "application/json"}
    if secret:
        headers["X-Webhook-Secret"] = secret

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    context = None
    if insecure:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(request, timeout=20, context=context) as response:
        return response.status, response.read().decode("utf-8")


def main() -> int:
    """Run the simulator."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Full webhook URL")
    parser.add_argument(
        "--secret",
        default=None,
        help="Shared secret (or set HEALTH_WEBHOOK_SECRET)",
    )
    parser.add_argument("--device-id", default="iphone-dev-001")
    parser.add_argument("--device-name", default="Dev iPhone")
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Seconds between payloads (default: 5)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of payloads to send; 0 means run until interrupted (default: 1)",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS verification (self-signed test instances only)",
    )
    args = parser.parse_args()

    secret = args.secret or os.environ.get("HEALTH_WEBHOOK_SECRET")

    if args.insecure:
        print("warning: TLS verification is disabled", file=sys.stderr)

    sent = 0
    try:
        while args.count == 0 or sent < args.count:
            payload = build_payload(args.device_id, args.device_name)
            try:
                status, body = post(args.url, payload, secret, args.insecure)
                print(f"{datetime.now().isoformat(timespec='seconds')}  {status}  {body}")
            except urllib.error.HTTPError as err:
                print(
                    f"{datetime.now().isoformat(timespec='seconds')}  "
                    f"{err.code}  {err.read().decode('utf-8', 'replace')}",
                    file=sys.stderr,
                )
            except urllib.error.URLError as err:
                print(f"connection error: {err.reason}", file=sys.stderr)

            sent += 1
            if args.count == 0 or sent < args.count:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nstopped", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
