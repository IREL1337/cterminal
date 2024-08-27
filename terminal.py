import difflib
import sys
import os
import winreg
import subprocess


services = {
    "dev_mode": False,
    "cpu_max": False,
    "ethernet_limits": False
}


def show_help():
    print("""
    Perintah yang tersedia:
    - onkan dev mode: Mengaktifkan Developer Mode.
    - onkan cpu max: Memaksimalkan penggunaan CPU.
    - onkan no limits: Menghapus batasan pada Ethernet.
    - running: Menampilkan fitur yang sedang berjalan.
    - stop [service]: Menghentikan service tertentu (misal: stop dev mode).
    - stop all: Menghentikan semua service yang berjalan.
    - help: Menampilkan pesan bantuan ini.
    """)

def correct_command(input_command, commands):
    closest_match = difflib.get_close_matches(input_command, commands, n=1, cutoff=0.6)
    return closest_match[0] if closest_match else None


def enable_developer_mode():
    key = winreg.HKEY_LOCAL_MACHINE
    sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock"
    value_name = "AllowDevelopmentWithoutDevLicense"
    try:
        winreg.CreateKey(key, sub_key)
        registry_key = winreg.OpenKey(key, sub_key, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, value_name, 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(registry_key)
        services["dev_mode"] = True
        print("Developer Mode enabled.")
    except WindowsError as e:
        print(f"Failed to enable Developer Mode: {e}")


def maximize_cpu_usage():
    try:
        os.system("wmic process where name='python.exe' CALL setpriority 128")
        services["cpu_max"] = True
        print("CPU usage maximized.")
    except Exception as e:
        print(f"Failed to maximize CPU usage: {e}")


def remove_ethernet_limits():
    try:
        subprocess.run(["netsh", "int", "tcp", "set", "global", "autotuninglevel=disabled"], check=True)
        subprocess.run(["netsh", "int", "tcp", "set", "heuristics", "disabled"], check=True)
        subprocess.run(["netsh", "int", "tcp", "set", "global", "rss=disabled"], check=True)
        subprocess.run(["netsh", "int", "tcp", "set", "global", "chimney=disabled"], check=True)
        services["ethernet_limits"] = True
        print("Ethernet limits removed.")
    except Exception as e:
        print(f"Failed to remove Ethernet limits: {e}")


def stop_service(service_name):
    if service_name == "dev mode" and services["dev_mode"]:
        services["dev_mode"] = False
        print("Developer Mode disabled.")
    elif service_name == "cpu max" and services["cpu_max"]:
        services["cpu_max"] = False
        print("CPU maximization stopped.")
    elif service_name == "no limits" and services["ethernet_limits"]:
        services["ethernet_limits"] = False
        print("Ethernet limits restored.")
    else:
        print(f"Service '{service_name}' is not running or not recognized.")


def stop_all_services():
    for service in services:
        services[service] = False
    print("All services stopped.")


def show_running_services():
    running_services = [service.replace('_', ' ') for service, status in services.items() if status]
    if running_services:
        print(f"Running services: {', '.join(running_services)}")
    else:
        print("No services are currently running.")

if __name__ == "__main__":
    commands = {
        "onkan dev mode": enable_developer_mode,
        "onkan cpu max": maximize_cpu_usage,
        "onkan no limits": remove_ethernet_limits,
        "running": show_running_services,
        "stop all": stop_all_services,
        "help": show_help
    }

    while True:
        user_input = input("Enter command: ").strip().lower()

        if user_input.startswith("stop "):
            service_name = user_input[5:].strip()
            correct_service = correct_command(service_name, ["dev mode", "cpu max", "no limits"])
            if correct_service:
                stop_service(correct_service)
            else:
                print(f"Service '{service_name}' not recognized.")
        else:
            correct_cmd = correct_command(user_input, list(commands.keys()))
            if correct_cmd:
                commands[correct_cmd]()
            else:
                print(f"Command '{user_input}' not recognized. Type 'help' for a list of commands.")
