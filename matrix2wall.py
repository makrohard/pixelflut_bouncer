import socket
import threading
import queue
from img2matrix import matrix

# uses pixelmatrix to send commands to pixelflut server
# queue is fed in main process and send to sockets by threads
# image is moving and bouncing on the edges

data_queue = queue.Queue(maxsize=500) # <- - - ADJUSTME

def main():
    server = 'wall.c3pixelflut.de' # specify server + port
    port = 1337
    num_threads = 1  # <- - - - - - - - - - - - SCALING - more threads, more data
    res_x = 3840 # nc server port SIZE
    res_y = 1080
    step = 3 # <- - - - - - - - - - - - - - - - MOVEMENT - how many pixels to move
    redraw_times = 5 # <- - - - - - - - - - - - COVERAGE - how many times image is sent to same position (per thread)
    offset = (0, 0) # initial offset
    direction_x = 1 # where to move to
    direction_y = 1

    # get dimensions from the matrix
    width, height = get_dimensions()
    half_x = int(width / 2)
    half_y = int(height / 2)

    # create commands for pixelflut server
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
    # send data to pixelflut server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'Connecting to {server} ...')
    sock.connect((server, port))
    print('Connection established.\n')

    while True:
        command = data_queue.get()
        for _ in range(redraw_times):
            sock.sendall(command)
        data_queue.task_done()

def get_dimensions():
    # get dimensions of the image matrix
    width = max(pixel[0] for pixel in matrix)
    height = max(pixel[1] for pixel in matrix)
    return width, height

def create_commands():
    # generate pixelflut commands from matrix
    commands = []
    for x, y, color in matrix:
        commands.append(f'PX {x} {y} {color}')
    commands_string = '\n'.join(commands).encode('utf-8')
    return commands_string

def new_offset(offset, half_x, half_y, direction_x, direction_y, res_x, res_y, step):
    # check if border is touched, move and return new position
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

if __name__ == '__main__':
    main()
