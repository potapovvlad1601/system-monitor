import psutil


class ProcessCollector:

    @staticmethod
    def get_processes_info(
        top_limit: int = 50,
        sort_by: str = "cpu"
    ) -> dict:
        """Collect metrics for all processes and details only for visible rows."""
        dynamic = {}

        for process in psutil.process_iter([
            'pid', 'status', 'cpu_percent', 'memory_percent', 'memory_info'
        ]):
            try:
                info = process.info

                pid = info['pid']
                dynamic[pid] = {
                    "status": info['status'],
                    "cpu_percent": info['cpu_percent'] or 0.0,
                    "memory_percent": info['memory_percent'] or 0.0,
                    "memory_rss": (
                        info['memory_info'].rss
                        if info['memory_info'] else None
                    )
                }

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        sort_keys = {
            "cpu": lambda pid: (
                dynamic[pid]["cpu_percent"], dynamic[pid]["memory_percent"]
            ),
            "memory": lambda pid: (
                dynamic[pid]["memory_percent"], dynamic[pid]["cpu_percent"]
            ),
            "pid": lambda pid: pid
        }
        top_pids = sorted(
            dynamic,
            key=sort_keys[sort_by],
            reverse=sort_by != "pid"
        )[:top_limit]

        static = {}
        for pid in top_pids:
            try:
                process_info = psutil.Process(pid).as_dict(
                    attrs=["name", "username"]
                )
                static[pid] = {
                    "name": process_info.get("name"),
                    "username": process_info.get("username")
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return {"static": static, "dynamic": dynamic}
