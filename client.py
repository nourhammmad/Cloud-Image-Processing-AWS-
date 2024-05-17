import socket
import cv2
import numpy as np
import matplotlib.pyplot as plt

from tkinter import Tk, Label, Button, Listbox, filedialog, StringVar, OptionMenu, messagebox
from tkinter.font import Font


def int_to_bytes(n):
    return n.to_bytes(4, byteorder='big')


def bytes_to_int(b):
    return int.from_bytes(b, byteorder='big')


def preprocess_image(image_path, target_size=(300, 300)):
    try:
        # Load the image from file
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Failed to load image. Check the file format and path.")

        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()

        # Resize the image
        resized_image = cv2.resize(image, target_size)

        # Convert the resized image to bytes
        _, image_data = cv2.imencode('.jpg', resized_image)
        image_data = image_data.tobytes()

        return image_data

    except Exception as e:
        messagebox.showerror("Preprocessing Error", f"Error preprocessing image: {e}")
        return None


def send_images(server_ip, server_port, image_paths, operation):
    try:
        # Create a client socket and connect to the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, server_port))

            # Send the number of images to the server
            num_images = len(image_paths)
            client_socket.sendall(int_to_bytes(num_images))

            # Send the operation to the server
            client_socket.sendall(operation.encode("latin-1"))

            for image_path in image_paths:
                # Preprocess the image
                image_data = preprocess_image(image_path)
                if image_data is not None:
                    # Send the image data size to the server
                    image_size = len(image_data)
                    client_socket.sendall(int_to_bytes(image_size))

                    # Send the image data to the server
                    client_socket.sendall(image_data)

            for _ in range(num_images):
                # Receive the size of the processed image data from the server
                processed_image_size_bytes = client_socket.recv(4)
                processed_image_size = bytes_to_int(processed_image_size_bytes)

                # Receive the processed image data from the server
                processed_image_data = b""
                while len(processed_image_data) < processed_image_size:
                    data_chunk = client_socket.recv(4096)
                    processed_image_data += data_chunk

                # Convert the processed image data to OpenCV format
                processed_image = cv2.imdecode(np.frombuffer(processed_image_data, np.uint8), cv2.IMREAD_COLOR)

                # Display the processed image
                plt.imshow(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
                plt.axis('off')
                plt.show()

    except Exception as e:
        messagebox.showerror("Client Error", f"An error occurred: {e}")


def select_images():
    filepaths = filedialog.askopenfilenames(filetypes=[("Image files", ".png;.jpg;*.jpeg")])
    if filepaths:
        for filepath in filepaths:
            image_listbox.insert('end', filepath)


def process_images():
    image_paths = list(image_listbox.get(0, 'end'))
    if not image_paths:
        messagebox.showerror("Input Error", "No images selected.")
        return

    operation = operation_var.get()
    if not operation:
        messagebox.showerror("Input Error", "No operation selected.")
        return

    send_images(server_ip, server_port, image_paths, operation)


def on_enter(event, button):
    button.config(bg='lightblue')


def on_leave(event, button):
    button.config(bg='blue')


# Create the Tkinter GUI
root = Tk()
root.title("Image Processing Client")

# Define a custom font
custom_font = Font(family="Helvetica", size=12, weight="bold")

Label(root, text="Select Images:").grid(row=0, column=0, padx=10, pady=10)
image_listbox = Listbox(root, width=50, height=10)
image_listbox.grid(row=1, column=0, padx=10, pady=10)

browse_button = Button(root, text="Browse", command=select_images, bg='blue', fg='white', font=custom_font, padx=10,
                       pady=5, relief='raised', bd=5)
browse_button.grid(row=1, column=1, padx=10, pady=10)

browse_button.bind("<Enter>", lambda event: on_enter(event, browse_button))
browse_button.bind("<Leave>", lambda event: on_leave(event, browse_button))

Label(root, text="Select Operation:").grid(row=2, column=0, padx=10, pady=10)
operation_var = StringVar()
operation_var.set("edge_detection")
operations = ["edge_detection", "color_inversion", "resize", "blur", "erosion", "dilation"]
operation_menu = OptionMenu(root, operation_var, *operations)
operation_menu.grid(row=3, column=0, padx=10, pady=10)

process_button = Button(root, text="Process Images", command=process_images, bg='green', fg='white', font=custom_font,
                        padx=10, pady=5, relief='raised', bd=5)
process_button.grid(row=4, column=0, padx=10, pady=10)

process_button.bind("<Enter>", lambda event: on_enter(event, process_button))
process_button.bind("<Leave>", lambda event: on_leave(event, process_button))

server_ip = '16.171.20.104'
server_port = 12345

root.mainloop()