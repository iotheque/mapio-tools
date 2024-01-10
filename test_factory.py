import os
import time
import paho.mqtt.publish as publish
import subprocess
import pytest
import json
import threading


def load_settings(nom_fichier='configuration.json'):
    try:
        with open(nom_fichier, 'r') as fichier:
            configuration = json.load(fichier)
        return configuration
    except FileNotFoundError:
        pytest.fail('Settings file not found')
    except json.JSONDecodeError:
        pytest.fail('Settings file is wrong')
config = load_settings()


def toggle_led(led_path, state):
    with open(os.path.join(led_path, 'brightness'), 'w') as file:
        file.write(str(state))

def chenillard():
    led_dirs = [d for d in os.listdir('/sys/class/leds/') if os.path.isdir(os.path.join('/sys/class/leds/', d))]
    led_dirs.sort()

    while True:
        for led_dir in led_dirs:
            led_path = os.path.join('/sys/class/leds/', led_dir)
            toggle_led(led_path, 1)
            time.sleep(0.1)
            toggle_led(led_path, 0)


def test_identification():
    serial_number = os.popen('cat /sys/firmware/devicetree/base/serial-number').read()
    print(f"Serial number : {serial_number}")
    assert 1 == 1


def test_check_all_gpios():
    command_to_run = "gpioinfo"
    command_process = subprocess.run(command_to_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert command_process.returncode == 0, f"Execution command error : {command_process.stderr.decode()}"
    line_count = len(command_process.stdout.decode('utf-8').splitlines())
    expected_line_count = 102
    assert line_count == expected_line_count, f"Unecpected output numbers : expected {expected_line_count} found : {line_count}"


def test_publish_mqtt_message():
    broker_address = "localhost"
    port = 1883
    topic = "homeassistant/switch/RELAY1/set"
    message = "on"
    publish.single(topic, payload=message, qos=1, hostname=broker_address, port=port)
    time.sleep(1)
    message = "off"
    publish.single(topic, payload=message, qos=1, hostname=broker_address, port=port)
    

def test_mount_and_unmount_usb_sda():
    usb_device = "/dev/sda1"

    mount_command = f"mount {usb_device} /mnt"
    mount_process = subprocess.run(mount_command, shell=True, stderr=subprocess.PIPE)
    assert mount_process.returncode == 0, f"Error during mount : {mount_process.stderr.decode()}"

    lsblk_command = "lsblk | grep mnt"
    lsblk_process = subprocess.run(lsblk_command, shell=True, stdout=subprocess.PIPE)
    assert lsblk_process.returncode == 0, f"Mount is wrong: {lsblk_process.stdout.decode()}"

    umount_command = "umount /mnt"
    umount_process = subprocess.run(umount_command, shell=True, stderr=subprocess.PIPE)
    assert umount_process.returncode == 0, f"Error during unmount : {umount_process.stderr.decode()}"

    df_process = subprocess.run(lsblk_command, shell=True, stdout=subprocess.PIPE)
    assert df_process.returncode != 0, "Error during unmount"


def test_mount_and_unmount_usb_sdb():
    usb_device = "/dev/sdb1"

    mount_command = f"mount {usb_device} /mnt"
    mount_process = subprocess.run(mount_command, shell=True, stderr=subprocess.PIPE)
    assert mount_process.returncode == 0, f"Error during mount : {mount_process.stderr.decode()}"

    lsblk_command = "lsblk | grep mnt"
    lsblk_process = subprocess.run(lsblk_command, shell=True, stdout=subprocess.PIPE)
    assert lsblk_process.returncode == 0, f"Mount is wrong: {lsblk_process.stdout.decode()}"

    umount_command = "umount /mnt"
    umount_process = subprocess.run(umount_command, shell=True, stderr=subprocess.PIPE)
    assert umount_process.returncode == 0, f"Error during unmount : {umount_process.stderr.decode()}"

    df_process = subprocess.run(lsblk_command, shell=True, stdout=subprocess.PIPE)
    assert df_process.returncode != 0, "Error during unmount"


def test_pcie_bus():
    dmesg_command = "dmesg"
    dmesg_process = subprocess.run(dmesg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check command return
    assert dmesg_process.returncode == 0, f"Execution command error dmesg : {dmesg_process.stderr.decode()}"

    pattern = "pcieport 0000:00:00.0: PME: Signaling with IRQ 23"
    assert pattern in dmesg_process.stdout.decode(), f"Patern'{pattern}' not found in dmesg."


def test_rf_module_uart1():
    command_to_run = "python3 cc2538-bsl.py -p /dev/ttyS1"
    command_process = subprocess.run(command_to_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert command_process.returncode == 0, f"Execution command error : {command_process.stderr.decode()}"
    pattern_to_check = "Primary IEEE Address"
    assert pattern_to_check in command_process.stderr.decode(), f"Pattern '{pattern_to_check}' not found in command output"


def test_rf_module_uart3():
    command_to_run = "python3 cc2538-bsl.py -p /dev/ttyAMA3"
    command_process = subprocess.run(command_to_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert command_process.returncode == 0, f"Execution command error : {command_process.stderr.decode()}"
    pattern_to_check = "Primary IEEE Address"
    assert pattern_to_check in command_process.stderr.decode(), f"Pattern '{pattern_to_check}' not found in command output"


def test_rf_module_uart5():
    command_to_run = "python3 cc2538-bsl.py -p /dev/ttyAMA5"
    command_process = subprocess.run(command_to_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert command_process.returncode == 0, f"Execution command error : {command_process.stderr.decode()}"
    pattern_to_check = "Primary IEEE Address"
    assert pattern_to_check in command_process.stderr.decode(), f"Pattern '{pattern_to_check}' not found in command output"


def test_iperf3_bitrate():
    iperf_command = f"iperf3 -c {config['serverip']} -J"
    iperf_process = subprocess.run(iperf_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert iperf_process.returncode == 0, f"iperf3 error : {iperf_process.stderr.decode()}"
    json_output = json.loads(iperf_process.stdout.decode('utf-8'))
    if 'end' in json_output and 'sum_received' in json_output['end']:
        bits_per_second = json_output['end']['sum_received']['bits_per_second']
        print(f"Bits per second : {bits_per_second}")
        assert bits_per_second > 100000000, f"Debit < 100 Mbits/sec. Current debit : {bits_per_second} bits/sec"
    else:
        pytest.fail("Debit not present in the report")


if __name__ == "__main__":
    chenillard_thread = threading.Thread(target=chenillard)
    chenillard_thread.start()
    pytest.main()
    chenillard_thread.join()
