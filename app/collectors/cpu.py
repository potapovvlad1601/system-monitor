import psutil


class CPUCollector:

    @staticmethod
    def get_cpu_static_info() -> dict:
        return {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True)
        }

    @staticmethod
    def get_cpu_dynamic_info() -> dict:

        percentage = psutil.cpu_percent(interval=1)
        freq = psutil.cpu_freq()
        temp = psutil.sensors_temperatures()
        cpu_temp = None


        try:
            load_avg = psutil.getloadavg()
        except (OSError, AttributeError):
            load_avg = None

        load_average = {
            "1_min": load_avg[0],
            "5_min": load_avg[1],
            "15_min": load_avg[2]
        }


        if temp:
            for key in ['coretemp', 'cpu_thermal', 'acpitz']:
                if key in temp and temp[key]:
                    cpu_temp = temp[key][0].current
                    break
            if cpu_temp is None:
                first_key = list(temp.keys())[0]
                if temp[first_key]:
                    cpu_temp = temp[first_key][0].current


        return {
            "percentage": percentage,
            "frequency_mhz": freq.current if freq else None,
            "temperature_c": cpu_temp,
            "load_average": load_average
        }

