import socket
my_socket = socket.socket()
my_socket.connect(('127.0.0.1', 8820))
message = ""

print("length are in mm\n")

while (message != "quit"):
    message = input('Enter data: ')
    my_socket.send(bytes(message, 'utf-8'))
    response_data = my_socket.recv(1024)
    print("Received: %s" % response_data)

my_socket.close
