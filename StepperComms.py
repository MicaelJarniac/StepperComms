# Required imports
import os
import sys
import serial
import time
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

ID_AMOUNT           = 38    # Amount of remote variables

# Message size
CMD_ADDR_SIZE       = 1
CMD_INFO_SIZE       = 1 + CMD_ADDR_SIZE             # 1 byte (basic info & transfer size) + 1 byte (address)
CMD_DATA_SIZE       = 61                            # 61 bytes (data)
CMD_BUFF_SIZE       = CMD_INFO_SIZE + CMD_DATA_SIZE # Command info + command data

# Message buffer and related
OutCmdBuffer        = [None] * CMD_BUFF_SIZE    # Initializes the buffer with given size
# TODO Remove not used var
OutCmdBufferId      = 0                         # Holds the current buffer position

# Message parameters
CmdType             = WRITE                     # Command type ('read' or 'write')
CmdSize             = 0                         #         size
CmdAddr             = 0                         #         address
CmdData             = [None] * CMD_DATA_SIZE    #         data

# Serial configuration parameters
SerPort             = "/dev/serial0"    # Device
SerBaud             = 9600              # Baud rate
SerTout             = 1                 # Timeout
SerDelay            = 0.05              # Delay between quick writes

# Declare serial
ser = serial.Serial(
        port                = SerPort,              # Serial port       configurable above
        baudrate            = SerBaud,              # Baudrate          configurable above
        bytesize            = serial.EIGHTBITS,     # Byte size     hardcoded 8 bits
        parity              = serial.PARITY_NONE,   # Parity        hardcoded no parity
        stopbits            = serial.STOPBITS_TWO,  # Stop bits     hardcoded 2 stopbits
        timeout             = SerTout,              # Timeout           configurable above
        xonxoff             = False,                # ?             hardcoded false
        rtscts              = False,                # ?             hardcoded false
        dsrdtr              = False,                # ?             hardcoded false
        write_timeout       = SerTout,              # Write timeout     configurable above
        inter_byte_timeout  = None)                 # ?             hardcoded none

# Remote variables
RemoteVars = [None] * ID_AMOUNT     # Stores received variables

def BuildMessage():
    # Iterates through entire message length
    for i in range(CMD_INFO_SIZE + CmdSize):
        data = 0

        # Builds first byte
        if i == 0:
            data |= RW_CMD  & BYTE_MASK             # Validation check bit
            data |= RW_MASK & (BYTE_MASK * CmdType) # Command type bit
            data |= CmdSize & TRANSFER_SIZE_MASK    # Transfer size bits
        # Builds second byte
        elif i == 1:
            data |= CmdAddr & BYTE_MASK # Address byte
        # Builds remaining bytes
        else:
            data |= CmdData[i - CMD_INFO_SIZE] & BYTE_MASK

        # Assigns built byte to its position on the message buffer
        OutCmdBuffer[i] = data & BYTE_MASK

def SendMessage():
    # Iterates through info bytes + command bytes
    for i in range(CMD_INFO_SIZE + CmdSize):
        ser.write(serial.to_bytes([OutCmdBuffer[i] & BYTE_MASK]))                  # Writes current message buffer position to the serial device
        debug("{1:02d} - {0:08b}".format(OutCmdBuffer[i], i))
        time.sleep(SerDelay)

def ReadMessage():
    # TODO Read message

def GetRemoteVars():
    CmdType = READ
    CmdSize = 0     # TODO Requires actual data size
    for i in range(ID_AMOUNT):
        CmdAddr = i
        BuildMessage()
        SendMessage()
        RemoteVars[i] = ReadMessage()

# Main loop
while True:
    # Clear serial in and out buffers
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # Placeholders
    CmdType    = WRITE
    CmdSize    = 1
    CmdAddr    = 31
    CmdData[0] = 0x1

    BuildMessage()
    SendMessage()

    debug("\n")
