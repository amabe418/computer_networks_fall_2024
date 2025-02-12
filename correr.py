import socket
import ssl
import threading

class IRCClient:
    def __init__(self, server, port, nickname, use_ssl=True):
        self.server = server
        self.port = port
        self.nickname = nickname
        self.use_ssl = use_ssl
        self.running = True
        
        self.sock = socket.create_connection((server, port))
        if use_ssl:
            self.sock = ssl.wrap_socket(self.sock)
        
        self.send_raw(f'NICK {self.nickname}')
        self.send_raw(f'USER {self.nickname} 0 * :Python IRC Client')
    
    def send_raw(self, data):
        self.sock.send((data + '\r\n').encode('utf-8'))
    
    def change_nick(self, new_nick):
        self.send_raw(f'NICK {new_nick}')
        self.nickname = new_nick
    
    def join_channel(self, channel):
        self.send_raw(f'JOIN {channel}')
    
    def part_channel(self, channel):
        self.send_raw(f'PART {channel}')
    
    def send_message(self, target, message):
        self.send_raw(f'PRIVMSG {target} :{message}')
    
    def send_notice(self, target, message):
        self.send_raw(f'NOTICE {target} :{message}')
    
    def quit(self, message="Goodbye!"):
        self.send_raw(f'QUIT :{message}')
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

if __name__ == "__main__":
    import sys
    
    server = "localhost"
    port = 8080
    nickname = "TestUser1"
    
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