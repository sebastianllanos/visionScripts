import depthai as dai
import cv2
import os
from datetime import datetime

# Create image output folder
output_folder = os.path.join(".", "images", "highRes")
os.makedirs(output_folder, exist_ok=True)

def create_pipeline():
    pipeline = dai.Pipeline()

    # Create camera node
    cam = pipeline.create(dai.node.ColorCamera)
    cam.setBoardSocket(dai.CameraBoardSocket.CAM_A)

    # Set high still resolution (max supported by OAK-1-MAX: 5312x6000)
    cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_5312X6000)
    cam.setStillSize(5312, 6000)

    # Set video resolution to 4K
    cam.setVideoSize(3840, 2160)

    # Limit memory usage
    cam.setNumFramesPool(2, 2, 1, 1, 1)

    # Set manual focus
    cam.initialControl.setManualFocus(255)

    # Set manual exposure time
    # cam.initialControl.setManualExposure(25000,400)

    # Create XLinkOut for video
    xout_video = pipeline.create(dai.node.XLinkOut)
    xout_video.setStreamName("video")
    cam.video.link(xout_video.input)

    # Create XLinkOut for still
    xout_still = pipeline.create(dai.node.XLinkOut)
    xout_still.setStreamName("still")
    cam.still.link(xout_still.input)

    # Create XLinkIn for control
    xin = pipeline.create(dai.node.XLinkIn)
    xin.setStreamName("control")
    xin.out.link(cam.inputControl)

    return pipeline

# Initialize device
with dai.Device(create_pipeline()) as device:
    video_queue = device.getOutputQueue("video", maxSize=1, blocking=False)
    still_queue = device.getOutputQueue("still", maxSize=1, blocking=True)
    control_queue = device.getInputQueue("control")

    print("[INFO] Streaming video... Press 's' to save high-res image. Press 'q' to quit.")

    while True:
        key = cv2.waitKey(1)
        if key == ord('s'):
            print("[INFO] Capturing high-resolution image...")
            ctrl = dai.CameraControl()
            ctrl.setCaptureStill(True)
            control_queue.send(ctrl)

            still_frame = still_queue.get()
            highres = still_frame.getCvFrame()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(output_folder, f"highres_{timestamp}.png")
            cv2.imwrite(filename, highres)
            print(f"[INFO] Saved: {filename}")

        elif key == ord('q'):
            print("[INFO] Exiting...")
            break

        frame = video_queue.get().getCvFrame()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        resized_frame = cv2.resize(frame, (1920, 1080))  # Cambia a la resolución que desees
        cv2.imshow(f"video", resized_frame)

    cv2.destroyAllWindows()
