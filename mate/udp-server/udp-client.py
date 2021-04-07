import socket
import json

msgFromClient = "Hello UDP Server"

bytesToSend = str.encode(msgFromClient)

serverAddressPort = ("127.0.0.1", 20001)

bufferSize = 128

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
for i in range(0, 10000):
    send_message = json.dumps({'motorid': 1, 'pwm': i}).encode('utf-8')
    UDPClientSocket.sendto(send_message, serverAddressPort)
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)

msg = "Message from Server {}".format(msgFromServer[0])

