CHOKE_TYPE = 0
UNCHOKE_TYPE = 1
INTERESTED_TYPE = 2
NOT_INTERESTED_TYPE = 3
HAVE_TYPE = 4
BITFIELD_TYPE = 5
REQUEST_TYPE = 6
PIECE_TYPE = 7

# ---------------Use for handshake----------------
HEADER = b"P2PFILESHARINGPROJ"
ZEROS = b"\x00" * 10
HANDSHAKE_MSG_LENGTH = 32  # 32 bytes in total
# ------------------------------------------------
