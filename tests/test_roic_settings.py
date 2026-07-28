from __future__ import annotations

from etf_screener.roic.settings import request_interval_seconds


def test_request_interval_for_300_rpm():
    assert request_interval_seconds(300) == 0.2


def test_request_interval_minimum_one_rpm():
    assert request_interval_seconds(1) == 60.0
