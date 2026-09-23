"""ALIAS Authentication Behavior Model.

Analyzes historical authentication attempts, success/failure distributions,
and failed attempt metrics without making security verdicts.
"""
from typing import List
from models.database import LoginEvent
from schemas.baseline import AuthenticationProfile


class AuthenticationBehaviorModel:
    """Models historical authentication outcome behavior."""

    @staticmethod
    def build_profile(events: List[LoginEvent]) -> AuthenticationProfile:
        """Constructs an AuthenticationProfile from historical events."""
        if not events:
            return AuthenticationProfile()

        total_attempts = len(events)
        successful_logins = 0
        failed_logins = 0
        status_dist = {}
        failed_attempts_records = []

        sorted_events = sorted(events, key=lambda e: e.timestamp)
        last_auth_status = None

        for event in sorted_events:
            status = (event.auth_status or "SUCCESS").upper()
            status_dist[status] = status_dist.get(status, 0) + 1
            if status == "SUCCESS":
                successful_logins += 1
            elif status == "FAILURE":
                failed_logins += 1

            failed_attempts = event.failed_attempts if event.failed_attempts is not None else 0
            failed_attempts_records.append(failed_attempts)
            last_auth_status = status

        failure_rate = round(failed_logins / total_attempts, 4) if total_attempts > 0 else 0.0
        max_failed = max(failed_attempts_records) if failed_attempts_records else 0
        mean_failed = round(sum(failed_attempts_records) / len(failed_attempts_records), 2) if failed_attempts_records else 0.0

        return AuthenticationProfile(
            total_attempts=total_attempts,
            successful_logins=successful_logins,
            failed_logins=failed_logins,
            failure_rate=failure_rate,
            status_distribution=status_dist,
            typical_failed_attempts_max=max_failed,
            typical_failed_attempts_mean=mean_failed,
            last_auth_status=last_auth_status
        )
