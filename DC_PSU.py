import enum
import numbers


class MockSocket:
    """
    This class represents a mock socket connection to the PSU.
    Lets assume we have a simple API with the PSU firmware:
    COMMANDS:

        power-on        # power on
        power-off       # power off
        reset-config    # reset to defaults

        set-X(Y)        # set amplitude to channel X-> INT channel number, Y-> Numeric channel amplitude.
        enable-X(Y)     # set channel enabled/disabled X-> INT channel number, Y-> 1=ON, 0=OFF
        on-x            # start channel injection
        off-x           # pause channel injection

    STATUS: (sent as feedback by unit)

        STATUS-OK       # command success
        STATUS-ERR      # command failure

    """
    VALID_CMDS = ['power-on', 'power-off', 'reset-config', 'set', 'enable', 'on', 'off']

    def __init__(self, ip, user, pswd):
        self.sock = None
        self.buf = []
        self.pswd = pswd
        self.user = user
        self.ip = ip

    def connect(self):
        print(f'Connected to PSU {self.ip}')

    def write(self, cmd):
        if any([cmd.startswith(v) for v in MockSocket.VALID_CMDS]):
            self.buf.append('STATUS-OK')
        else:
            self.buf.append('STATUS-ERR')

    def read(self):
        return self.buf[-1]


class DCPowerSupplyUnit:

    def __init__(self, sn, num_of_channels=2, max_amp=60):
        self.status = State.OFF
        self.socket = None
        self.sn = sn
        self.num_of_channels = num_of_channels
        self.channels = [DCChannel(i, max_amp) for i in range(num_of_channels)]

    def connect(self, ip, user, password):
        self.socket = MockSocket(ip, user, password)

    def enable_channel(self, ch_num):
        self.socket.write(f'enable-{ch_num}(1)')
        status = self.socket.read()
        if status == 'STATUS-OK':
            self.channels[ch_num - 1].on()
            return True
        return False

    def disable_channel(self, ch_num):
        self.socket.write(f'enable-{ch_num}(0)')
        status = self.socket.read()
        if status == 'STATUS-OK':
            self.channels[ch_num - 1].off()
            return True
        return False

    def set_ch_amp(self, ch_num, amp):
        self.socket.write(f'set-{ch_num}({amp})')
        status = self.socket.read()
        return status == 'STATUS-OK'

    def power_on(self):
        self.socket.write(f'power-on')
        status = self.socket.read()
        if status == 'STATUS-OK':
            self.status = State.ON
            return True
        return False

    def power_off(self):
        self.socket.write(f'power-off')
        status = self.socket.read()
        if status == 'STATUS-OK':
            self.status = State.OFF
            return True
        return False

    def reset(self):
        self.socket.write(f'reset')
        status = self.socket.read()
        return status == 'STATUS-OK'

    def channel_on(self, ch_num):
        self.socket.write(f'on-{ch_num}')
        status = self.socket.read()
        return status == 'STATUS-OK'

    def channel_off(self, ch_num):
        self.socket.write(f'off-{ch_num}')
        status = self.socket.read()
        return status == 'STATUS-OK'


class DCChannel:
    """
    Class DC Channel represents a single channel of a DC PSU.
    """

    def __init__(self, ch_num, max_amp):
        self.ch_num = ch_num
        self.state = State.OFF
        self._amp = 0
        self.max_amp = max_amp

    @property
    def amp(self):
        return self._amp

    @amp.setter
    def amp(self, num):
        if not isinstance(num, numbers.Number) and 0 <= num <= self.max_amp:
            self._amp = num
        else:
            raise ValueError(f'Cannot set value {num} to channel {self.ch_num}.')

    def _set_state(self, state):
        self.state = state

    def on(self):
        self._set_state(State.ON)

    def off(self):
        self._set_state(State.OFF)


class State(enum.Enum):
    ON = 1
    OFF = 2
