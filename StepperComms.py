import os
import sys
sys.path.append(os.path.dirname(os.path.expanduser('~/projects/Python-Playground/Debug')))
import serial
from Debug.Debug import Debug
debug = Debug(True, 3).prt

RW_CMD              = 0x80
TRANSFER_SIZE_MASK  = 0x3f
BYTE_MASK           = 0xff
RW_MASK             = 0x40

READ                = 1
WRITE               = 0

CMD_BUFFER_SIZE     = 68

OutCmdBuffer        = [None] * CMD_BUFFER_SIZE
OutCmdBufferId      = 0
CmdType             = 0
CmdSize             = 0
CmdAddr             = 0

PORT                = "/dev/serial0"
BAUD                = 9600
TOUT                = 1

ser = serial.Serial(PORT, BAUD, timeout = TOUT)
while True:
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    for i in range(CMD_BUFFER_SIZE):
        data = 0
        CmdType = WRITE
        CmdSize = 1
        CmdAddr = 0x2dc
        if i == 0:
            data |= RW_CMD & BYTE_MASK
            data |= RW_MASK & (BYTE_MASK * CmdType)
            data |= CmdSize & TRANSFER_SIZE_MASK
        elif i == 1:
            data |= CmdAddr & BYTE_MASK
        elif i == 2:
            data |= 0x1 & BYTE_MASK
        OutCmdBuffer[i] = data
    for i in range(CmdSize + 2):
        ser.write(OutCmdBuffer[i]);
