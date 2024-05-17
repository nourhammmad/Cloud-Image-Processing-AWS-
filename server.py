import socket

import cv2

import numpy as np

from mpi4py import MPI

import os


comm = MPI.COMM_WORLD

rank = comm.Get_rank()

size = comm.Get_size()


def get_ip_address():
    return os.popen('hostname -I').read().strip()


def process_image(image, operation):
    try:
        if image is None or image.size == 0:
            print(f"Received empty or invalid image data.")
            return None

        print(f"Processing image with shape: {image.shape}, operation: {operation}")

        # Perform the specified image processing operation
        if operation == 'edge_detection':
            processed_image = cv2.Canny(image, 100, 200)
        elif operation == 'color_inversion':
            processed_image = cv2.bitwise_not(image)
        elif operation == 'resize':
            processed_image = cv2.resize(image, (int(image.shape[1] / 2), int(image.shape[0] / 2)))
        elif operation == 'blur':
            processed_image = cv2.GaussianBlur(image, (25, 25), 0)
        elif operation == 'erosion':
            kernel = np.ones((25, 25), np.uint8)
            processed_image = cv2.erode(image, kernel, iterations=1)
        elif operation == 'dilation':
            kernel = np.ones((25, 25), np.uint8)
            processed_image = cv2.dilate(image, kernel, iterations=1)
        else:
            processed_image = image

        print(f"Image processing complete for operation: {operation}")

        return processed_image

    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def int_to_bytes(n):
    return n.to_bytes(4, byteorder='big')


def bytes_to_int(b):
    return int.from_bytes(b, byteorder='big')


def split_image(image, num_parts):
    h, w = image.shape[:2]

    split_height = h // num_parts

    return [image[i * split_height:(i + 1) * split_height, :] for i in range(num_parts)]


def merge_images(images):
    return cv2.vconcat(images)


def start_server(server_ip, server_port):
    try:


        if rank == 0:


            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            server_socket.bind((server_ip, server_port))

            server_socket.listen(1)

            print(f"Server listening on {server_ip}:{server_port}", flush=True)

            while True:


                client_socket, client_address = server_socket.accept()

                print(f"Accepted connection from {client_address[0]}:{client_address[1]}", flush=True)


                num_images_bytes = client_socket.recv(4)

                num_images = bytes_to_int(num_images_bytes)

                print(f"Rank {rank}: Received {num_images} images.", flush=True)


                operation = client_socket.recv(1024).decode("latin-1")

                print(f"Rank {rank}: Received operation: {operation}", flush=True)

                all_processed_images = []

                for _ in range(num_images):


                    image_size_bytes = client_socket.recv(4)

                    image_size = bytes_to_int(image_size_bytes)


                    image_data = b""

                    while len(image_data) < image_size:
                        data_chunk = client_socket.recv(4096)

                        image_data += data_chunk

                    print(f"Rank {rank}: Received image data of size {len(image_data)}", flush=True)


                    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)


                    image_parts = split_image(image, size)


                    for i in range(1, size):
                        comm.send((image_parts[i], operation), dest=i)


                    processed_part = process_image(image_parts[0], operation)

                    processed_image_parts = [processed_part]


                    for i in range(1, size):
                        worker_processed_part = comm.recv(source=i)

                        processed_image_parts.append(worker_processed_part)


                    processed_image = merge_images(processed_image_parts)


                    _, processed_image_data = cv2.imencode('.jpg', processed_image)

                    all_processed_images.append(processed_image_data.tobytes())


                    processed_image_size = len(processed_image_data)

                    client_socket.sendall(int_to_bytes(processed_image_size))

                    print(f"Rank {rank}: Sent processed image size: {processed_image_size}", flush=True)


                    client_socket.sendall(processed_image_data.tobytes())

                    print(f"Rank {rank}: Sent processed image data", flush=True)


                client_socket.close()


                for idx, processed_image_data in enumerate(all_processed_images):

                    nparr = np.frombuffer(processed_image_data, np.uint8)

                    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            server_socket.close()


        else:

            while True:

                image_data_chunk, operation = comm.recv(source=0)

                print(f"Rank {rank} (IP: {get_ip_address()}): Received image data chunk", flush=True)

                processed_image_data = process_image(image_data_chunk, operation)

                print(f"Rank {rank} (IP: {get_ip_address()}): Processed image data chunk", flush=True)

                comm.send(processed_image_data, dest=0)

                print(f"Rank {rank} (IP: {get_ip_address()}): Sent processed image data", flush=True)

    except Exception as e:

        print(f"Server error: {e}", flush=True)

    finally:

        if rank == 0:
            # Close the server socket

            server_socket.close()


if __name__ == "__main__":
    server_ip = '172.31.38.188'

    server_port = 12345

    start_server(server_ip,server_port)