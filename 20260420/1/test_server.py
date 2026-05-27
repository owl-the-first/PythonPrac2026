import multiprocessing
import socket
import time
import unittest

from mood.server.__main__ import serve

HOST = "localhost"
PORT = 1337


class ServerFromClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = multiprocessing.Process(target=serve)
        cls.server.start()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.join()

    def setUp(self):
        self.sock = socket.create_connection((HOST, PORT))
        self.sock.settimeout(0.2)
        self.username = f"tester_{time.time_ns()}"
        self.sock.sendall((self.username + "\n").encode())
        self.read_available(1)

    def tearDown(self):
        self.sock.close()

    def send_command(self, command):
        self.sock.sendall((command + "\n").encode())
        time.sleep(0.2)
        return self.read_available(1)

    def read_available(self, seconds):
        data = ""
        finish_time = time.time() + seconds
        while time.time() < finish_time:
            try:
                data += self.sock.recv(4096).decode()
            except TimeoutError:
                pass
        return data

    def test_addmon(self):
        response = self.send_command('addmon dragon "hello" 35 1 2')
        self.assertIn("dragon", response)
        self.assertIn("(1, 2)", response)

    def test_encounter(self):
        self.send_command('addmon dragon "hello" 35 1 1')
        self.send_command("move 1 0")
        response = self.send_command("move 0 1")
        self.assertIn("Moved to (1, 1)", response)
        self.assertIn("MONSTER dragon hello", response)

    def test_attack(self):
        self.send_command('addmon dragon "hello" 15 1 2')
        response = self.send_command("attack dragon sword 10")
        self.assertIn("dragon", response)
        self.assertIn("10", response)


if __name__ == "__main__":
    unittest.main()

