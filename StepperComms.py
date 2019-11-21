# Required imports
import os
import sys
import serial
sys.path.append(os.path.dirname(os.path.expanduser('~/projects/Python-Playground/Debug')))  # Update path accordingly
from Debug.Debug import Debug

# Declare debug
debug = Debug(True, 3).prt  # Simplifies debugging messages

# Message building blocks
RW_CMD              = 0x80  # Validation check
TRANSFER_SIZE_MASK  = 0x3f  # Masks bits used for transfer size
BYTE_MASK           = 0xff  # Masks 1 byte
RW_MASK             = 0x40  # Bit used for defining if 'read' or 'write' command type

READ                = 1     # Command of type 'read'
WRITE               = 0     #                 'write'

# Message size
CMD_BUFFER_SIZE     = 1 + 1 + 61    # 1 byte (basic info & transfer size) + 1 byte (address) + 61 bytes (data)

# Message buffer and related
OutCmdBuffer        = [None] * CMD_BUFFER_SIZE  # Initializes the buffer with given size
OutCmdBufferId      = 0                         # Holds the current buffer position

# Message parameters
CmdType             = 0 # Command type ('read' or 'write')
CmdSize             = 0 # Command size
CmdAddr             = 0 # Command address

# Serial configuration parameters
PORT                = "/dev/serial0"    # Device
BAUD                = 9600              # Baud rate
TOUT                = 1                 # Timeout

# Declare serial
ser = serial.Serial(PORT, BAUD, timeout = TOUT)

# Main loop
while True:
    # Clear serial in and out buffers
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # Iterates through entire message buffer
    for i in range(CMD_BUFFER_SIZE):
        data    = 0
        CmdType = WRITE
        CmdSize = 1
        CmdAddr = 31

        # Builds first byte
        if i == 0:
            data |= RW_CMD & BYTE_MASK              # Validation check bit
            data |= RW_MASK & (BYTE_MASK * CmdType) # Command type bit
            data |= CmdSize & TRANSFER_SIZE_MASK    # Transfer size bits
        # Builds second byte
        elif i == 1:
            data |= CmdAddr & BYTE_MASK # Address byte
        # Builds third byte
        elif i == 2:
            data |= 0x57 & BYTE_MASK # Placeholder

        # Assigns built byte to its position on the message buffer
        OutCmdBuffer[i] = data

    # Iterates through 2 info bytes + command bytes
    for i in range(2 + CmdSize):
        ser.write(serial.to_bytes([OutCmdBuffer[i] & BYTE_MASK]))                  # Writes current message buffer position to the serial device
        debug("{1:02d} - {0:08b}".format(OutCmdBuffer[i], i))

    debug("\n")
