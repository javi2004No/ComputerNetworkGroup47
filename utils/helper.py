import struct


def build_msg(msg_type: int, payload: bytes = b"") -> bytes:
    """
    msg type defined in constant file to determine which type of message, is it choke unchoke, interested, not interested, have, bitfield, etc

    message will have message length + message type + payload
    """
    return struct.pack(">I", len(payload) + 1) + bytes([msg_type]) + payload


def send_msg(socket, msg_type: int, payload=b"") -> None:
    """
    Helper function to send a message with the given type and payload.

    Structure of the message:
    - 4 bytes for message length
    - 1 byte for message type
    - Payload (variable length)
    """
    length = 1 + len(payload)  # 1 byte for msg_type
    socket.sendall(struct.pack(">I", length) + bytes([msg_type]) + payload)


def recv_exact(socket, n) -> bytes:
    """
    Helper function to receive exactly n bytes from the socket.
    """
    data = b""
    while len(data) < n:
        chunk = socket.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Connection closed while receiving data")
        data += chunk
    return data


def recv_msg(socket) -> tuple[int, bytes]:
    """
    Helper function to receive a message from the socket.

    Returns a tuple containing the message type and the payload.
    """
    length = struct.unpack(">I", socket.recv(4))[0]  # since message length is 4 bytes
    body = recv_exact(
        socket, length
    )  # read the rest of message into n bytes, first byte is message type, the rest is payload
    msg_type = body[0]
    return msg_type, body[1:]
