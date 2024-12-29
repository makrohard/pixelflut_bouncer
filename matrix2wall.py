import socket
from img2matrix import matrix

def main():
    server = 'wall.c3pixelflut.de'
    #server = 'newcomer.c3pixelflut.de'
    port = 1337
    res_x = 3840
    res_y = 1080
    color = 'FF0000'
    width, height = get_dimensions()
    half_x = int(width/2)
    half_y = int(height/2)
    offset = (half_x, res_y / 2)
    direction_x = 1
    direction_y = 1
    step = 10
    redraw_times = 10

    commands = create_commands(color)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'Connecting to %s:%s ...' % (server, port))
    sock.connect((server, port))
    print('\nSending floodpixel!')

    while True:
        offset, direction_x, direction_y = new_offset(offset, half_x, half_y, direction_x, direction_y, res_x, res_y, step)
        offset_command = (f'OFFSET %i %i\n' % (offset[0], offset[1])).encode('utf-8')
        command = offset_command + commands

        print(offset)

        for i in range(redraw_times):
            sock.sendall(command)
    sock.close()

def new_offset(offset, half_x, half_y, direction_x, direction_y, res_x, res_y, step):
        #return (1,1), 1, 1
        if (offset[0] <= half_x):
            direction_x = 1
        if (offset[0] >= res_x - half_x):
            direction_x = -1
        if (offset[1] <= half_y):
            direction_y = 1
        if (offset[1] >= res_y - half_y):
            direction_y = -1
        return (int(offset[0] + step * direction_x),int(offset[1] + step * direction_y)), direction_x, direction_y

def get_dimensions():
    width = (max(x for x, y in matrix))+1
    height = (max(y for x, y in matrix))+1
    return width, height


def create_commands(color):
    commands = []
    for x, y in matrix:
        commands.append(f'PX {x} {y} {color}')
    commands_string = '\n'.join(commands).encode('utf-8')
    return commands_string

if __name__ == "__main__":
    main()
