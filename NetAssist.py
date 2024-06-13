from socket import AF_INET, SOCK_STREAM, socket


ENCODING='utf-8'

class TcpClient:
    # def __init__(self, host, port):
    #     self.host = host
    #     self.port = port
    def run(self):
        host = input("Enter host: ")
        port = input("Enter port: ")
        if not host:
            host = "127.0.0.1"
        if not port:
            port = '8990'
        tcp_client = socket(AF_INET, SOCK_STREAM)
        tcp_client.connect((host, int(port)))
        while True:
            message = input("Enter message: ")
            if message == "exit":
                tcp_client.close()
                break
            tcp_client.send(message.encode(ENCODING))

def main():
    client = TcpClient()
    client.run()

if __name__ == '__main__':
    main()