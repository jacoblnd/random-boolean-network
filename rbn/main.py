from PIL import Image
import random
from network import Network, edge_algorithm_uniform

def generate_sample_image():
    # Define image dimensions
    width = 256
    height = 256
    black = 0
    white = 255

    # Create a new RGB image (you can also use "L" for grayscale)
    image = Image.new("L", (width, height))

    # Access pixel data
    pixels = image.load()

    # Iterate through pixels and set colors (example: gradient)
    for y in range(height):
        for x in range(width):
            pixels[x, y] = white if random.choice([True, False]) else black

    # Save the image as a BMP file
    image.save("gradient_bitmap.bmp")


def generate_image_slice(node_states: list[int]):
    return [0 if node_state == 0 else 255 for node_state in node_states]


def write_image_slice(column, pixels, node_states):
    for pixel_row, pixel_value in enumerate(generate_image_slice(node_states)):
        pixels[column, pixel_row] = pixel_value


def generate_image(network: Network, num_transitions: int):
    width = num_transitions
    height = network.num_nodes
    image = Image.new("L", (width, height))
    pixels = image.load()
    # Write first state
    write_image_slice(0, pixels, network.node_states)
    for i in range(num_transitions):
        network.transition_state()
        write_image_slice(column=i, pixels=pixels, node_states=network.node_states)
    
    image.save("myimage.bmp")


def main():
    network = Network(1000, 2000, edge_algorithm=edge_algorithm_uniform, edge_transition_probability=0.2)
    generate_image(network, 10000)
   
if __name__ == "__main__":
    main()
