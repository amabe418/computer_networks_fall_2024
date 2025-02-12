import socket
import ssl
import threading
import sys
import getopt
import time

class IRCClient:
    def __init__(self, server, port, nickname, use_ssl=True):
        self.server = server
        self.port = port
        self.nickname = nickname
        self.use_ssl = use_ssl
        self.running = True
        
        self.sock = socket.create_connection((server, port))
        if use_ssl:
            context = ssl.create_default_context()
            self.sock = context.wrap_socket(self.sock, server_hostname=server)  
        
        self.send_raw(f'NICK {self.nickname}')
        self.send_raw(f'USER {self.nickname} 0 * :Python IRC Client')
    
    def send_raw(self, data):
        self.sock.send((data + '\r\n').encode('utf-8'))
    
    def change_nick(self, new_nick):
        self.send_raw(f'NICK {new_nick}')
        print(f'Tu nuevo apodo es {new_nick}')
        self.nickname = new_nick
    
    def join_channel(self, channel):
        self.send_raw(f'JOIN {channel}')
        print(f'Te has unido al canal {channel}')
    
    def part_channel(self, channel):
        self.send_raw(f'PART {channel}')
        print(f'Has salido del canal {channel}')
    
    def send_message(self, target, message):
        self.send_raw(f'PRIVMSG {target} :{message}')
        print(f'Mensaje de {self.nickname}: {message}')
    
    def send_notice(self, target, message):
        self.send_raw(f'NOTICE {target} :{message}')
        print(f'Notificacion de {self.nickname}: {message}')
    
    def quit(self, message="Goodbye!"):
        self.send_raw(f'QUIT :{message}')
        print("Desconectado del servidor")
        self.running = False
        self.sock.close()
    
    def handle_server_response(self):
        while self.running:
            try:
                data = self.sock.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    break
                for line in data.split('\r\n'):
                    if line:
                        print(line)
                        self.process_message(line)
            except Exception as e:
                print(f'Error en la recepción: {e}')
                break
    
    def process_message(self, message):
        parts = message.split()
        if len(parts) < 2:
            return
        if parts[0] == 'PING':
            self.send_raw(f'PONG {parts[1]}')
    
    def start(self):
        thread = threading.Thread(target=self.handle_server_response)
        thread.start()

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "H:p:n:c:a:", ["port=", "host=", "nick=", "command=", "argument="])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    server = None
    port = None
    nickname = None
    command = None
    argument = None
    use_ssl = False

    for opt, arg in opts:
        if opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-H", "--host"):
            server_ip = arg
        elif opt in ("-n", "--nick"):
            nickname = arg
        elif opt in ("-c", "--command"):
            command = arg
        elif opt in ("-a", "--argument"):
            argument = arg


    client = IRCClient(server, port, nickname)
    client.start()
    
    while True:
        cmd = input().strip().split(" ", 1)
        if not cmd:
            continue
        command = cmd[0]
        argument = cmd[1] if len(cmd) > 1 else ""
        
        if command == "/nick":
            client.change_nick(argument)
        elif command == "/join":
            client.join_channel(argument)
        elif command == "/part":
            client.part_channel(argument)
        elif command == "/privmsg":
            target, message = argument.split(" ", 1)
            client.send_message(target, message)
        elif command == "/notice":
            target, message = argument.split(" ", 1)
            client.send_notice(target, message)
        elif command == "/quit":
            client.quit(argument)
            break
