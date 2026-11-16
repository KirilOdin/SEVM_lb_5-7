from src.client.network import ChatClient
import time


def print_msg(msg):
    print(f"\n[MESSAGE] {msg}")


def on_conn():
    print("\nУспешное подключение!")


if __name__ == '__main__':
    username = input("Введите логин для входа: ")


    client = ChatClient(on_message=print_msg, on_connected=on_conn)

    client.connect(username)

    try:
        # Простой цикл для отправки сообщений из консоли
        while True:
            text = input("> ")
            if text.lower() == 'exit':
                break
            client.send_message(text)
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()