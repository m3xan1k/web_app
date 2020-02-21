import socket


HOST = '0.0.0.0'
PORT = 80

URLS = [
    '/about',
    '/home'
]


def parse_request(request):
    pass


def generate_headers():
    pass


def generate_content():
    pass


def generate_response(request):
    print(request)
    return b'<h1>Hello</h1>'


def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.listen(1)
        while True:
            client_socket, client_addr = server.accept()
            request = client_socket.recv(4096)

            print(client_addr, request)

            response = generate_response(request.decode('utf-8'))
            client_socket.sendall(response)
            client_socket.close()


if __name__ == '__main__':
    run()
