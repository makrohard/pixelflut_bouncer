import socket
import threading
from img2matrix import matrix

offset_lock = threading.Lock()

offset = (0, 0)
direction_x = 1
direction_y = 1

def main():
    server = 'wall.c3pixelflut.de'
    # server = 'newcomer.c3pixelflut.de'
    port = 1337
    res_x = 3840
    res_y = 1080
    num_threads = 5

    step = 10
    redraw_times = 10

    # Get dimensions from the matrix
    width, height = get_dimensions()
    half_x = int(width / 2)
    half_y = int(height / 2)

    commands = create_commands()

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(
            target=socket_worker,
            args=(server, port, res_x, res_y, half_x, half_y, step, redraw_times, commands)
        )
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

def socket_worker(server, port, res_x, res_y, half_x, half_y, step, redraw_times, commands):
    global offset, direction_x, direction_y
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'Connecting to {server}:{port} ...')
    sock.connect((server, port))
    print(f'Successfully connected to {server}:{port}')

    while True:
        with offset_lock:
            offset, direction_x, direction_y = new_offset(offset, half_x, half_y, direction_x, direction_y, res_x, res_y, step)
            offset_command = (f'OFFSET {offset[0]} {offset[1]}\n').encode('utf-8')
        command = offset_command + commands

        # send pixeldata
        for _ in range(redraw_times):
            sock.sendall(command)

def new_offset(offset, half_x, half_y, direction_x, direction_y, res_x, res_y, step):
    if offset[0] <= half_x:
        direction_x = 1
    if offset[0] >= res_x - half_x:
        direction_x = -1
    if offset[1] <= half_y:
        direction_y = 1
    if offset[1] >= res_y - half_y:
        direction_y = -1
    return (
        int(offset[0] + step * direction_x),
        int(offset[1] + step * direction_y)
    ), direction_x, direction_y

def get_dimensions():
    width = max(pixel[0] for pixel in matrix)
    height = max(pixel[1] for pixel in matrix)
    return width, height

def create_commands():
    commands = []
    for x, y, color in matrix:
        commands.append(f'PX {x} {y} {color}')
    commands_string = '\n'.join(commands).encode('utf-8')
    return commands_string

if __name__ == "__main__":
    main()