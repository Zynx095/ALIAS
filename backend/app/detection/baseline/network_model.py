"""ALIAS Network Behavior Model.

Extracts IP address histories, subnets, protocol versions,
and network contexts from login events.
"""
import ipaddress
from typing import List
from models.database import LoginEvent
from schemas.baseline import NetworkProfile


class NetworkBehaviorModel:
    """Models historical network and IP behavior."""

    @staticmethod
    def _extract_subnet(ip_str: str) -> str:
        """Extracts standard /24 (IPv4) or /64 (IPv6) subnet for an IP address."""
        if not ip_str:
            return ""
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            if ip_obj.version == 4:
                return str(ipaddress.ip_network(f"{ip_str}/24", strict=False))
            elif ip_obj.version == 6:
                return str(ipaddress.ip_network(f"{ip_str}/64", strict=False))
        except ValueError:
            # Fallback if invalid or special format
            parts = ip_str.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        return ip_str

    @staticmethod
    def _extract_ip_version(ip_str: str) -> str:
        """Determines if the IP address is IPv4 or IPv6."""
        if not ip_str:
            return "IPv4"
        try:
            return f"IPv{ipaddress.ip_address(ip_str).version}"
        except ValueError:
            return "IPv6" if ":" in ip_str else "IPv4"

    @classmethod
    def build_profile(cls, events: List[LoginEvent]) -> NetworkProfile:
        """Constructs a NetworkProfile from historical events."""
        if not events:
            return NetworkProfile()

        ip_usage = {}
        subnet_usage = {}
        versions_seen = set()
        last_seen_ip = None

        sorted_events = sorted(events, key=lambda e: e.timestamp)

        for event in sorted_events:
            ip = event.ip_address
            if ip:
                ip_usage[ip] = ip_usage.get(ip, 0) + 1
                last_seen_ip = ip

                subnet = cls._extract_subnet(ip)
                if subnet:
                    subnet_usage[subnet] = subnet_usage.get(subnet, 0) + 1

                version = cls._extract_ip_version(ip)
                versions_seen.add(version)

        # Primary IPs: Making up >= 10% of logins
        total_ip_events = sum(ip_usage.values())
        primary_ips = []
        if total_ip_events > 0:
            threshold = total_ip_events * 0.10
            for ip, count in ip_usage.items():
                if count >= threshold:
                    primary_ips.append(ip)

        # Primary subnets: Making up >= 15% of logins
        primary_subnets = []
        if total_ip_events > 0:
            subnet_threshold = total_ip_events * 0.15
            for snet, count in subnet_usage.items():
                if count >= subnet_threshold:
                    primary_subnets.append(snet)

        return NetworkProfile(
            known_ips=list(ip_usage.keys()),
            ip_usage_counts=ip_usage,
            primary_ips=primary_ips,
            known_subnets=list(subnet_usage.keys()),
            subnet_usage_counts=subnet_usage,
            primary_subnets=primary_subnets,
            ip_versions_seen=sorted(list(versions_seen)),
            last_seen_ip=last_seen_ip
        )
