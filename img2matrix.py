from PIL import Image, ImageDraw
from io import BytesIO

# create matrix with x/y-coords + color
# from fully black pixel of .png images

def main():
    # open images
    outer =  Image.open('img/O.png')
    inner =  Image.open('img/A.png')

    # scale images
    scale_factor = 0.5
    inner = scale_image(inner, scale_factor)
    outer = scale_image(outer, scale_factor)

    # create matrix of fully black pixels
    color_inner = 'FFFFFF'
    color_outer = 'FF0000'
    matrix_inner, matrix_outer = byte_stream(inner, outer, color_inner, color_outer)

    # remove every nth pixel
    matrix_outer = remove_data_points(matrix_outer, 0.3)
    matrix_inner = remove_data_points(matrix_inner, 0.3)

    # combine inner and outer image
    matrix = matrix_inner + matrix_outer
    matrix2image(matrix)
    return matrix

# scale the image
def scale_image(image, scale_factor):
    width, height = image.size
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    return image.resize((new_width, new_height))

# use scaled image to create pixelmatrix
def byte_stream(inner, outer, color_inner, color_outer):
    with BytesIO() as byte_io:
        inner.save(byte_io, format='PNG')
        inner_data = byte_io.getvalue()
    matrix_inner = image2matrix(inner_data, color_inner)
    with BytesIO() as byte_io:
        outer.save(byte_io, format='PNG')
        outer_data = byte_io.getvalue()
    matrix_outer = image2matrix(outer_data, color_outer)
    return matrix_inner, matrix_outer

# write black pixels from image to pixelmatrix
def image2matrix(image_data, color):
    img = Image.open(BytesIO(image_data)).convert('RGBA')
    pixel_matrix = []
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))
            if r + g + b + a > 0 and r == 0 and g == 0 and b == 0:
                pixel_matrix.append((x, y, color))
    return pixel_matrix

# make datapackage smaller by removing pixel
def remove_data_points(pixel_matrix, percentage):
    if percentage <= 0.5:
        return [point for i, point in enumerate(pixel_matrix) if (i + 1) % max(1, int(1 / percentage)) != 0]
    else:
        return [point for i, point in enumerate(pixel_matrix) if (i + 1) % max(1, int(1 / (1 - percentage))) == 0]

# re-convert pixelmatrix to image and display the result
def matrix2image(pixel_matrix):
    bg_color = (0, 0, 0, 255)
    width = max(pixel[0] for pixel in pixel_matrix)
    height = max(pixel[1] for pixel in pixel_matrix)
    img = Image.new('RGBA', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    for x, y, color in pixel_matrix:
        rgb_color= tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        draw.point((x, y), fill=rgb_color)
    img.show()  #< - - - - - comment this line to prevent image popup on start - - - -

matrix = main()
