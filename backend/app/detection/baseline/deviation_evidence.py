"""ALIAS Deviation Evidence Builder.

Phase 3.10: Generates structured, explainable, human-readable evidence
for observed behavioral baseline deviations.
Contains strictly descriptive observations without assigning risk scores or verdicts.
"""
from typing import List
from schemas.baseline import (
    BaselineComparisonResult,
    DeviationEvidence,
    DeviationEvidenceReport
)


class DeviationEvidenceBuilder:
    """Builds structured factual evidence from comparison results."""

    @classmethod
    def build_evidence(cls, comparison: BaselineComparisonResult) -> DeviationEvidenceReport:
        """
        Translates a BaselineComparisonResult into a structured, human-readable
        DeviationEvidenceReport.
        """
        evidence_items: List[DeviationEvidence] = []
        deviating_dims: List[str] = []

        # 1. Temporal Evidence
        temp_dev = comparison.deviations.get("TEMPORAL")
        if temp_dev:
            d = temp_dev.details
            hour = d.get("hour_of_day")
            typical_hours = d.get("typical_hours", [])
            is_off_hours = d.get("is_off_hours", False)
            is_unusual_day = d.get("is_unusual_day", False)
            is_weekend = d.get("is_weekend", False)

            if is_off_hours:
                evidence_items.append(DeviationEvidence(
                    dimension="TEMPORAL",
                    feature_name="hour_of_day",
                    is_deviant=True,
                    observed_value=f"{hour:02d}:00 UTC",
                    baseline_expected=f"Typical active hours: {typical_hours}",
                    evidence_text=f"Authentication occurred at {hour:02d}:00 UTC, outside user's customary active hours ({typical_hours})."
                ))

            if is_unusual_day:
                day_type = "weekend" if is_weekend else "workday"
                evidence_items.append(DeviationEvidence(
                    dimension="TEMPORAL",
                    feature_name="day_of_week",
                    is_deviant=True,
                    observed_value=day_type,
                    baseline_expected=f"Historical {day_type} count: 0",
                    evidence_text=f"Authentication occurred on a {day_type}, but user history contains 0 prior {day_type} logins."
                ))

            if temp_dev.is_deviant:
                deviating_dims.append("TEMPORAL")

        # 2. Device Evidence
        dev_dev = comparison.deviations.get("DEVICE")
        if dev_dev:
            d = dev_dev.details
            fp = d.get("device_fingerprint")
            is_new = d.get("is_new_device", False)
            known_count = d.get("known_devices_count", 0)

            if is_new:
                evidence_items.append(DeviationEvidence(
                    dimension="DEVICE",
                    feature_name="device_fingerprint",
                    is_deviant=True,
                    observed_value=fp,
                    baseline_expected=f"{known_count} known device(s)",
                    evidence_text=f"Device fingerprint '{fp}' has not been previously observed for this user ({known_count} known devices in baseline)."
                ))
                deviating_dims.append("DEVICE")

        # 3. Location Evidence
        loc_dev = comparison.deviations.get("LOCATION")
        if loc_dev:
            d = loc_dev.details
            loc_name = d.get("location_name")
            is_new_loc = d.get("is_new_location", False)
            dist_km = d.get("distance_from_last_seen_km")
            sig_dist = d.get("significant_distance_observed", False)
            last_loc = d.get("last_seen_location")
            known_locs = d.get("known_locations", [])

            if is_new_loc:
                evidence_items.append(DeviationEvidence(
                    dimension="LOCATION",
                    feature_name="location_name",
                    is_deviant=True,
                    observed_value=loc_name,
                    baseline_expected=f"Known locations: {known_locs}",
                    evidence_text=f"Geographic location '{loc_name}' has not been previously observed in user baseline."
                ))

            if sig_dist and dist_km is not None:
                evidence_items.append(DeviationEvidence(
                    dimension="LOCATION",
                    feature_name="geographic_displacement",
                    is_deviant=True,
                    observed_value=f"{dist_km} km",
                    baseline_expected=f"Last seen location: '{last_loc}'",
                    evidence_text=f"Physical location is displaced by {dist_km} km from the user's last observed login at '{last_loc}'."
                ))

            if loc_dev.is_deviant:
                deviating_dims.append("LOCATION")

        # 4. Network Evidence
        net_dev = comparison.deviations.get("NETWORK")
        if net_dev:
            d = net_dev.details
            ip = d.get("ip_address")
            snet = d.get("subnet")
            is_new_ip = d.get("is_new_ip", False)
            is_new_subnet = d.get("is_new_subnet", False)
            known_ips_count = d.get("known_ips_count", 0)
            known_subnets_count = d.get("known_subnets_count", 0)

            if is_new_ip:
                subnet_clause = f"and new subnet '{snet}'" if is_new_subnet else f"in known subnet '{snet}'"
                evidence_items.append(DeviationEvidence(
                    dimension="NETWORK",
                    feature_name="ip_address",
                    is_deviant=True,
                    observed_value=ip,
                    baseline_expected=f"{known_ips_count} known IPs across {known_subnets_count} subnets",
                    evidence_text=f"IP address {ip} is new for this user ({subnet_clause}; {known_ips_count} previously known IPs)."
                ))
                deviating_dims.append("NETWORK")

        # 5. Authentication Evidence
        auth_dev = comparison.deviations.get("AUTHENTICATION")
        if auth_dev:
            d = auth_dev.details
            status = d.get("auth_status")
            is_failure = d.get("is_auth_failure", False)
            failed_attempts = d.get("failed_attempts", 0)
            typical_max = d.get("typical_failed_attempts_max", 0)
            exceeds_max = d.get("exceeds_typical_max_failed", False)

            if is_failure:
                evidence_items.append(DeviationEvidence(
                    dimension="AUTHENTICATION",
                    feature_name="auth_status",
                    is_deviant=True,
                    observed_value=status,
                    baseline_expected="SUCCESS",
                    evidence_text=f"Authentication attempt resulted in {status}."
                ))

            if exceeds_max:
                evidence_items.append(DeviationEvidence(
                    dimension="AUTHENTICATION",
                    feature_name="failed_attempts",
                    is_deviant=True,
                    observed_value=failed_attempts,
                    baseline_expected=f"Typical max: {typical_max}",
                    evidence_text=f"Recorded {failed_attempts} failed attempts prior to authentication, exceeding historical max of {typical_max}."
                ))

            if auth_dev.is_deviant:
                deviating_dims.append("AUTHENTICATION")

        # 6. Access Pattern Evidence
        access_dev = comparison.deviations.get("ACCESS_PATTERN")
        if access_dev:
            d = access_dev.details
            pattern = d.get("access_pattern")
            is_new_pat = d.get("is_new_access_pattern", False)
            known_patterns = d.get("known_access_patterns", [])

            if is_new_pat:
                evidence_items.append(DeviationEvidence(
                    dimension="ACCESS_PATTERN",
                    feature_name="access_pattern",
                    is_deviant=True,
                    observed_value=pattern,
                    baseline_expected=f"Known access patterns: {known_patterns}",
                    evidence_text=f"Access pattern '{pattern}' is new for this user (baseline contains: {known_patterns})."
                ))
                deviating_dims.append("ACCESS_PATTERN")

        from schemas.baseline import BaselineStatus
        
        # Cold start handling
        if comparison.comparison_status in [BaselineStatus.NO_BASELINE, BaselineStatus.INSUFFICIENT_HISTORY]:
            return DeviationEvidenceReport(
                user_id=comparison.user_id,
                timestamp=comparison.timestamp,
                baseline_version=comparison.baseline_version,
                comparison_status=comparison.comparison_status,
                evidence_items=[],
                deviating_dimensions=[],
                has_deviations=False,
                summary=f"Comparison skipped: Baseline status is {comparison.comparison_status.value}."
            )

        # Compile Summary
        has_deviations = len(deviating_dims) > 0
        if has_deviations:
            summary = f"Observed {len(evidence_items)} deviation(s) across {len(deviating_dims)} dimension(s): {', '.join(deviating_dims)}."
        else:
            summary = "No behavioral deviations observed; authentication conforms to historical baseline across all monitored dimensions."

        return DeviationEvidenceReport(
            user_id=comparison.user_id,
            timestamp=comparison.timestamp,
            baseline_version=comparison.baseline_version,
            comparison_status=comparison.comparison_status,
            evidence_items=evidence_items,
            deviating_dimensions=deviating_dims,
            has_deviations=has_deviations,
            summary=summary
        )
