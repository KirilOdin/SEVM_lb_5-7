from src.server.network import ChatServer
from src.server.gui import ServerGUI
# if __name__ == '__main__':
#     server = ChatServer()
#     try:
#         server.start()
#
#     except KeyboardInterrupt:
#         server.stop()
#

if __name__ == '__main__':
    app = ServerGUI()
    app.run()
