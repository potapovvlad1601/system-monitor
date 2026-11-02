import psutil
from datetime import datetime


class ProcessCollector:

    @staticmethod
    def get_process_static_info() -> dict:
        result = {}

        for process in psutil.process_iter(
            ['pid', 'name', 'username', 'create_time']
        ):
            try:
                info = process.info

                result[info['pid']] = {
                    "name": info['name'],
                    "username": info['username'],
                    "create_time": (
                        datetime.fromtimestamp(info['create_time']).isoformat()
                        if info['create_time'] else None
                    )
                }

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return result

    @staticmethod
    def get_process_dynamic_info() -> dict:
        result = {}

        for process in psutil.process_iter(
            ['pid', 'status', 'cpu_percent', 'memory_percent', 'memory_info']
        ):
            try:
                info = process.info

                result[info['pid']] = {
                    "status": info['status'],
                    "cpu_percent": info['cpu_percent'],
                    "memory_percent": info['memory_percent'],
                    "memory_rss": (
                        info['memory_info'].rss
                        if info['memory_info'] else None
                    )
                }

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return result