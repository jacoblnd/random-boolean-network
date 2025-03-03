from PIL import Image
import math

from network import Network, edge_algorithm_uniform

def generate_image_slice(node_states: list[int]):
    return [0 if node_state == 0 else 255 for node_state in node_states]


def write_image_slice(column, pixels, node_states):
    for pixel_row, pixel_value in enumerate(generate_image_slice(node_states)):
        pixels[column, pixel_row] = pixel_value


def get_disturbance_time_slices(
    num_disturbances: int,
    total_time_slices: int
):
    disturbance_period = math.floor(total_time_slices / (num_disturbances+1))
    current_disturbance_slice = disturbance_period
    disturbance_times = [current_disturbance_slice]
    for _ in range(num_disturbances - 1):
        current_disturbance_slice += disturbance_period
        disturbance_times.append(current_disturbance_slice)
    return disturbance_times


def generate_image(
    network: Network,
    num_transitions: int,
    num_disturbances: int = 0,
    disturbance_factor: float = 0.2
):
    width = num_transitions
    height = network.num_nodes
    image = Image.new("L", (width, height))
    pixels = image.load()
    # Write first state
    write_image_slice(0, pixels, network.node_states)
    disturbance_times = None
    if num_disturbances != 0:
        disturbance_times = get_disturbance_time_slices(num_disturbances, total_time_slices=num_transitions)
    print("Disturbance times: ", disturbance_times)
    for i in range(num_transitions):
        if disturbance_times is not None and i in disturbance_times:
            print("INTRODUCING DISTURBANCE")
            network.introduce_disturbance(disturbance_factor)
        network.transition_state()
        write_image_slice(column=i, pixels=pixels, node_states=network.node_states)
    
    image.save("myimage.bmp")


def main():
    network = Network(40, 400, edge_algorithm=edge_algorithm_uniform, node_rule_activation_probability=0.5)
    network.print_stats()
    # print(network.adjacency_list)
    generate_image(network, 2000, num_disturbances=4, disturbance_factor=0.0)
   
if __name__ == "__main__":
    main()
