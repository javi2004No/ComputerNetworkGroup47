import datetime
import threading


def _get_time():
    return str(datetime.datetime.now()) + ": "


class logger:
    def __init__(self, id):
        self._id = id
        self._file = open("log_peer_" + str(id) + ".log", "w")
        self._lock = threading.Lock()

    def log_tcp_connection(self, id_to, connected_to):
        with self._lock:
            if connected_to:
                self._file.write(
                    _get_time() + "Peer " + str(self._id) + " makes a connection to Peer " + str(id_to) + ".\n")
            else:
                self._file.write(
                    _get_time() + "Peer " + str(self._id) + " is connected from Peer " + str(id_to) + ".\n")
            self._file.flush()

    def log_change_of_preferred_neighbors(self, preferred_neighbors):
        with self._lock:
            to_write = _get_time() + "Peer " + str(self._id) + "has the preferred neighbors"
            if preferred_neighbors:
                to_write += " " + str(preferred_neighbors[0])
                for neighbor in preferred_neighbors[1:]:
                    to_write += ", " + str(neighbor)
            to_write += "."
            self._file.write(to_write)
            self._file.flush()

    def log_change_of_optimistically_unchoked_neighbor(self, id_to):
        with self._lock:
            self._file.write(
                _get_time() + "Peer " + str(self._id) + " has the optimistically unchoked neighbor " + str(id_to) + ".\n")
            self._file.flush()

    def log_unchoked(self, id_from):
        with self._lock:
            self._file.write(_get_time() + "Peer " + str(self._id) + " is unchoked by " + str(id_from) + ".\n")
            self._file.flush()

    def log_choked(self, id_from):
        with self._lock:
            self._file.write(_get_time() + "Peer " + str(self._id) + " is choked by " + str(id_from) + ".\n")
            self._file.flush()

    def log_received_have(self, id_from, piece_index):
        with self._lock:
            self._file.write(_get_time() + "Peer " + str(self._id) + " received the 'have' message from " + str(id_from)
                             + " for the piece " + str(piece_index) + ".\n")
            self._file.flush()

    def log_received_interested(self, id_from):
        with self._lock:
            self._file.write(
                _get_time() + "Peer " + str(self._id) + " received the 'interested' message from  " + str(id_from) + ".\n")
            self._file.flush()

    def log_received_not_interested(self, id_from):
        with self._lock:
            self._file.write(
                _get_time() + "Peer " + str(self._id) + " received the 'not interested' message from  " + str(id_from)
                + ".\n")
            self._file.flush()

    def log_downloaded_piece(self, id_from, piece_index, number_of_pieces):
        with self._lock:
            self._file.write(_get_time() + "Peer " + str(self._id) + " has downloaded the piece " + str(piece_index) +
                             " from " + str(id_from) + ". Now the number of pieces it has is " + str(number_of_pieces)
                             + ".\n")
            self._file.flush()

    def log_completed_download(self):
        with self._lock:
            self._file.write(_get_time() + "Peer " + str(self._id) + " has downloaded the complete file.\n")
            self._file.flush()

    def close(self):
        self._file.close()

