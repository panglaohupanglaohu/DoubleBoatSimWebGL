# -*- coding: utf-8 -*-
"""
Vessel AIS Channel — 船舶自动识别系统数据.

AIS (Automatic Identification System) 是船舶自动识别系统，用于船舶追踪和避碰。
本 Channel 提供 AIS 数据查询和解析功能。

AIS 数据类型:
- AIVDM: AIS VHF Data-link Message (接收到的其他船舶消息)
- AIVDO: AIS VHF Data-link Own vessel message (本船消息)

参考标准: IEC 61993-2, ITU-R M.1371
"""

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from .base import Channel


@dataclass
class VesselPosition:
    """AIS vessel position report.

    Attributes:
        mmsi: Maritime Mobile Service Identity (9-digit ship ID).
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.
        course: Course over ground (0-359.9 degrees).
        speed: Speed over ground in knots.
        heading: True heading (0-359 degrees, 511 = not available).
        status: Navigation status (0-15).
        timestamp: UTC timestamp of the report.
        ship_name: Optional vessel name.
        imo: Optional IMO number.
        callsign: Optional call sign.
    """

    mmsi: int
    latitude: Optional[float]
    longitude: Optional[float]
    course: Optional[float]
    speed: Optional[float]
    heading: Optional[int]
    status: int
    timestamp: Optional[datetime]
    ship_name: Optional[str] = None
    imo: Optional[int] = None
    callsign: Optional[str] = None


# Navigation status codes (ITU-R M.1371)
NAVIGATION_STATUS = {
    0: "Under way using engine",
    1: "At anchor",
    2: "Not under command",
    3: "Restricted manoeuvrability",
    4: "Constrained by her draught",
    5: "Moored",
    6: "Aground",
    7: "Engaged in Fishing",
    8: "Under way sailing",
    9: "Reserved (HSC)",
    10: "Reserved (WIG)",
    11: "Power-driven vessel towing",
    12: "Power-driven vessel pushing",
    13: "Reserved (future use)",
    14: "AIS-SART (active)",
    15: "Undefined (default)"
}

# Ship type codes (ITU-R M.1371)
SHIP_TYPES = {
    0: "Not available",
    1-19: "Reserved (future use)",
    20: "Wing in ground (WIG)",
    21-29: "Wing in ground (WIG, reserved)",
    30-39: "Fishing",
    40-49: "Towing",
    50-59: "Dredging or underwater ops",
    60-69: "Sailing",
    70-79: "Pleasure craft",
    80-89: "Reserved (future use)",
    90-99: "Other",
    100-199: "Reserved (future use)",
    200-299: "Wing in ground (WIG, high speed)",
    300-399: "Reserved (future use)",
    400-449: "Ship type A (high speed)",
    450-499: "Ship type B (high speed)",
    500-549: "Ship type C (high speed)",
    550-599: "Ship type D (high speed)",
    600-699: "Passenger ship",
    700-799: "Cargo ship",
    800-899: "Tanker",
    900-999: "Other"
}


class VesselAISChannel(Channel):
    """AIS vessel tracking channel.

    Provides functionality for:
    - Parsing AIVDM/AIVDO messages
    - Decoding vessel position reports
    - Querying AIS data from online APIs
    - Filtering vessels by area/type/status

    Usage:
        >>> ais = VesselAISChannel()
        >>> # Parse AIVDM message
        >>> aivdm = "!AIVDM,1,1,,B,13u@rN0025Inn@hQhAJrIPr<046p,0*5E"
        >>> vessel = ais.parse_aivdm(aivdm)
        >>> if vessel:
        ...     print(f"MMSI: {vessel.mmsi}, Position: {vessel.latitude}, {vessel.longitude}")

        # Check online AIS APIs
        >>> status, msg = ais.check()
        >>> print(f"AIS Channel: {status} - {msg}")
    """

    name = "vessel_ais"
    description = "AIS 船舶追踪数据"
    backends = ["pyais (optional)", "AIS API (MarineTraffic/VesselFinder)"]
    tier = 1

    def can_handle(self, url: str) -> bool:
        """Check if input is AIS data or AIS-related URL.

        Args:
            url: URL, AIVDM sentence, or file path to check.

        Returns:
            True if input is AIS data or from known AIS services.
        """
        # Check for AIVDM/AIVDO sentences
        if url.startswith('!AIVDM') or url.startswith('!AIVDO'):
            return True

        # Check for AIS service URLs
        ais_domains = [
            'marinetraffic.com',
            'vesselfinder.com',
            'shipfinder.com',
            'aislive.com',
            'exactais.com'
        ]

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        for ais_domain in ais_domains:
            if ais_domain in domain:
                return True

        # Check for AIS file extensions
        if url.endswith(('.ais', '.nmea', '.log')):
            return True

        return False

    def check(self, config: object | None = None) -> tuple[str, str]:
        """Check if AIS channel is available.

        Base parsing is built-in. Full functionality requires:
        - pyais library for AIVDM/AIVDO decoding
        - API key for online AIS services

        Returns:
            Tuple of (status, message).
        """
        features = []
        status = "ok"

        # Check for pyais library
        try:
            import importlib.util
            if importlib.util.find_spec("pyais"):
                features.append("pyais 库 (AIVDM/AIVDO 解码)")
            else:
                features.append("pyais: 未安装 (pip install pyais)")
                status = "warn"
        except Exception:
            features.append("pyais: 检查失败")
            status = "warn"

        # Check for online API configuration
        if config and hasattr(config, 'ais_api_key'):
            features.append("在线 AIS API: 已配置")
        else:
            features.append("在线 AIS API: 未配置 (MarineTraffic/VesselFinder)")

        # Base functionality always available
        features.insert(0, "内置 AIVDM 解析器 (基础)")

        return status, " | ".join(features)

    def parse_aivdm(self, sentence: str) -> Optional[VesselPosition]:
        """Parse AIVDM/AIVDO sentence (simplified decoder).

        This is a basic decoder for Type 1/2/3 position reports.
        For full AIS decoding, use the pyais library.

        AIVDM Format:
        !AIVDM,sentences,total,fills,encoded_payload,radio_channel*checksum

        Args:
            sentence: Raw AIVDM/AIVDO sentence.

        Returns:
            VesselPosition object or None if parsing fails.
        """
        if not (sentence.startswith('!AIVDM') or sentence.startswith('!AIVDO')):
            return None

        try:
            # Split AIVDM sentence
            parts = sentence.split(',')
            if len(parts) < 6:
                return None

            # Extract encoded payload
            payload = parts[5]

            # Decode 6-bit ASCII to binary
            binary = self._decode_payload(payload)

            # Extract message type (first 6 bits)
            msg_type = int(binary[:6], 2)

            # Only handle position reports (Type 1, 2, 3)
            if msg_type not in [1, 2, 3]:
                return None

            # Extract MMSI (bits 8-37)
            mmsi = int(binary[8:38], 2)

            # Extract navigation status (bits 38-42)
            nav_status = int(binary[38:42], 2)

            # Extract rate of turn (bits 42-49)
            # (simplified - skip for now)

            # Extract speed over ground (bits 50-59)
            sog = int(binary[50:60], 2) / 10.0  # Convert to knots

            # Extract position accuracy (bit 60)
            # (skip for now)

            # Extract longitude (bits 61-88)
            lon_raw = int(binary[61:89], 2)
            longitude = (lon_raw - 181000000) / 600000.0 if lon_raw != 67919520 else None

            # Extract latitude (bits 89-115)
            lat_raw = int(binary[89:116], 2)
            latitude = (lat_raw - 91000000) / 600000.0 if lat_raw != 550816000 else None

            # Extract course over ground (bits 116-127)
            cog = int(binary[116:128], 2) / 10.0

            # Extract true heading (bits 128-136)
            heading = int(binary[128:137], 2)
            if heading == 511:
                heading = None  # Not available

            # Extract timestamp (bits 137-142)
            timestamp_second = int(binary[137:143], 2)
            timestamp = None
            if timestamp_second != 59:  # 59 = not available
                timestamp = datetime.utcnow().replace(second=timestamp_second)

            return VesselPosition(
                mmsi=mmsi,
                latitude=latitude,
                longitude=longitude,
                course=cog,
                speed=sog,
                heading=heading,
                status=nav_status,
                timestamp=timestamp
            )

        except (ValueError, IndexError) as e:
            # Parsing failed
            return None

    def _decode_payload(self, payload: str) -> str:
        """Decode 6-bit ASCII payload to binary string.

        AIS uses a custom 6-bit encoding scheme.

        Args:
            payload: Encoded AIS payload string.

        Returns:
            Binary string representation.
        """
        binary = ""
        for char in payload:
            # AIS 6-bit encoding
            ascii_val = ord(char)
            if ascii_val >= 48 and ascii_val <= 87:  # 0-9, A-W
                val = ascii_val - 48
            elif ascii_val >= 97 and ascii_val <= 119:  # a-w
                val = ascii_val - 48
            else:
                val = 0

            # Convert to 6-bit binary
            binary += format(val, '06b')

        return binary

    def get_navigation_status(self, status_code: int) -> str:
        """Get human-readable navigation status.

        Args:
            status_code: Navigation status code (0-15).

        Returns:
            Human-readable status description.
        """
        return NAVIGATION_STATUS.get(status_code, "Unknown")

    def get_ship_type(self, type_code: int) -> str:
        """Get human-readable ship type.

        Args:
            type_code: Ship type code (0-999).

        Returns:
            Human-readable ship type description.
        """
        for key, value in SHIP_TYPES.items():
            if isinstance(key, int) and key == type_code:
                return value
            elif isinstance(key, range) and type_code in key:
                return value
        return "Unknown"

    def calculate_distance(self, pos1: VesselPosition, pos2: VesselPosition) -> Optional[float]:
        """Calculate distance between two vessel positions (Haversine formula).

        Args:
            pos1: First vessel position.
            pos2: Second vessel position.

        Returns:
            Distance in nautical miles, or None if positions are invalid.
        """
        if pos1.latitude is None or pos1.longitude is None:
            return None
        if pos2.latitude is None or pos2.longitude is None:
            return None

        # Convert to radians
        lat1 = math.radians(pos1.latitude)
        lon1 = math.radians(pos1.longitude)
        lat2 = math.radians(pos2.latitude)
        lon2 = math.radians(pos2.longitude)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # Earth radius in nautical miles
        r = 3440.065

        return c * r


# Export for easy import
__all__ = ['VesselAISChannel', 'VesselPosition', 'NAVIGATION_STATUS', 'SHIP_TYPES']
