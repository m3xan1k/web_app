import socket
import os
from views import index, about


IP_ADDR = '0.0.0.0'
HOSTNAME = os.environ.get('HOSTNAME', 'localhost')
PORT = 8080

URLS = {
    '/': index,
    '/about': about,
}

REDIRECTS = ['/home', '/index']


def parse_request(request):
    """
    Парсим http запрос для получения метода и пути
    """
    splitted_request = request.split(' ')
    method = splitted_request[0]
    url = splitted_request[1]
    return method, url


def generate_headers(method, url):
    """
    Создаем заголовок ответа, обрабатываем ошибки
    """
    if method != 'GET':
        return ('HTTP/1.1 405 Method not allowed\n\n', 405)
    if url in REDIRECTS:
        return ('HTTP/1.1 301 Moved permanently\n', 301)
    if not URLS.get(url):
        return ('HTTP/1.1 404 Page not found\n\n', 404)
    return ('HTTP/1.1 200 OK\n\n', 200)


def generate_content(code, url):
    """
    Создаем тело http ответа
    """
    if code == 405:
        return '<h1>405 Method not allowed</h1>'
    if code == 404:
        return '<h1>404 Page not found</h1>'
    if code == 301:
        return f'Location: http://{HOSTNAME}:{PORT}\n\n'
    return URLS.get(url)()


def generate_response(request):
    """
    Пайплайн генерации ответа на запрос
    """
    method, url = parse_request(request)
    header, code = generate_headers(method, url)
    content = generate_content(code, url)
    return f'{header}{content}'.encode()


def run():
    """
    Инстанцируем веб-сервер
    """
    # уточняем семейство и тип сокета(AF_INET - сетевой, SOCK_STREAM - TCP)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        # занимаем сокет (адрес, порт)
        server.bind((IP_ADDR, PORT))
        # декларируем закрытие сокета при завершении процесса
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # открываем сокет для приёма данных
        server.listen(1)
        while True:
            # в случае подключения к сокету получаем сокет клиента и его адрес
            client_socket, client_addr = server.accept()
            # байты полученые от клиентского сокета(запрос)
            request = client_socket.recv(4096)

            print(client_addr, request)

            # готовим ответ в зависимости от запроса
            response = generate_response(request.decode('utf-8'))
            # отправляем клиенту ответ
            client_socket.sendall(response)
            # закрываем сокет
            client_socket.close()


if __name__ == '__main__':
    run()
