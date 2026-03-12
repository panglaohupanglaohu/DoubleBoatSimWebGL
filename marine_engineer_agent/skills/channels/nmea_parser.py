# -*- coding: utf-8 -*-
"""
NMEA Parser Channel — 船舶导航数据解析.

NMEA 0183 是船舶导航设备的标准通信协议，用于 GPS、罗经、测深仪、AIS 等设备。
本 Channel 提供 NMEA 语句解析功能，支持常见导航数据类型。

参考标准: IEC 61162-1 (NMEA 0183)
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from .base import Channel


@dataclass
class NMEASentence:
    """Parsed NMEA sentence structure.

    Attributes:
        talker_id: Talker identifier (e.g., 'GP' for GPS, 'II' for Integrated Instruments).
        sentence_type: Sentence type (e.g., 'GGA', 'RMC', 'VTG').
        data_fields: List of data fields from the sentence.
        checksum: Optional checksum value.
        raw: Original raw sentence string.
    """

    talker_id: str
    sentence_type: str
    data_fields: list[str]
    checksum: Optional[str]
    raw: str


@dataclass
class GPSFix:
    """GPS position fix data.

    Attributes:
        latitude: Latitude in decimal degrees (positive = North).
        longitude: Longitude in decimal degrees (positive = East).
        quality: Fix quality (0=invalid, 1=GPS, 2=DGPS, etc.).
        satellites: Number of satellites in use.
        hdop: Horizontal Dilution of Precision.
        altitude: Altitude in meters.
        timestamp: UTC timestamp of the fix.
    """

    latitude: Optional[float]
    longitude: Optional[float]
    quality: int
    satellites: int
    hdop: Optional[float]
    altitude: Optional[float]
    timestamp: Optional[datetime]


class NMEAParserChannel(Channel):
    """NMEA 0183 parser channel for marine navigation data.

    Supports parsing of common NMEA sentences:
    - GGA: GPS Fix Data
    - RMC: Recommended Minimum Navigation Information
    - VTG: Course Over Ground and Ground Speed
    - DBT/DBS/DBK: Depth Below Transducer/Surface/Keel
    - HDG: Heading
    - AIS: AIVDM/AIVDO messages (requires external decoder)

    Usage:
        >>> parser = NMEAParserChannel()
        >>> sentence = parser.parse("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47")
        >>> if sentence.sentence_type == "GGA":
        ...     fix = parser.parse_gga(sentence)
        ...     print(f"Position: {fix.latitude}, {fix.longitude}")
    """

    name = "nmea_parser"
    description = "NMEA 0183 船舶导航数据解析"
    backends = ["pynmea2 (optional)", "ais-decoder (optional)"]
    tier = 0

    # NMEA sentence patterns
    NMEA_PATTERN = re.compile(
        r"^\$(\w{2})(\w{3}),([^*]*)\*(\w{2})$",
        re.IGNORECASE
    )

    def can_handle(self, url: str) -> bool:
        """Check if input is NMEA data or file path.

        Args:
            url: URL, file path, or NMEA sentence to check.

        Returns:
            True if input appears to be NMEA data or .nmea/.log file.
        """
        # Check for file extension
        if url.endswith(('.nmea', '.log', '.txt')):
            return True

        # Check for NMEA sentence pattern
        if url.startswith('$') and self.NMEA_PATTERN.match(url):
            return True

        # Check for NMEA file paths
        parsed = urlparse(url)
        if parsed.path.endswith(('.nmea', '.log')):
            return True

        return False

    def check(self, config: object | None = None) -> tuple[str, str]:
        """Check if NMEA parser channel is available.

        The base parser is built-in (regex-based). Optional enhancements:
        - pynmea2: Full-featured NMEA parsing library
        - ais-decoder: AIS message decoding

        Returns:
            Tuple of (status, message).
        """
        # Base functionality always available (regex parser)
        status = "ok"
        features = ["内置解析器 (GGA, RMC, VTG, DBT, HDG)"]

        # Check for pynmea2
        try:
            import importlib.util
            if importlib.util.find_spec("pynmea2"):
                features.append("pynmea2 库 (增强解析)")
            else:
                features.append("pynmea2: 未安装 (pip install pynmea2)")
        except Exception:
            features.append("pynmea2: 检查失败")

        # Check for AIS decoder
        try:
            import importlib.util
            if importlib.util.find_spec("pyais"):
                features.append("pyais 库 (AIS 解码)")
            else:
                features.append("pyais: 未安装 (pip install pyais)")
        except Exception:
            features.append("pyais: 检查失败")

        return status, " | ".join(features)

    def parse(self, sentence: str) -> Optional[NMEASentence]:
        """Parse a raw NMEA sentence.

        Args:
            sentence: Raw NMEA sentence (e.g., "$GPGGA,123519,...*47").

        Returns:
            NMEASentence object or None if parsing fails.
        """
        sentence = sentence.strip()

        # Handle sentences without checksum
        if '*' not in sentence:
            sentence = sentence.rstrip('\r\n')
            match = re.match(r"^\$(\w{2})(\w{3}),(.*)$", sentence)
            if match:
                return NMEASentence(
                    talker_id=match.group(1),
                    sentence_type=match.group(2),
                    data_fields=match.group(3).split(','),
                    checksum=None,
                    raw=sentence
                )
            return None

        match = self.NMEA_PATTERN.match(sentence)
        if not match:
            return None

        return NMEASentence(
            talker_id=match.group(1),
            sentence_type=match.group(2),
            data_fields=match.group(3).split(','),
            checksum=match.group(4),
            raw=sentence
        )

    def parse_gga(self, sentence: NMEASentence) -> Optional[GPSFix]:
        """Parse GGA sentence (GPS Fix Data).

        GGA Format:
        $--GGA,hhmmss.ss,llll.ll,a,yyyyy.yy,a,x,xx,x.x,x.x,M,x.x,M,x.x,aaaa*hh

        Args:
            sentence: Parsed NMEA sentence (must be GGA type).

        Returns:
            GPSFix object or None if parsing fails.
        """
        if sentence.sentence_type != "GGA":
            return None

        fields = sentence.data_fields
        if len(fields) < 15:
            return None

        try:
            # Parse timestamp
            timestamp = None
            if fields[0]:
                try:
                    time_str = fields[0].split('.')[0]
                    timestamp = datetime.strptime(time_str, "%H%M%S")
                except ValueError:
                    pass

            # Parse latitude
            latitude = None
            if fields[1] and fields[2]:
                lat_deg = float(fields[1][:2])
                lat_min = float(fields[1][2:])
                latitude = lat_deg + lat_min / 60.0
                if fields[2].upper() == 'S':
                    latitude = -latitude

            # Parse longitude
            longitude = None
            if fields[3] and fields[4]:
                lon_deg = float(fields[3][:3])
                lon_min = float(fields[3][3:])
                longitude = lon_deg + lon_min / 60.0
                if fields[4].upper() == 'W':
                    longitude = -longitude

            return GPSFix(
                latitude=latitude,
                longitude=longitude,
                quality=int(fields[5]) if fields[5] else 0,
                satellites=int(fields[6]) if fields[6] else 0,
                hdop=float(fields[7]) if fields[7] else None,
                altitude=float(fields[8]) if fields[8] else None,
                timestamp=timestamp
            )
        except (ValueError, IndexError):
            return None

    def parse_rmc(self, sentence: NMEASentence) -> dict:
        """Parse RMC sentence (Recommended Minimum Navigation Information).

        RMC Format:
        $--RMC,hhmmss.ss,A,llll.ll,a,yyyyy.yy,a,x.x,x.x,xxxx,x.x,a*hh

        Args:
            sentence: Parsed NMEA sentence (must be RMC type).

        Returns:
            Dictionary with position, speed, course, and date information.
        """
        if sentence.sentence_type != "RMC":
            return {}

        fields = sentence.data_fields
        result = {
            'valid': fields[1].upper() == 'A' if len(fields) > 1 else False,
            'latitude': None,
            'longitude': None,
            'speed_knots': None,
            'course': None,
            'date': None
        }

        try:
            # Parse position
            if len(fields) > 4 and fields[2] and fields[3]:
                lat_deg = float(fields[2][:2])
                lat_min = float(fields[2][2:])
                result['latitude'] = lat_deg + lat_min / 60.0
                if fields[3].upper() == 'S':
                    result['latitude'] = -result['latitude']

            if len(fields) > 6 and fields[4] and fields[5]:
                lon_deg = float(fields[4][:3])
                lon_min = float(fields[4][3:])
                result['longitude'] = lon_deg + lon_min / 60.0
                if fields[5].upper() == 'W':
                    result['longitude'] = -result['longitude']

            # Parse speed and course
            if len(fields) > 7 and fields[6]:
                result['speed_knots'] = float(fields[6])

            if len(fields) > 8 and fields[7]:
                result['course'] = float(fields[7])

            # Parse date
            if len(fields) > 9 and fields[8]:
                result['date'] = fields[8]

        except (ValueError, IndexError):
            pass

        return result

    def verify_checksum(self, sentence: NMEASentence) -> bool:
        """Verify NMEA sentence checksum.

        Args:
            sentence: Parsed NMEA sentence with checksum.

        Returns:
            True if checksum is valid, False otherwise.
        """
        if not sentence.checksum:
            return True  # No checksum to verify

        # Calculate checksum (XOR of all chars between $ and *)
        content = sentence.raw[1:sentence.raw.rfind('*')]
        calculated = 0
        for char in content:
            calculated ^= ord(char)

        return calculated == int(sentence.checksum, 16)


# Export for easy import
__all__ = ['NMEAParserChannel', 'NMEASentence', 'GPSFix']
