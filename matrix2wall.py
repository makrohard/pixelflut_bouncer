import socket
import threading
import queue
from img2matrix import matrix

data_queue = queue.Queue(maxsize=1000)

def main():
    server = 'wall.c3pixelflut.de'
    # server = 'newcomer.c3pixelflut.de'
    num_threads = 3
    port = 1337
    res_x = 3840
    res_y = 1080
    offset = (100, 100)
    step = 10
    redraw_times = 10

    # get dimensions from the matrix
    width, height = get_dimensions()
    half_x = int(width / 2)
    half_y = int(height / 2)

    # create commands
    commands = create_commands()

    # launch threads
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(
            target=socket_worker,
            args=(server, port, data_queue, redraw_times)
        )
        thread.start()
        threads.append(thread)

    # offset variables
    offset = (0, 0)
    direction_x = 1
    direction_y = 1

    # feed queue
    while True:

        offset, direction_x, direction_y = new_offset(
            offset, half_x, half_y, direction_x, direction_y, res_x, res_y, step
        )
        offset_command = f'OFFSET {offset[0]} {offset[1]}\n'.encode('utf-8')
        command = offset_command + commands

        try:
            data_queue.put_nowait(command)
            print(f'offset: {offset}')
        except queue.Full:
            while data_queue.full():
                pass

def socket_worker(server, port, data_queue, redraw_times):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'Connecting to {server} ...')
    sock.connect((server, port))
    print('Connection established.\n')

    # write pixeldata
    while True:
        command = data_queue.get()
        for _ in range(redraw_times):
            sock.sendall(command)
        data_queue.task_done()

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
    # get the dimensions of the image matrix
    width = max(pixel[0] for pixel in matrix)
    height = max(pixel[1] for pixel in matrix)
    return width, height

def create_commands():
    # generate pixel commands from matrix
    commands = []
    for x, y, color in matrix:
        commands.append(f'PX {x} {y} {color}')
    commands_string = '\n'.join(commands).encode('utf-8')
    return commands_string

if __name__ == '__main__':
    main()
