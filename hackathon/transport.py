from __future__ import absolute_import

import abc
import socket
import ssl
import struct

import riemann_pb2

# Default arguments
HOST = 'localhost'
PORT = 5555
TIMEOUT = None

def socket_recvall(socket, length, bufsize=4096):
    """A helper method to read of bytes from a socket to a maximum length"""
    data = b""
    while len(data) < length:
        data += socket.recv(bufsize)
    return data

class RiemannError(Exception):
    """Raised when the Riemann server returns an error message"""
    pass

class Transport(object):
    """Abstract transport definition

    Subclasses must implement the :py:meth:`.connect`, :py:meth:`.disconnect`
    and :py:meth:`.send` methods.

    Can be used as a context manager, which will call :py:meth:`.connect` on
    entry and :py:meth:`.disconnect` on exit.
    """

    __metaclass__ = abc.ABCMeta

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def disconnect(self):
        pass

    @abc.abstractmethod
    def send(self):
        pass

class SocketTransport(Transport):
    """Provides common methods for Transports that use a sockets"""

    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port

    @property
    def address(self):
        """
        :returns: A tuple describing the address to connect to
        :rtype: (host, port)
        """
        return self.host, self.port

    @property
    def socket(self):
        """Returns the socket after checking it has been created"""
        if not hasattr(self, '_socket'):
            raise RuntimeError("Transport has not been connected!")
        return self._socket

    @socket.setter
    def socket(self, value):
        self._socket = value

class UDPTransport(SocketTransport):
    def connect(self):
        """Creates a UDP socket"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def disconnect(self):
        """Closes the socket"""
        self.socket.close()

    def send(self, message):
        """Sends a message, but does not return a response

        :returns: None - can't receive a response over UDP
        """
        self.socket.sendto(message.SerializeToString(), self.address)
        return None

class TCPTransport(SocketTransport):
    def __init__(self, host=HOST, port=PORT, timeout=TIMEOUT):
        """Communicates with Riemann over TCP

        :param str host: The hostname to connect to
        :param int port: The port to connect to
        :param int timeout: The time in seconds to wait before raising an error
        """
        super(TCPTransport, self).__init__(host, port)
        self.timeout = timeout

    def connect(self):
        """Connects to the given host"""
        self.socket = socket.create_connection(self.address, self.timeout)

    def disconnect(self):
        """Closes the socket"""
        self.socket.close()

    def send(self, message):
        """Sends a message to a Riemann server and returns it's response

        :param message: The message to send to the Riemann server
        :returns: The response message from Riemann
        :raises RiemannError: if the server returns an error
        """
        message = message.SerializeToString()
        self.socket.sendall(struct.pack('!I', len(message)) + message)

        length = struct.unpack('!I', self.socket.recv(4))[0]
        response = riemann_pb2.Msg()
        response.ParseFromString(socket_recvall(self.socket, length))

        if not response.ok:
            raise RiemannError(response.error)

        return response
