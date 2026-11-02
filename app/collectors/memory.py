import psutil


class MemoryCollector:

    @staticmethod
    def get_memory_dynamic_info() -> dict:
        return psutil.virtual_memory()._asdict()