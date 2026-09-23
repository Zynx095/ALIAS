"""ALIAS Baseline Comparison Engine.

Phase 3.9: Compares extracted behavioral features of a login event
against the user's historical CanonicalBaseline across 6 dimensions.
Purely calculates objective deltas and differences; NO risk scores or threat verdicts.
"""
import math
from typing import Optional, Tuple
from schemas.baseline import (
    EventBehavioralFeatures,
    CanonicalBaseline,
    DimensionDeviation,
    BaselineComparisonResult
)


class BaselineComparisonEngine:
    """Compares an authentication event's features against a user's canonical baseline."""

    @staticmethod
    def _haversine_distance_km(
        lat1: Optional[float], lon1: Optional[float],
        lat2: Optional[float], lon2: Optional[float]
    ) -> Optional[float]:
        """Calculates great-circle distance in kilometers between two lat/lon points."""
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return None

        # Earth radius in kilometers
        r = 6371.0
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(r * c, 2)

    @classmethod
    def compare(
        cls,
        features: EventBehavioralFeatures,
        baseline: CanonicalBaseline
    ) -> BaselineComparisonResult:
        """
        Executes objective comparison across all 6 behavioral dimensions.
        """
        from schemas.baseline import BaselineStatus
        
        if baseline.status in [BaselineStatus.NO_BASELINE, BaselineStatus.INSUFFICIENT_HISTORY]:
            return BaselineComparisonResult(
                user_id=features.user_id,
                timestamp=features.timestamp,
                baseline_version=baseline.baseline_version,
                comparison_status=baseline.status,
                deviations={},
                has_deviations=False
            )

        deviations = {}

        # 1. Temporal Dimension
        temporal = baseline.temporal
        is_off_hours = False
        if temporal.typical_hours:
            is_off_hours = features.hour_of_day not in temporal.typical_hours

        is_unusual_day = False
        total_days = temporal.workday_count + temporal.weekend_count
        if total_days > 0:
            if features.is_weekend and temporal.weekend_count == 0:
                is_unusual_day = True
            elif not features.is_weekend and temporal.workday_count == 0:
                is_unusual_day = True

        hour_count = temporal.hourly_distribution.get(str(features.hour_of_day), 0)
        temporal_deviant = is_off_hours or is_unusual_day

        deviations["TEMPORAL"] = DimensionDeviation(
            dimension="TEMPORAL",
            is_deviant=temporal_deviant,
            details={
                "hour_of_day": features.hour_of_day,
                "is_off_hours": is_off_hours,
                "typical_hours": temporal.typical_hours,
                "historical_hour_count": hour_count,
                "is_weekend": features.is_weekend,
                "is_unusual_day": is_unusual_day,
                "workday_count": temporal.workday_count,
                "weekend_count": temporal.weekend_count
            }
        )

        # 2. Device Dimension
        device = baseline.device
        is_new_device = False
        if features.device_fingerprint and device.known_devices:
            is_new_device = features.device_fingerprint not in device.known_devices

        is_primary_device = (
            features.device_fingerprint in device.primary_devices
            if features.device_fingerprint else False
        )
        device_count = (
            device.device_usage_counts.get(features.device_fingerprint, 0)
            if features.device_fingerprint else 0
        )

        device_deviant = is_new_device

        deviations["DEVICE"] = DimensionDeviation(
            dimension="DEVICE",
            is_deviant=device_deviant,
            details={
                "device_fingerprint": features.device_fingerprint,
                "is_new_device": is_new_device,
                "is_primary_device": is_primary_device,
                "historical_usage_count": device_count,
                "known_devices_count": len(device.known_devices),
                "primary_devices": device.primary_devices
            }
        )

        # 3. Location Dimension
        loc = baseline.location
        is_new_location = False
        if features.location_name and loc.known_locations:
            is_new_location = features.location_name not in loc.known_locations

        distance_km = cls._haversine_distance_km(
            features.latitude, features.longitude,
            loc.last_seen_latitude, loc.last_seen_longitude
        )

        # Objective distance observation (> 500 km threshold for geographic displacement)
        significant_distance = distance_km is not None and distance_km > 500.0
        location_deviant = is_new_location or significant_distance

        deviations["LOCATION"] = DimensionDeviation(
            dimension="LOCATION",
            is_deviant=location_deviant,
            details={
                "location_name": features.location_name,
                "is_new_location": is_new_location,
                "known_locations": loc.known_locations,
                "distance_from_last_seen_km": distance_km,
                "significant_distance_observed": significant_distance,
                "last_seen_location": loc.last_seen_location
            }
        )

        # 4. Network Dimension
        net = baseline.network
        is_new_ip = False
        if features.ip_address and net.known_ips:
            is_new_ip = features.ip_address not in net.known_ips

        is_new_subnet = False
        if features.subnet and net.known_subnets:
            is_new_subnet = features.subnet not in net.known_subnets

        is_primary_ip = (
            features.ip_address in net.primary_ips
            if features.ip_address else False
        )
        ip_count = (
            net.ip_usage_counts.get(features.ip_address, 0)
            if features.ip_address else 0
        )

        # If both IP and subnet are new, it's an objective network displacement
        network_deviant = is_new_ip

        deviations["NETWORK"] = DimensionDeviation(
            dimension="NETWORK",
            is_deviant=network_deviant,
            details={
                "ip_address": features.ip_address,
                "subnet": features.subnet,
                "is_new_ip": is_new_ip,
                "is_new_subnet": is_new_subnet,
                "is_primary_ip": is_primary_ip,
                "historical_ip_count": ip_count,
                "known_ips_count": len(net.known_ips),
                "known_subnets_count": len(net.known_subnets)
            }
        )

        # 5. Authentication Dimension
        auth = baseline.authentication
        is_auth_failure = features.auth_status != "SUCCESS"
        exceeds_max_failed = False
        if features.failed_attempts > 0:
            exceeds_max_failed = features.failed_attempts > auth.typical_failed_attempts_max

        auth_deviant = is_auth_failure or exceeds_max_failed

        deviations["AUTHENTICATION"] = DimensionDeviation(
            dimension="AUTHENTICATION",
            is_deviant=auth_deviant,
            details={
                "auth_status": features.auth_status,
                "is_auth_failure": is_auth_failure,
                "failed_attempts": features.failed_attempts,
                "typical_failed_attempts_max": auth.typical_failed_attempts_max,
                "exceeds_typical_max_failed": exceeds_max_failed,
                "historical_failure_rate": auth.failure_rate,
                "total_historical_attempts": auth.total_attempts
            }
        )

        # 6. Access Pattern Dimension
        access = baseline.access_pattern
        is_new_pattern = False
        if features.access_pattern and access.known_access_patterns:
            is_new_pattern = features.access_pattern not in access.known_access_patterns

        is_primary_pattern = (
            features.access_pattern in access.primary_access_patterns
            if features.access_pattern else False
        )

        access_deviant = is_new_pattern

        deviations["ACCESS_PATTERN"] = DimensionDeviation(
            dimension="ACCESS_PATTERN",
            is_deviant=access_deviant,
            details={
                "access_pattern": features.access_pattern,
                "is_new_access_pattern": is_new_pattern,
                "is_primary_access_pattern": is_primary_pattern,
                "known_access_patterns": access.known_access_patterns
            }
        )

        has_any_deviation = any(dev.is_deviant for dev in deviations.values())

        return BaselineComparisonResult(
            user_id=features.user_id,
            timestamp=features.timestamp,
            baseline_version=baseline.baseline_version,
            comparison_status=baseline.status,
            deviations=deviations,
            has_deviations=has_any_deviation
        )
