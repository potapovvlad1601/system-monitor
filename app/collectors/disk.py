import psutil


class DiskCollector:

    @staticmethod
    def get_disk_static_info() -> dict:
        partitions = psutil.disk_partitions()

        result = {}

        for partition in partitions:
            result[partition.mountpoint] = {
                "device": partition.device,
                "filesystem": partition.fstype,
                "mount_options": partition.opts
            }

        return result

    @staticmethod
    def get_disk_dynamic_info() -> dict:
        partitions = psutil.disk_partitions()

        result = {}

        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)

                result[partition.mountpoint] = usage._asdict()

            except (PermissionError, OSError) as error:
                result[partition.mountpoint] = {
                    "error": str(error)
                }

        return result