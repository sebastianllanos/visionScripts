import depthai as dai
import cv2
import os
from datetime import datetime

def createPipeline():
    try:
        pipeline = dai.Pipeline()
        camRgb = pipeline.createColorCamera()
        camRgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
        camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K) 
        camRgb.setNumFramesPool(2, 2, 1, 1, 1)
        camRgb.initialControl.setManualFocus(255)

        xoutRgb = pipeline.create(dai.node.XLinkOut)
        xoutRgb.setStreamName("rgb")
        camRgb.video.link(xoutRgb.input)

        xin = pipeline.create(dai.node.XLinkIn)
        xin.setStreamName("control")
        xin.out.link(camRgb.inputControl)

        xoutStill = pipeline.create(dai.node.XLinkOut)
        xoutStill.setStreamName("still")
        camRgb.still.link(xoutStill.input)

        return pipeline
    except Exception as e:
        print(f"Error creating pipeline: {e}")

def save_frames(frames_dict):
    os.makedirs("images", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for mxid, frame in frames_dict.items():
        filename = os.path.join("images", f"{mxid}_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Saved frame from {mxid} as {filename}")

device_infos = []
rgbQs = []
pipelines = []
devices = []

if __name__ == "__main__":
    for device in dai.Device.getAllAvailableDevices():
        print(f"{device.getMxId()} {device.state}")
        device_infos.append(device.getMxId())

    for dev_info in device_infos:
        pipelines.append(createPipeline())

    for count, dev_info in enumerate(device_infos):
        usbSpeed = dai.UsbSpeed.SUPER
        openvino_version = dai.OpenVINO.Version.VERSION_2021_4
        devices.append(dai.Device(openvino_version, dai.DeviceInfo(dev_info), usbSpeed))

    for count, dev_info in enumerate(device_infos):
        devices[count].startPipeline(pipelines[count])
        rgbQs.append(devices[count].getOutputQueue(name="rgb", maxSize=1, blocking=False))
        cv2.namedWindow(f"video{str(dev_info)}", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(f"video{str(dev_info)}", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    latest_frames = {}

    while True:
        key = cv2.waitKey(1) & 0xFF

        for count, dev_info in enumerate(device_infos):
            frame = rgbQs[count].get().getCvFrame()
            latest_frames[dev_info] = frame
            cv2.imshow(f"video{str(dev_info)}", frame)

        if key == ord('s'):
            save_frames(latest_frames)
        elif key == ord('q'):
            break

    cv2.destroyAllWindows()
