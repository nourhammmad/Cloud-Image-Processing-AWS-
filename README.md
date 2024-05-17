# Cloud-Image-Processing-AWS-
video link on drive:
https://drive.google.com/drive/folders/13hMaiN1F6_wGcM_2InYShEdxqVWj1Q6n?usp=sharing
The "Parallel Image Processing with MPI" project aims to efficiently process a large number of images using parallel computing techniques with the Message Passing Interface (MPI) standard.

The project involves two main components: a server and multiple client processes. The server distributes image processing tasks to the client processes, which execute the tasks concurrently.

Here's how the project works:

Server Component:

The server is responsible for distributing image processing tasks and managing communication with client processes.
It listens for incoming connections from client processes.
Upon receiving a connection, the server accepts image processing requests along with the desired operation (e.g., edge detection, color inversion).
It divides the images into parts and distributes them among the available client processes for parallel processing.
After processing each image part, the server receives the results from the client processes and merges them into the final processed image.
Additionally, the server sends progress updates to the client processes to track the completion status of image processing tasks.

Client Component:

Client processes connect to the server to request image processing tasks.
Upon receiving a task, each client process performs image processing on the assigned image parts in parallel.
After processing the image parts, each client sends the results back to the server for merging and further processing.
Client processes also receive and display progress updates from the server to inform users about the status of image processing tasks.
The project utilizes the MPI library for communication and coordination between server and client processes, enabling efficient parallelization of image processing tasks across multiple compute nodes or processor cores. This parallel approach significantly reduces the time required to process a large number of images compared to sequential processing.

The project offers benefits such as improved processing speed, scalability to handle large datasets, and efficient resource utilization in distributed computing environments. It can be applied in various domains requiring intensive image processing tasks, including computer vision, medical imaging, satellite image analysis, and more.
