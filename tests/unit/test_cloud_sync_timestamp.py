#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for S3CompatibleAdapter._extract_event_timestamp()"""

from datetime import datetime, timezone
from storage.cloud_sync import S3CompatibleAdapter


def _make_adapter():
    return S3CompatibleAdapter({"bucket_name": "test-bucket"})


class TestExtractEventTimestamp:
    def test_iso_string_parsing(self):
        adapter = _make_adapter()
        event = {"timestamp": "2026-03-20T12:30:00"}
        result = adapter._extract_event_timestamp(event)
        assert isinstance(result, datetime)
        assert result.year == 2026
        assert result.month == 3
        assert result.day == 20
        assert result.hour == 12
        assert result.minute == 30

    def test_utc_z_suffix(self):
        adapter = _make_adapter()
        event = {"timestamp": "2026-03-20T12:30:00Z"}
        result = adapter._extract_event_timestamp(event)
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    def test_uploaded_at_field(self):
        adapter = _make_adapter()
        event = {"uploaded_at": "2026-01-15T08:00:00"}
        result = adapter._extract_event_timestamp(event)
        assert isinstance(result, datetime)
        assert result.month == 1

    def test_invalid_string_uses_fallback(self):
        adapter = _make_adapter()
        fb = datetime(2026, 1, 1, tzinfo=timezone.utc)
        event = {"timestamp": "not-a-date"}
        result = adapter._extract_event_timestamp(event, fallback=fb)
        assert result == fb

    def test_no_timestamp_returns_none(self):
        adapter = _make_adapter()
        event = {"payload": "data"}
        result = adapter._extract_event_timestamp(event)
        assert result is None

    def test_no_timestamp_with_datetime_fallback(self):
        adapter = _make_adapter()
        fb = datetime(2026, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        result = adapter._extract_event_timestamp({}, fallback=fb)
        assert result == fb

    def test_fallback_none_returns_none(self):
        adapter = _make_adapter()
        event = {"timestamp": "invalid_ts"}
        result = adapter._extract_event_timestamp(event, fallback=None)
        assert result is None

    def test_iso_with_offset(self):
        adapter = _make_adapter()
        event = {"timestamp": "2026-03-20T12:30:00+08:00"}
        result = adapter._extract_event_timestamp(event)
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    def test_empty_timestamp_uses_fallback(self):
        adapter = _make_adapter()
        fb = datetime(2026, 2, 1, tzinfo=timezone.utc)
        event = {"timestamp": ""}
        result = adapter._extract_event_timestamp(event, fallback=fb)
        assert result == fb
