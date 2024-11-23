import tkinter as tk
import socket
import struct
import cv2
from PIL import Image, ImageTk
import numpy as np

# Initialize the Tkinter window
root = tk.Tk()
root.title("UDP Video Stream")

# Set up the UDP socket to receive video
UDP_IP = "127.0.0.1"  # Localhost (should match the sender's IP)
UDP_PORT = 5001  # Same port as sender
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# Create a canvas to display the video
canvas = tk.Canvas(root, width=640, height=480)
canvas.pack()

def update_frame():
    try:
        # Receive frame size first (expect 8 bytes for 64-bit size)
        frame_size_data, addr = sock.recvfrom(8)  # Expect 8 bytes
        frame_size = struct.unpack("Q", frame_size_data)[0]  # Unpack as 64-bit unsigned integer
        print(f"Received frame size: {frame_size}")  # Debugging frame size received

        # Validate frame size
        if frame_size > 1000000 or frame_size <= 0:
            print(f"Suspicious frame size: {frame_size}. Skipping frame.")
            raise ValueError("Invalid frame size")

        # Receive all chunks and reassemble the frame
        frame_data = b""
        remaining_size = frame_size
        while remaining_size > 0:
            chunk, addr = sock.recvfrom(min(65507, remaining_size))  # Max UDP packet size
            frame_data += chunk
            remaining_size -= len(chunk)

        print(f"Received complete frame of size: {len(frame_data)}")  # Debugging complete frame

        # Validate received frame data size
        if len(frame_data) != frame_size:
            print(f"Error: Expected frame size {frame_size}, but received {len(frame_data)}. Skipping frame.")
            raise ValueError("Incomplete frame received")

        # Decode the JPEG image to get a frame as an OpenCV image
        nparr = np.frombuffer(frame_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            print("Error: Frame decoding failed. Skipping frame.")
            raise ValueError("Frame decoding failed")

        # Convert the image to a format that Tkinter can display
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  # Convert to RGB
        img_tk = ImageTk.PhotoImage(img_pil)

        # Update the Tkinter canvas with the new frame
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.image = img_tk  # Keep a reference to avoid garbage collection

    except Exception as e:
        # Log the error and skip the frame
        print(f"Error receiving frame: {e}")

    # Schedule the next frame update (always schedule, even on failure)
    root.after(30, update_frame)

# Start the frame update loop
update_frame()

# Start the Tkinter event loop
root.mainloop()
