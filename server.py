import socket
import select
import datetime  # Added for logging timestamps

# Function to send message to all connected clients
def send_to_all(sock, message):
    # Message not forwarded to server and sender itself
    for socket in connected_list:
        if socket != server_socket and socket != sock:
            try:
                socket.send(message.encode())
            except:
                # If connection not available
                socket.close()
                connected_list.remove(socket)

if __name__ == "__main__":
    name = ""
    # Dictionary to store address corresponding to username
    record = {}
    # List to keep track of socket descriptors
    connected_list = []
    buffer = 4096
    port = 5001

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind(("localhost", port))
    server_socket.listen(10)  # Listen at most 10 connections at one time

    # Add server socket to the list of readable connections
    connected_list.append(server_socket)

    # Display message when server starts
    print("\033[1;32mSERVER IS WORKING!\033[0m")

    log_file = open("chat_log.txt", "a")

    try:
        while True:
            # Get the list sockets which are ready to be read through select
            rList, wList, error_sockets = select.select(connected_list, [], [])

            for sock in rList:
                # New connection
                if sock == server_socket:
                    # Handle the case in which there is a new connection received through server_socket
                    sockfd, addr = server_socket.accept()
                    name = sockfd.recv(buffer).decode()
                    connected_list.append(sockfd)
                    record[addr] = ""
                    # if repeated username
                    if name in record.values():
                        sockfd.send("\r\033[1;31m Username already taken!\033[0m".encode())
                        del record[addr]
                        connected_list.remove(sockfd)
                        sockfd.close()
                        continue
                    else:
                        # Add name and address
                        record[addr] = name
                        print("Client (%s, %s) connected" % addr, " [", record[addr], "]")
                        sockfd.send("\033[1;32m\r Welcome to chat room. Enter 'exit' anytime to exit\033[0m".encode())
                        send_to_all(sockfd, "\033[1;32m\r " + name + " joined the conversation \033[0m \n")

                # Some incoming message from a client
                else:
                    # Data from client
                    try:
                        data1 = sock.recv(buffer)
                        # get address of client sending the message
                        i, p = sock.getpeername()
                        data = data1[:data1.index(b"\n")].decode()
                        if data == "exit":
                            msg = "\r\033[1m" + "\033[1;31m " + record[(i, p)] + " left the conversation \033[0m\n"
                            send_to_all(sock, msg)
                            print("Client (%s, %s) is offline" % (i, p), " [", record[(i, p)], "]")
                            del record[(i, p)]
                            connected_list.remove(sock)
                            sock.close()
                            continue
                        else:
                            # Log client message
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            log_msg = f"[{timestamp}] {record[(i, p)]}: {data}"
                            print(log_msg)
                            log_file.write(log_msg + "\n")
                            
                            msg = "\r\033[1m" + "\033[1;35m " + record[(i, p)] + ": " + "\033[0m" + data + "\n"
                            send_to_all(sock, msg)
                    # Abrupt user exit
                    except:
                        (i, p) = sock.getpeername()
                        send_to_all(sock, "\r\033[1;31m \033[1m" + record[(i, p)] + " left the conversation unexpectedly\033[0m\n")
                        print("Client (%s, %s) is offline (error)" % (i, p), " [", record[(i, p)], "]\n")
                        log_file.write(f"[{timestamp}] Client ({i}, {p}) is offline (error) [ {record[(i, p)]} ]\n")
                        del record[(i, p)]
                        connected_list.remove(sock)
                        sock.close()
                        continue
    except KeyboardInterrupt:
        # Display message when server stops
        print("\n\033[1;31mSERVER STOPPED!\033[0m")
        log_file.close()
        server_socket.close()
