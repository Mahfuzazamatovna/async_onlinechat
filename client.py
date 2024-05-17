import socket
import select
import string
import sys

# Helper function (formatting)
def display():
    you = "\33[33m\33[1m" + " You: " + "\33[0m"
    sys.stdout.write(you)
    sys.stdout.flush()

def main():
    
    if len(sys.argv) < 2:
        host = input("Enter host ip address: ")
    else:
        host = sys.argv[1]

    port = 5001
    
    # Asks for user name
    name = input("\33[34m\33[1m CREATING NEW ID:\n Enter username: \33[0m")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    
    # Connecting host
    try:
        s.connect((host, port))
    except Exception as e:
        print("\33[31m\33[1m Can't connect to the server:", e, "\33[0m")
        sys.exit()

    # If connected
    s.send(name.encode())
    display()
    while True:
        socket_list = [sys.stdin, s]
        
        # Get the list of sockets which are readable
        rList, wList, error_list = select.select(socket_list, [], [])
        
        for sock in rList:
            # Incoming message from server
            if sock == s:
                data = sock.recv(4096)
                if not data:
                    print('\33[31m\33[1m \rDISCONNECTED!!\n \33[0m')
                    sys.exit()
                else:
                    sys.stdout.write(data.decode())
                    display()
        
            # User entered a message
            else:
                msg = sys.stdin.readline()
                s.send(msg.encode())
                display()

if __name__ == "__main__":
    main()
