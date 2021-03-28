import unittest

from CapsLockListener import start_listen


class MyTestCase(unittest.TestCase):
    def test_listener(self):
        start_listen()
        x = 0


if __name__ == '__main__':
    unittest.main()
