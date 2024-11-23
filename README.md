# gstreamer_udp_cv2

The code is used to read the gstreamer video frames using cv2. Gstreamer sends the video frames via udp and then this udp is read using gstreamer command and converted to opencv frames. Further these frames are again transmitted via udp do that tkinter GUI can read these frames as gstreamer cant directly run gstreamer commands.(fails to use of threading)


start streaming the camera video using gstreamer command
```
gst-launch-1.0 v4l2src ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay ! udpsink host=127.0.0.1 port=5000
```

Run the code to read these gstreamer frames to opencv and again transmit via udp:
``` python3 receive.py```


Run the tkinter GUI to diplay the frames:
```python3 tkin.py```


## Streaming using shared memory in a same system
sender command
```
gst-launch-1.0 v4l2src ! videoconvert ! video/x-raw,format=RGB,width=640,height=480,framerate=30/1 ! shmsink socket-path=/tmp/gstreamer-shm wait-for-connection=true
```

receiver command:
```
gst-launch-1.0 shmsrc socket-path=/tmp/gstreamer-shm ! video/x-raw,format=RGB,width=640,height=480,framerate=30/1 ! videoconvert ! autovideosink

```
