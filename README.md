# 🖐️ Advanced Gesture-Controlled Image Viewer

An advanced computer vision application that allows users to manipulate an image in a 2D augmented reality space using only hand gestures. This project leverages the MediaPipe library for high-fidelity hand tracking to create a fluid, intuitive, and hands-free user experience.

This application goes beyond simple commands, enabling complex interactions like panning, zooming, and rotating, all controlled by the position and orientation of the user's hands in real-time.

![Demo GIF](https://user-images.githubusercontent.com/.../demo.gif)

*(This is a placeholder. It is highly recommended to create a GIF of the application in action using a tool like [ScreenToGif](https://www.screentogif.com/) and upload it here. A visual demo is the most powerful way to showcase this project.)*

---

## ✨ Features

-   **Multi-Gesture Control:**
    -   **Pan (Move):** Use a single open palm to "grab" the image and move it around the screen.
    -   **Zoom:** Use a "pinch" gesture with your thumb and index finger. Moving them apart zooms in; bringing them together zooms out.
    -   **Rotate:** Use two hands. The application tracks the angle between your palms to rotate the image.
-   **High-Fidelity Hand Tracking:** Powered by **Google's MediaPipe**, providing real-time, accurate tracking of 21 keypoints on each hand.
-   **Fluid Interaction:** Implements motion smoothing (interpolation) to eliminate jitter and create a smooth, professional feel for all transformations.
-   **Real-time AR-like Experience:** Overlays the manipulated image in a dedicated window, creating a compelling demonstration of human-computer interaction.

---

## 🛠️ Technology Stack

-   **Python**
-   **OpenCV:** For webcam capture, image processing, and rendering the final transformed image.
-   **MediaPipe:** For robust, high-performance hand and landmark detection.
-   **NumPy:** For performing the mathematical transformations (rotation, scaling, translation).
-   **Pygame:** Used for creating the display window and handling the event loop.

---

## 🚀 Getting Started

Follow these instructions to get the project running on your local machine.

### Prerequisites

-   Python 3.9+
-   A webcam connected to your computer.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Zaid2044/Advanced-Gesture-Image-Viewer.git
    cd Advanced-Gesture-Image-Viewer
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install opencv-python mediapipe numpy pygame
    ```

4.  **Add an Image:**
    -   Place an image file (e.g., `test_image.jpg`) inside the `images/` folder.
    -   Ensure the filename in `src/main.py` matches the name of your image file.

---

## ⚡ Usage

To run the application, execute the `main.py` script from the project root:

```bash
python src/main.py
```
-   Two windows will appear: one showing your webcam feed with hand tracking overlays, and another showing the image you are controlling.
-   Use the gestures described above to interact with the image.
-   Press 'q' or the Esc key on the active window to quit the application.