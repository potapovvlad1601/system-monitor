from concurrent.futures import ThreadPoolExecutor, as_completed

from app.collectors.cpu import CPUCollector
from app.collectors.memory import MemoryCollector
from app.collectors.disk import DiskCollector
from app.collectors.network import NetworkCollector
from app.collectors.processes import ProcessCollector


def collect_static_info() -> dict:
    tasks = {
        "cpu": CPUCollector.get_cpu_static_info,
        "disk": DiskCollector.get_disk_static_info,
        "network": NetworkCollector.get_network_static_info
    }

    result = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_name = {
            executor.submit(func): name
            for name, func in tasks.items()
        }

        for future in as_completed(future_to_name):
            name = future_to_name[future]

            try:
                result[name] = future.result()
            except Exception as error:
                result[name] = {
                    "error": str(error)
                }

    return result


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


def collect_processes_info() -> dict:
    return {
        "static": ProcessCollector.get_process_static_info(),
        "dynamic": ProcessCollector.get_process_dynamic_info()
    }


def collect_dynamic_info(static_info: dict) -> dict:
    tasks = {
        "cpu": collect_cpu_dynamic_info,
        "memory": collect_memory_info,
        "disk": collect_disk_dynamic_info,
        "network": collect_network_dynamic_info,
        "processes": collect_processes_info
    }

    result = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_name = {
            executor.submit(func): name
            for name, func in tasks.items()
        }

        for future in as_completed(future_to_name):
            name = future_to_name[future]

            try:
                result[name] = future.result()
            except Exception as error:
                result[name] = {
                    "error": str(error)
                }

    # Добавляем ранее полученные статические данные.
    result["cpu"]["static"] = static_info["cpu"]
    result["disk"]["static"] = static_info["disk"]
    result["network"]["static"] = static_info["network"]

    return result