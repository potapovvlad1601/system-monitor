import psutil
import socket


class NetworkCollector:

    @staticmethod
    def get_network_static_info() -> dict:
        addresses = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        result = {}

        for interface, addr_list in addresses.items():
            if_stats = stats.get(interface)

            formatted_addresses = []

            for addr in addr_list:

                if addr.family == socket.AF_INET:
                    addr_type = "IPv4"

                elif addr.family == socket.AF_INET6:
                    addr_type = "IPv6"

                elif addr.family == psutil.AF_LINK:
                    addr_type = "MAC"

                else:
                    addr_type = f"Unknown({addr.family})"

                formatted_addresses.append({
                    "type": addr_type,
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                })

            result[interface] = {
                "addresses": formatted_addresses,
                "is_up": if_stats.isup if if_stats else None,
                "speed_mbps": if_stats.speed if if_stats else None,
                "mtu": if_stats.mtu if if_stats else None
            }

        return result

    @staticmethod
    def get_network_dynamic_info() -> dict:
        counters = psutil.net_io_counters(pernic=True)

        return {
            interface: stats._asdict()
            for interface, stats in counters.items()
        }

    @staticmethod
    def get_network_connections() -> dict:
        connections = psutil.net_connections(kind="inet")

        return {
            "connections": {
                str(index): connection._asdict()
                for index, connection in enumerate(connections)
            }
        }