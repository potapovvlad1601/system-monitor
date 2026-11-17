from app.collectors.cpu import CPUCollector
from app.collectors.memory import MemoryCollector
from app.collectors.disk import DiskCollector
from app.collectors.network import NetworkCollector
from app.collectors.processes import ProcessCollector


def collect_static_info() -> dict:
    """Collect infrequently-changing data once in the monitor worker."""
    return {
        "cpu": CPUCollector.get_cpu_static_info(),
        "disk": DiskCollector.get_disk_static_info(),
        "network": NetworkCollector.get_network_static_info()
    }


def collect_cpu_dynamic_info() -> dict:
    return{
        "dynamic": CPUCollector.get_cpu_dynamic_info()
    }


def collect_memory_info() -> dict:
    return {
        "dynamic": MemoryCollector.get_memory_dynamic_info()
    }


def collect_disk_dynamic_info() -> dict:
    return {
        "dynamic": DiskCollector.get_disk_dynamic_info()
    }


def collect_network_dynamic_info() -> dict:
    return {
        "dynamic": NetworkCollector.get_network_dynamic_info()
    }


def collect_processes_info(process_limit: int, process_sort_by: str) -> dict:
    return ProcessCollector.get_processes_info(process_limit, process_sort_by)


def collect_page_data(
    page_name: str,
    static_info: dict,
    process_limit: int = 50,
    process_sort_by: str = "cpu"
) -> dict | None:
    """Return only the information required by the currently visible page."""
    if page_name == "dashboard":
        return {
            "cpu": {
                "static": static_info["cpu"],
                "dynamic": CPUCollector.get_cpu_dynamic_info()
            },
            "memory": collect_memory_info(),
            "disk": {
                "static": static_info["disk"],
                "dynamic": DiskCollector.get_disk_dynamic_info()
            },
            "network": {
                "static": static_info["network"],
                "dynamic": NetworkCollector.get_network_dynamic_info()
            }
        }

    if page_name == "cpu":
        return {
            "cpu": {
                "static": static_info["cpu"],
                "dynamic": CPUCollector.get_cpu_dynamic_info()
            }
        }

    if page_name == "memory":
        return {"memory": collect_memory_info()}

    if page_name == "disk":
        return {
            "disk": {
                "static": static_info["disk"],
                "dynamic": DiskCollector.get_disk_dynamic_info()
            }
        }

    if page_name == "network":
        return {
            "network": {
                "static": static_info["network"],
                "dynamic": NetworkCollector.get_network_dynamic_info()
            }
        }

    if page_name == "processes":
        return {
            "processes": collect_processes_info(
                process_limit, process_sort_by
            )
        }

    return None
