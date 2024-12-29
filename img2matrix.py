from PIL import Image
from io import BytesIO

def main():
    outer =  Image.open('img/ring.png')
    inner =  Image.open('img/8.png')

    scale_factor = 0.3
    inner = scale_image(inner, scale_factor)
    outer = scale_image(outer, scale_factor)
    matrix_inner, matrix_outer = byte_stream(inner, outer)

    matrix_outer = remove_data_points(matrix_outer, 0.8)
    #matrix_inner = remove_data_points(matrix_inner, 0.5)

    matrix = matrix_inner + matrix_outer
    #matrix2image(matrix)
    return matrix

def byte_stream(inner, outer):
    with BytesIO() as byte_io:
        inner.save(byte_io, format='PNG')
        inner_data = byte_io.getvalue()
    matrix_inner = image2matrix(inner_data)
    with BytesIO() as byte_io:
        outer.save(byte_io, format='PNG')
        outer_data = byte_io.getvalue()
    matrix_outer = image2matrix(outer_data)
    return matrix_inner, matrix_outer

def scale_image(image, scale_factor):
    width, height = image.size
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    return image.resize((new_width, new_height))

def image2matrix(image_data):
    img = Image.open(BytesIO(image_data)).convert('RGBA')
    pixel_matrix = []
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))
            if r + g + b + a > 0 and r == 0 and g == 0 and b == 0:
                pixel_matrix.append((x, y))
    return pixel_matrix

def remove_data_points(pixel_matrix, percentage):
    if percentage <= 0.5:
        return [point for i, point in enumerate(pixel_matrix) if (i + 1) % max(1, int(1 / percentage)) != 0]
    else:
        return [point for i, point in enumerate(pixel_matrix) if (i + 1) % max(1, int(1 / (1 - percentage))) == 0]

def matrix2image(pixel_matrix):
    max_x = max(x for x, y in pixel_matrix) + 1
    max_y = max(y for x, y in pixel_matrix) + 1
    new_img = Image.new('RGB', (max_x, max_y), (255, 255, 255))
    pixels = new_img.load()
    for x, y in pixel_matrix:
        pixels[x, y] = (0, 0, 0)
    new_img.show()

matrix = main()
