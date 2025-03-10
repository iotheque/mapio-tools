import subprocess
import time
import argparse
import gpiod

BAUDRATE = 115200

def run_cmd(cmd, capture_output=True):
    result = subprocess.run(cmd, capture_output=capture_output, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result

def list_images(port):
    print("Image list :")
    run_cmd(["mcumgr-client", "--device", f"{port}", "list"])

def upload_firmware(port, file):
    print("flashing...")
    run_cmd(["mcumgr-client", "--device", f"{port}", "upload", f"{file}"])

def reset_module(port):
    print("Reset module")
    run_cmd(["mcumgr-client", "--device", f"{port}", "reset"])

def main():
    parser = argparse.ArgumentParser(description="NRF update script with mcumgr.")
    parser.add_argument("port", help="serial port (ex: /dev/ttyS1)")
    parser.add_argument("file", help="Path ton binary file")
    args = parser.parse_args()
    serial_port = args.port
    file = args.file

    print(f"Flashing firmware {file} on module on port {serial_port}")
    config = gpiod.line_request()
    config.request_type = gpiod.line_request.DIRECTION_OUTPUT
    # UART1
    if serial_port == "/dev/ttyS1":
        chip = gpiod.chip(2)
        flash_gpio = chip.get_line(3)
        flash_gpio.request(config)
        chip = gpiod.chip(2)
        reset_gpio = chip.get_line(5)
        reset_gpio.request(config)
    # UART3
    if serial_port == "/dev/ttyAMA3":
        chip = gpiod.chip(2)
        flash_gpio = chip.get_line(7)
        flash_gpio.request(config)
        chip = gpiod.chip(3)
        reset_gpio = chip.get_line(4)
        reset_gpio.request(config)
    # UART5
    if serial_port == "/dev/ttyAMA5":
        chip = gpiod.chip(2)
        flash_gpio = chip.get_line(6)
        flash_gpio.request(config)
        chip = gpiod.chip(3)
        reset_gpio = chip.get_line(6)
        reset_gpio.request(config)
    else:
        print("Unknown port")
        return

    flash_gpio.set_value(0)
    reset_gpio.set_value(0)
    time.sleep(0.1)
    reset_gpio.set_value(1)
    time.sleep(0.5)

    list_images(serial_port)
    upload_firmware(serial_port, file)

    flash_gpio.set_value(1)
    reset_gpio.set_value(0)
    time.sleep(0.1)
    reset_gpio.set_value(1)

    print("Flash done")

if __name__ == "__main__":
    main()

