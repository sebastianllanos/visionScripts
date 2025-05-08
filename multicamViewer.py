import depthai as dai
import cv2

"""
Purpose: View camera feed of multiple cameras simultaneously
How to us: Simply plug in all cameras and run script
Expected Result: One cv2 window will appear for each camera plugged in. Alt-tab to switch between the windows.
"""

def createPipeline():
    try:
        pipeline = dai.Pipeline()
        # camRgb = pipeline.create(dai.node.ColorCamera)
        camRgb = pipeline.createColorCamera()
        camRgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
        camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K) 

        camRgb.setNumFramesPool(2, 2, 1, 1, 1)
        # camRgb.initialControl.setManualFocus(134) old setting
        # camRgb.initialControl.setManualExposure(29994, 554) old setting
        camRgb.initialControl.setManualFocus(255) # 255 -> Closer
        #camRgb.initialControl.setManualExposure(35000, 800)
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


device_infos = []
global rgbQs0
global rgbQs1
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
        usbSpeed = dai.UsbSpeed.SUPER = dai.UsbSpeed.SUPER
        openvino_version = dai.OpenVINO.Version.VERSION_2021_4
        devices.append(dai.Device(openvino_version, dai.DeviceInfo(dev_info), usbSpeed))
        

    for count, dev_info in enumerate(device_infos):
        devices[count].startPipeline(pipelines[count])
        rgbQs.append(devices[count].getOutputQueue(name="rgb", maxSize=1, blocking=False))

        cv2.namedWindow(f"video{str(dev_info)}", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(f"video{str(dev_info)}",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN) 
    while True:
        key = cv2.waitKey(1)
        
        for count, dev_info in enumerate(device_infos):
            full = rgbQs[count].get().getCvFrame()
            cv2.imshow(f"video{str(dev_info)}", full)
            
