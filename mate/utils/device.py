"""Module for communicating via CLI with devices using serial or SSH connection.
Provides common interface for communicating with SSH and serial devices. Will reconnect to
devices. Provides simplified subset of pexpect API but also expose complete pexpect API.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import logging
import os
import subprocess
import time
import traceback
from subprocess import STDOUT

import click
# noinspection PyPackageRequirements
import serial
from pexpect import EOF, TIMEOUT, pxssh, spawn
from pexpect.fdpexpect import fdspawn
from pexpect.pxssh import ExceptionPxssh


COMMAND_TIMEOUT = 5.0
CONNECT_RETRIES = 5
CONNECT_TIMEOUT = 120
DEFAULT_BAUD_RATE = 115200
DEFAULT_SERIAL_PORT = "/dev/ttyACM0"
PROMPT = "(\#)"
RETRIES = 5
RETRY_SLEEP_INTERVAL = 5.0
RESET_SLEEP_TIME = 3.0
SERIAL_LOG_FILENAME = "serial.log"
SHELL_LOG_FILENAME = "shell.log"
SSH_LOG_FILENAME = "ssh.log"
SOCKET_LOG_FILENAME = "socket.log"
TELNET_LOG_FILENAME = "telnet.log"
CONNECT_DELAY = 10.0
PING_CHECK_DELAY = 30.0
NL = "\n"
CRLF = "\r\n"
CR = "\r"

logger = logging.getLogger("mate")


def run_command(cmd, no_crlf=False):
    """run shell command in subprocess and return results

    Arg:
        cmd (str): Shell command
        timeout (int): Time in seconds to wait for command to complete.
        no_crlf (bool): Remove the CR and LF characters from response (default = False)

    Returns:
        (str) results from shell command

    """
    try:
        response = subprocess.check_output(cmd, shell=True, stderr=STDOUT).decode()
        if no_crlf:
            response = response.replace("\r", "").replace("\n", "")
        return response, 0
    except subprocess.CalledProcessError as error:
        return error.output.decode(), error.returncode


def sendline_and_expect(device,
                        command,
                        pattern=PROMPT,
                        timeout=COMMAND_TIMEOUT,
                        line_terminator=NL):
    """Send command with line terminator to router, look for pattern and return matching results or None"""
    return send_and_expect(device, command, pattern=pattern, timeout=timeout,
                           line_terminator=line_terminator)


def send_and_expect(device,
                    command,
                    pattern=PROMPT,
                    timeout=COMMAND_TIMEOUT,
                    line_terminator=""):
    """Send command to device, look for pattern and return matching results or None."""
    result = None
    logger.debug("Sending to {}  {}".format(device.name, command))
    for retry in range(RETRIES):
        try:
            whole_command = "{}{}".format(command, line_terminator)
            device.connection.send(whole_command)
            result = expect(device, pattern=pattern, timeout=timeout)
            break
        except (ExceptionPxssh, OSError, IndexError):
            traceback.print_exc()
            logger.debug("Problem trying to send command to device {}. Reconnecting and trying again.")
            device.reconnect()

    return result


def expect(device,
           pattern=PROMPT,
           timeout=COMMAND_TIMEOUT):
    """Look for patterns and return matching results or None.
        Args:
            device: Device pexepct spawn object.
            pattern: Patterns to match. Can be a single regex or list of regexes.
            timeout (float): time in seconds to wait for a matching pattern.

        Returns:
            (str): Matching pattern from regex.
    """
    result = None
    for retry in range(RETRIES):
        try:
            logger.debug(
                "Attempt {} On {} Looking for {}.  Timeout = {} seconds.".format(retry,
                                                                                 device.name,
                                                                                 pattern,
                                                                                 timeout))
            if type(pattern) == list:
                patterns = pattern
            else:
                patterns = [pattern]

            # noinspection PyTypeChecker
            search_patterns = [EOF, TIMEOUT] + patterns
            index = device.connection.expect(search_patterns, timeout=timeout)
            logger.debug("Pattern {} Index {}".format(search_patterns, index))
            logger.debug("Match {}".format(result))
            logger.debug("Found before {}".format(device.connection.before))
            logger.debug("Found after {}".format(device.connection.after))
            logger.debug("Found match {}".format(result))
            if index == 0:
                logger.debug("EOF Error during attempt {} while looking "
                             "for {} on {}.".format(retry, pattern, device.connection.name))
                device.reconnect()
            elif index == 1:
                logger.debug("TIMEOUT Error during attempt {} while looking "
                             "for {} on {}.  Timeout = {} seconds.".format(retry, pattern, device.connection.name,
                                                                           timeout))
                logger.debug("Found before {}".format(device.connection.before))
                logger.debug("Found after {}".format(device.connection.after))
            else:
                if hasattr(device.connection.match, "group"):
                    logger.debug("Found a match ...")
                    result = ""
                    for match in device.connection.match.groups():
                        if len(result) != 0:
                            result = result + "\n"
                        result = result + match.decode('utf-8')
                        logger.debug("Match {}".format(result))
                    logger.debug("Found before {}".format(device.connection.before))
                    logger.debug("Found after {}".format(device.connection.after))
                    logger.debug("Found match {}".format(result))
            if result is not None:
                result = result.strip()
            logger.debug("Returning the result ...")
            break
        except (ExceptionPxssh, OSError, IndexError):
            traceback.print_exc()
            logger.debug("Problem trying to send command to device {}. Reconnecting and trying again.")
            device.reconnect()
    return result


def reconnect(device):
    """Close router and try to reconnect ..."""
    for retry in range(RETRIES):
        try:
            if device.connection is None:
                logger.debug("Reconnecting to {}.".format(device.name))
                device.connect()
                return
            if device.is_booted():
                device.close()
            device.connect()
        except (ExceptionPxssh, OSError, IndexError):
            traceback.print_exc()
            logger.debug("Problem trying to send command to device {}. Reconnecting and trying again.")
            device.reset()

    return


def sendline(device,
             command,
             line_terminator=NL):
    """

    :param device:
    :type device:
    :param command:
    :type command:
    :param line_terminator:
    :type line_terminator:
    """
    line = command + line_terminator
    line = line.encode('utf-8')
    device.connection.send(line)


def send(device, command):
    """

    :param device:
    :type device:
    :param command:
    :type command:
    """
    device.connection.send(command.encode('utf-8'))


def prompt(device):
    """

    :param device:
    :type device:
    """
    device.connection.prompt()


def flush(device):
    """

    :param device:
    :type device:
    """
    device.connection.flush()


def close(device):
    """

    :param device:
    :type device:
    """
    device.connection.close()


# noinspection SpellCheckingInspection,PyMissingOrEmptyDocstring
class SSHDevice(object):
    """Class for controlling device via SSH router.

    Args:
        name (str): Name for device.
        ip_address (str): Hostname or IP Address of device.
        username (str): Username for SSH router.
        password (str): Password for SSH router.
        default_password (str): Default password for device, used when device has been reset to factory defaults.
        ssh_key_filename (str): SSH key filename.
        timeout (float): Timeout value in seconds for SSH router.
        log_filename (str): Name of file for logging SSH router output.
        progress_message (str): Mesaage displayed when connecting to host.
        delay_after_reboot (bool): True if need to delay before reconnecting to device after reboot (default=False).
    """

    def __init__(self,
                 name=None,
                 ip_address=None,
                 username=None,
                 password=None,
                 default_password=None,
                 ssh_key_filename=None,
                 timeout=COMMAND_TIMEOUT,
                 log_filename=SSH_LOG_FILENAME,
                 progress_message=None,
                 delay_after_reboot=False):

        logger.debug("Creating SSH Device ...")
        if name is None:
            self.name = "SSH Device @ {}".format(ip_address)
        else:
            self.name = name
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.default_password = default_password
        self.ssh_key_filename = ssh_key_filename
        self.timeout = timeout
        self.delay_after_reboot = delay_after_reboot
        if log_filename is not None:
            self.log_filename = log_filename + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".log"
            self.log_file = open(log_filename, 'ab+')
        else:
            self.log_file = None
        self.progress_message = progress_message
        self.connection = None
        logger.debug("Connecting to SSH device ...")
        self.connect(self.progress_message)

    def connect(self,
                progress_message=None,
                timeout=CONNECT_TIMEOUT):
        """
        Connect to the device.

        Args:
            progress_message (str): Message to display while trying to connect.
            timeout (float): Time in seconds to wait for connection to complete.
        """
        logger.debug("Starting Ping Check ...")
        if self.delay_after_reboot:
            ping_check_delay = PING_CHECK_DELAY
            connect_delay = CONNECT_DELAY
            self.delay_after_reboot = False
        else:
            ping_check_delay = 0.0
            connect_delay = 0.0
        self.ping_check(progress_message, timeout=timeout, ping_check_delay=ping_check_delay)
        logger.debug("Waiting an additional {} seconds before connecting to device ...".format(connect_delay))
        time.sleep(connect_delay)

        password = self.password
        for retry in range(CONNECT_RETRIES):
            logger.debug("Logging into {} -- attempt # {}".format(self.ip_address, retry + 1))
            try:
                self.connection = pxssh.pxssh(
                    options={"StrictHostKeyChecking": "no", "UserKnownHostsFile": "/dev/null"},
                    logfile=self.log_file)
                logger.debug("Logging into device with Hostname {} Password {} "
                             "SSH Keyfile {} Log Filename {}".format(self.ip_address,
                                                                     self.password,
                                                                     self.ssh_key_filename,
                                                                     self.log_filename))

                if password is None and self.ssh_key_filename is None:
                    logger.debug("Logging into {} with just username {}".format(self.ip_address, self.username))
                    self.connection.login(self.ip_address, self.username)
                    break
                elif password is not None and self.ssh_key_filename is None:
                    logger.debug(
                        "Logging into {} with username {} and password {}".format(self.ip_address, self.username,
                                                                                  password))
                    self.connection.login(self.ip_address, self.username, password=password)
                    break
                elif self.ssh_key_filename is not None:
                    logger.debug(
                        "Logging into {} with username {} and SSH Key {}".format(self.ip_address, self.username,
                                                                                 self.ssh_key_filename))
                    self.connection.login(self.ip_address, self.username, ssh_key=self.ssh_key_filename)
                    # self.connection.login(self.ip_address, self.username, password=password)
                    break
                else:
                    raise RuntimeError("Problem SSHing into the device error with IP address {} password {} "
                                       "SSH key filename {}.".format(self.ip_address, self.password,
                                                                     self.ssh_key_filename))
            except ExceptionPxssh as e:
                logger.debug("Problem connecting to the device with IP address {} username {} "
                             "SSH key filename {}.".format(self.ip_address, self.username, self.ssh_key_filename))
                logger.debug("SSH Exception {}".format(str(e)))
                if str(e) == "password refused":
                    # noinspection PyUnusedLocal
                    logger.debug("Password refused. Going to try default password.")
                    password = self.default_password
                elif str(e) == "Could not establish connection to host":
                    # noinspection PyUnusedLocal
                    logger.debug("Could not establish connection to host. Trying again ...")
                else:
                    raise
                time.sleep(RETRY_SLEEP_INTERVAL)
                # self.ping_check(progress_message, timeout=timeout, start_delay=start_delay)

    def reconnect(self):
        """Try to reconnect to SSH device."""
        return reconnect(self)

    def is_alive(self):
        """Check if SSH connection to device is alive."""
        return self.connection.isalive()

    # noinspection PyMethodMayBeStatic
    def is_booted(self):
        """Check if SSH device is booted."""
        return True

    def reset(self):
        """Reset router."""
        if self.connection is not None:
            self.connection.close()

    def flush(self):
        """

        """
        flush(self)

    def close(self):
        """

        """
        close(self)

    def ping_check(self,
                   progress_message=None,
                   timeout=CONNECT_TIMEOUT,
                   ping_check_delay=0):
        """Ping host to check to see if it is up.

        Args:
            progress_message (str): Message to prefix the progress bar.
            timeout (float): Time to wait in seconds for host to be reachable.
            ping_check_delay (float): Time in seconds to wait before pinging and connecting to host.

        Raises:
            RuntimeError: When host does not respond to ping after timeout seconds.
        """
        logger.debug("Pinging {} for up to {} seconds ...".format(self.ip_address, timeout))
        logger.debug("Waiting {} seconds before pinging ...".format(ping_check_delay))
        shell = Shell()
        start_time = time.time()
        stop_time = time.time() + timeout
        delay_time = time.time() + ping_check_delay
        up = False
        length = timeout
        if progress_message is not None:
            with click.progressbar(length=length, label=progress_message) as bar:
                while delay_time > time.time():
                    logger.debug("Waiting before pinging {} ...".format(int(time.time() - start_time)))
                    bar.update(1)
                    time.sleep(1)
                while stop_time > time.time() and not up:
                    response = shell.sendline_and_expect("ping -c 1 -t 1 {} "
                                                         "> /dev/null 2>&1; echo $?".format(self.ip_address), "(\d)")
                    bar.update(1)
                    up = response == "0"
        else:
            while delay_time > time.time():
                logger.debug("Waiting before pinging {} ...".format(int(time.time() - start_time)))
                time.sleep(1)
            while stop_time > time.time() and not up:
                response = shell.sendline_and_expect(
                    "ping -c 1 -t 1 {} > /dev/null 2>&1; echo $?".format(self.ip_address), "(\d)")
                up = response == "0"

        if time.time() > stop_time:
            raise RuntimeError("Unable to reach host {} after {} seconds.".format(self.ip_address, timeout))

    def send(self,
             command):
        """

        :param command:
        :type command:
        """
        self.connection.send(command)

    def sendline(self,
                 line,
                 line_terminator=NL, no_wait=False):
        """

        :param line:
        :type line:
        :param line_terminator:
        :type line_terminator:
        :param no_wait:
        :type no_wait:
        """
        sendline(self, line, line_terminator=line_terminator)
        if not no_wait:
            self.prompt()

    # noinspection PyMissingOrEmptyDocstring
    def send_and_expect(self,
                        command,
                        pattern=PROMPT,
                        timeout=COMMAND_TIMEOUT):
        return send_and_expect(self, command, pattern=pattern, timeout=timeout)

    def sendline_and_expect(self,
                            command,
                            pattern=PROMPT,
                            line_terminator=NL,
                            timeout=COMMAND_TIMEOUT):
        """

        :param command:
        :type command:
        :param pattern:
        :type pattern:
        :param line_terminator:
        :type line_terminator:
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        return send_and_expect(self,
                               command,
                               pattern=pattern,
                               line_terminator=line_terminator,
                               timeout=timeout)

    # noinspection PyMissingOrEmptyDocstring,PyMissingOrEmptyDocstring
    def expect(self,
               pattern=PROMPT,
               timeout=COMMAND_TIMEOUT):
        result = expect(self, pattern=pattern, timeout=timeout)
        self.flush()
        return result

    def prompt(self):
        """

        """
        self.connection.prompt()


# noinspection PyUnboundLocalVariable
class SerialDevice(object):
    """Class for controlling device via serial router.

    Args:
        name (str): Name for device.
        port (str): Device file name for the serial port connected.
        baud_rate (int): Baud rate (default = 115200).
        timeout=COMMAND_TIMEOUT,
        log_filename (str): Name of file for logging serial device output.
    """

    def __init__(self,
                 name=None,
                 port=DEFAULT_SERIAL_PORT,
                 baud_rate=DEFAULT_BAUD_RATE,
                 timeout=COMMAND_TIMEOUT,
                 usb_hub=None,
                 usb_port=None,
                 log_filename=SERIAL_LOG_FILENAME):

        if name is None:
            self.name = "Serial Device @ {}".format(port)
        else:
            self.name = name
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.usb_hub = usb_hub
        self.usb_port = usb_port
        self.log_filename = log_filename

        if self.log_filename is not None:
            try:
                self.log_filename = log_filename + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".log"
                self.log_file = open(log_filename, "ab+")
            except IOError:
                logger.error("Failed to open serial device log file {}".format(log_filename))
                self.log_file = None
        else:
            self.log_file = None
        self.serial_port = None
        self.connection = None
        self.connect()

    def connect(self):
        """

        :return:
        :rtype:
        """
        for retry in range(4):
            try:
                self.serial_port = serial.Serial(self.port, baudrate=self.baud_rate, xonxoff=False, )
                self.connection = fdspawn(self.serial_port, 'wb', logfile=self.log_file, timeout=self.timeout)
                return
            except (OSError, serial.SerialException):
                logger.debug(traceback.format_exc())
                logger.debug("Problem opening serial port {} .... trying again in 5 seconds.".format(self.port))
                time.sleep(RETRY_SLEEP_INTERVAL)

        logger.debug("Unable to connect to serial port. Reset port and try again ...")
        self.reset()

        for retry in range(4):
            try:
                self.serial_port = serial.Serial(self.port, baudrate=self.baud_rate, xonxoff=False, )
                self.connection = fdspawn(self.serial_port, 'wb', logfile=self.log_file, timeout=self.timeout)
                return
            except (OSError, serial.SerialException):
                logger.debug(traceback.format_exc())
                logger.debug("Problem opening serial port {} .... trying again in 5 seconds.".format(self.port))
                time.sleep(RETRY_SLEEP_INTERVAL)

        logger.debug("Opened serial port to {} with baud rate {}.".format(self.port, self.baud_rate))

    def reconnect(self):
        """Try to reconnect to SSH device."""
        return reconnect(self)

    def is_alive(self):
        """Check if serial connection to device is alive."""
        return self.serial_port.is_open

    def reset(self):
        """Try to reset the serial port by flushing port or power cycling the USB port for the serial router."""
        logger.debug("Attempting to reset router to serial port {} ...".format(self.name))
        self.close()
        if self.usb_hub is not None:
            self.usb_hub.power_cycle(self.port, 3)
        time.sleep(RESET_SLEEP_TIME)
        self.flush()
        self.sendline("", line_terminator=CRLF)

    def flush(self):
        """Flush the output bufer."""
        flush(self)

    def close(self):
        """Close serial port and fdexpect process.
        """
        # Catch OSError which is thrown by pexpect when the file descriptor is already closed. This is a known issue
        # with pexpect.
        try:
            if not self.serial_port.closed:
                self.serial_port.close()
        except OSError:
            traceback.print_exc()
            logger.debug("Problem closing serial port {}".format(self.serial_port))

    def send(self, command):
        """

        :param command:
        :type command:
        """
        self.connection.send(command)

    def sendline(self,
                 line,
                 line_terminator=NL):
        """

        :param line:
        :type line:
        :param line_terminator:
        :type line_terminator:
        """
        sendline(self, line, line_terminator=line_terminator)
        # logger.debug("Found before: {}".format(self.connection.before))
        # logger.debug("Found after: {}".format(self.connection.after))

    def send_and_expect(self, command, pattern=PROMPT, timeout=COMMAND_TIMEOUT):
        """

        :param command:
        :type command:
        :param pattern:
        :type pattern:
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        return send_and_expect(self, command, pattern=pattern, timeout=timeout)

    def sendline_and_expect(self,
                            command,
                            pattern=PROMPT,
                            line_terminator=NL,
                            timeout=COMMAND_TIMEOUT):
        """

        :param command:
        :type command:
        :param pattern:
        :type pattern:
        :param line_terminator:
        :type line_terminator:
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        return send_and_expect(self,
                               command,
                               pattern=pattern,
                               line_terminator=line_terminator,
                               timeout=timeout)

    def expect(self,
               pattern=PROMPT,
               timeout=COMMAND_TIMEOUT):
        """

        :param pattern:
        :type pattern:
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        return expect(self, pattern=pattern, timeout=timeout)

    def prompt(self):
        """Wait for the prompt."""
        prompt(self)

    # noinspection PyMethodMayBeStatic
    def is_booted(self):
        """Check if Serial device is booted."""
        return True

# TODO: Investigate using bash or zsh in Shell Class.
#       https://pexpect.readthedocs.io/en/stable/FAQ.html
#       Look at using -l option to Make bash act as if it had been invoked as a login shell (see INVOCATION below).
#       man bash
# noinspection PyUnboundLocalVariable
class Shell(object):
    """Class for controlling local device using a bash shell.

    Args:
        name (str): Name for device.
        timeout=COMMAND_TIMEOUT,
        log_filename (str): Name of file for logging serial device output.
    """

    def __init__(self,
                 name=None,
                 command=None,
                 timeout=COMMAND_TIMEOUT,
                 log_filename=SHELL_LOG_FILENAME):

        if name is None:
            self.name = " Shell"
        else:
            self.name = name
        self.log_filename = log_filename

        if self.log_filename is not None:
            try:
                self.log_filename = log_filename + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".log"
                self.log_file = open(log_filename, "ab+")
            except IOError:
                logger.error("Failed to open shell log file {}".format(log_filename))
                self.log_file = None
        else:
            self.log_file = None
        self.timeout = timeout
        self.connection = None
        self.command = command
        self.connect()

    def connect(self):
        """

        :return:
        :rtype:
        """
        for retry in range(4):
            try:
                if self.command is not None:
                    spawn_command = self.command
                else:
                    spawn_command = os.getenv('SHELL')
                self.connection = spawn(spawn_command)
                self.connection.logfile = self.log_file
                self.connection.timeout = self.timeout
                return
            except (OSError, serial.SerialException):
                logger.debug(traceback.format_exc())
                logger.debug("Problem spawning zsh shell .... trying again in 5 seconds.")
                time.sleep(RETRY_SLEEP_INTERVAL)

    def reconnect(self):
        """Try to reconnect to shell device."""
        return reconnect(self)

    # noinspection PyMethodMayBeStatic
    def is_alive(self):
        """Check if shell connection to device is alive."""
        return True

    def reset(self):
        """Placeholder for the reset method. Not used for Bash shells."""
        return

    def flush(self):
        """Placeholder for the flush method. Not used for Bash shells."""
        flush(self)

    def close(self):
        """Close bash shell and pexpect process.
        """
        # Catch OSError which is thrown by pexpect when the file descriptor is already closed. This is a known issue
        # with pexpect.
        try:
            if not self.connection.closed:
                self.connection.close()
        except OSError:
            traceback.print_exc()
            logger.debug("Problem closing bash shell")

    def send(self, command):
        """

        :param command:
        :type command:
        """
        self.connection.send(command)

    def sendline(self,
                 line,
                 line_terminator=NL):
        """

        :param line:
        :type line:
        :param line_terminator:
        :type line_terminator:
        """
        sendline(self, line, line_terminator=line_terminator)

    def send_and_expect(self, command, pattern=PROMPT, timeout=COMMAND_TIMEOUT):
        """

        :param command:
        :type command:
        :param pattern:
        :type pattern:
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        return send_and_expect(self, command, pattern=pattern, timeout=timeout)

    def sendline_and_expect(self,
                            command,
                            pattern=PROMPT,
                            line_terminator=NL,
                            timeout=COMMAND_TIMEOUT):
        """

        :param command:
        :type command:
        :param pattern:
        :type pattern:
        :param line_terminator:
        :type line_terminator:
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        return send_and_expect(self,
                               command,
                               pattern=pattern,
                               line_terminator=line_terminator,
                               timeout=timeout)

    def expect(self,
               pattern=PROMPT,
               timeout=COMMAND_TIMEOUT):
        """

        :param pattern:
        :type pattern:
        :param timeout:
        :type timeout:
        :return:
        :rtype:
        """
        return expect(self, pattern=pattern, timeout=timeout)

    def prompt(self):
        """Wait for the prompt."""
        self.connection.prompt(self)

    # noinspection PyMethodMayBeStatic
    def is_booted(self):
        """Check if Shell device is booted."""
        return True