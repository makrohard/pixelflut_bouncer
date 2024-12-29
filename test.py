import socket
from img2matrix import matrix

def main():
    server = 'wall.c3pixelflut.de'
    port = 1337
    res_x = 3840
    res_y = 1080

    redraw_times = 10

    commands = create_commands()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'Connecting to %s:%s ...' % (server, port))
    sock.connect((server, port))
    print('\nSending floodpixel!')

    while True:
        for i in range(redraw_times):
            sock.sendall(commands)
    sock.close()

def create_commands(color):
    commands = []
    for x in range(100):
        for y in range(100):
            commands.append(f'PX {x} {y}')

    commands_string = '\n'.join(commands).encode('utf-8')
    return commands_string


if __name__ == "__main__":
    main()
