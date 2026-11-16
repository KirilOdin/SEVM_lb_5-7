from src.server.network import ChatServer

if __name__ == '__main__':
    server = ChatServer()
    try:
        server.start()

    except KeyboardInterrupt:
        server.stop()

