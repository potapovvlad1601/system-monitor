import psutil


class NetworkCollector:

    @staticmethod
    def get_network_static_info() -> dict:
        stats = psutil.net_if_stats()

        result = {}

        for interface, info in stats.items():
            result[interface] = {
                "is_up": info.isup,
                "speed_mbps": info.speed
            }

        return result

    @staticmethod
    def get_network_dynamic_info() -> dict:
        counters = psutil.net_io_counters(pernic=True)

        result = {}

        for interface, stats in counters.items():
            result[interface] = {
                "bytes_sent": stats.bytes_sent,
                "bytes_recv": stats.bytes_recv
            }

        return result

    @staticmethod
    def calculate_network_speed(
        previous_data: dict,
        current_data: dict,
        interval: float
    ) -> dict:

        result = {}

        if interval <= 0:
            return result

        for interface, current in current_data.items():
            previous = previous_data.get(interface)

            if previous is None:
                continue

            sent_difference = current["bytes_sent"] - previous["bytes_sent"]
            recv_difference = current["bytes_recv"] - previous["bytes_recv"]

            # Счётчики могли сброситься, например после переподключения.
            if sent_difference < 0 or recv_difference < 0:
                continue

            result[interface] = {
                "upload_speed": sent_difference / interval,
                "download_speed": recv_difference / interval
            }

        return result