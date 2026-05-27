import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock

from mood.client.__main__ import MudClient


class ClientCommandTest(unittest.TestCase):
    def setUp(self):
        self.sock = Mock()
        self.client = MudClient(self.sock)

    def sent_text(self):
        return self.sock.sendall.call_args[0][0].decode()

    def test_addmon_protocol(self):
        self.client.onecmd('addmon dragon hello "Who goes there?" hp 35 coords 1 2')
        self.assertEqual(
            self.sent_text(),
            "addmon dragon 'Who goes there?' 35 1 2\n",
        )

    def test_addmon_protocol_second_values(self):
        self.client.onecmd('addmon abcdefgh hello "meow meow" hp 10 coords 3 4')
        self.assertEqual(
            self.sent_text(),
            "addmon abcdefgh 'meow meow' 10 3 4\n",
        )

    def test_attack_protocol(self):
        self.client.onecmd("attack dragon with axe")
        self.assertEqual(self.sent_text(), "attack dragon axe 20\n")

    def test_attack_protocol_second_values(self):
        self.client.onecmd("attack dragon with spear")
        self.assertEqual(self.sent_text(), "attack dragon spear 15\n")

    def test_bad_weapon(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.client.onecmd("attack dragon with stick")
        self.assertIn("Unknown weapon", output.getvalue())
        self.sock.sendall.assert_not_called()


if __name__ == "__main__":
    unittest.main()

