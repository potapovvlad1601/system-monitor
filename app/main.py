from pprint import pprint

from app.services.system_info import (
    collect_static_info,
    collect_dynamic_info
)

import time

def display_network_info(data: dict) -> None:
    static = data["network"]["static"]
    dynamic = data["network"]["dynamic"]

    print("\n[ NETWORK ]")

    print(
        f"{'Interface':<15}"
        f"{'Status':<12}"
        f"{'Speed':<12}"
        f"{'Sent (MB)':<15}"
        f"{'Received (MB)':<15}"
    )

    for interface, stats in dynamic.items():
        interface_info = static.get(interface, {})

        status = "UP" if interface_info.get("is_up") else "DOWN"
        speed = interface_info.get("speed_mbps")

        sent = stats["bytes_sent"] / (1024 ** 2)
        received = stats["bytes_recv"] / (1024 ** 2)

        speed_text = f"{speed} Mbps" if speed else "Unknown"

        print(
            f"{interface:<15}"
            f"{status:<12}"
            f"{speed_text:<12}"
            f"{sent:<15.2f}"
            f"{received:<15.2f}"
        )

def display_system_info(data: dict) -> None:

    print("\n" + "=" * 50)
    print("SYSTEM MONITOR")
    print("=" * 50)

    # CPU
    print("\n[ CPU ]")
    pprint(data["cpu"])

    # MEMORY
    print("\n[ MEMORY ]")
    pprint(data["memory"]["dynamic"])

    # DISK
    print("\n[ DISK ]")
    print("Static information:")
    pprint(data["disk"]["static"])

    print("\nDynamic information:")
    pprint(data["disk"]["dynamic"])

    # NETWORK
    display_network_info(data)

    print("\nDynamic information:")
    pprint(data["network"]["dynamic"])

    # PROCESSES
    print("\n[ TOP 10 PROCESSES BY MEMORY ]")

    static_processes = data["processes"]["static"]
    dynamic_processes = data["processes"]["dynamic"]

    processes = []

    for pid, static_info in static_processes.items():
        dynamic_info = dynamic_processes.get(pid)

        if dynamic_info is None:
            continue

        processes.append({
            "pid": pid,
            **static_info,
            **dynamic_info
        })

    processes.sort(
        key=lambda process: process["memory_percent"],
        reverse=True
    )

    for process in processes[:10]:
        pprint(process)

    print("\n" + "=" * 50)



def main():
    try:
        print("Collecting static system information...")

        static_info = collect_static_info()

        print("Static information collected successfully.")

        while True:
            start_time = time.perf_counter()

            data = collect_dynamic_info(static_info)

            collection_time = time.perf_counter() - start_time

            print(f"\nCollection time: {collection_time:.2f} seconds")

            display_system_info(data)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSystem Monitor stopped.")


if __name__ == "__main__":
    main()