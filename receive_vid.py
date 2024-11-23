#!/usr/bin/env python

import cv2
import gi
import numpy as np

gi.require_version('Gst', '1.0')
from gi.repository import Gst


class Video():
    """Shared memory video capture class"""

    def __init__(self, socket_path='/tmp/gstreamer-shm'):
        """
        Args:
            socket_path (str): Path to the shared memory socket
        """
        Gst.init(None)

        self.socket_path = socket_path
        self._frame = None

        # Shared memory video source
        self.video_source = f'shmsrc socket-path={self.socket_path} is-live=true'
        # Decode raw video frames from shared memory
        self.video_decode = \
            '! video/x-raw,format=(string)RGB,width=640,height=480,framerate=30/1 ' \
            '! videoconvert ! video/x-raw,format=(string)BGR'
        # Create a sink to get data
        self.video_sink_conf = \
            '! appsink emit-signals=true sync=false max-buffers=2 drop=true'

        self.video_pipe = None
        self.video_sink = None

        self.run()

    def start_gst(self, config=None):
        """Start GStreamer pipeline"""
        if not config:
            config = \
                [
                    self.video_source,
                    self.video_decode,
                    self.video_sink_conf
                ]

        command = ' '.join(config)
        self.video_pipe = Gst.parse_launch(command)
        self.video_pipe.set_state(Gst.State.PLAYING)
        self.video_sink = self.video_pipe.get_by_name('appsink0')

    @staticmethod
    def gst_to_opencv(sample):
        """Transform byte array into OpenCV-compatible numpy array"""
        buf = sample.get_buffer()
        caps = sample.get_caps()
        array = np.ndarray(
            (
                caps.get_structure(0).get_value('height'),
                caps.get_structure(0).get_value('width'),
                3
            ),
            buffer=buf.extract_dup(0, buf.get_size()), dtype=np.uint8)
        return array

    def frame(self):
        """Get the current frame"""
        return self._frame

    def frame_available(self):
        """Check if a frame is available"""
        return type(self._frame) != type(None)

    def run(self):
        """Start the pipeline and connect the callback"""
        self.start_gst()
        self.video_sink = self.video_pipe.get_by_name('appsink0')
        self.video_sink.connect('new-sample', self.callback)

    def callback(self, sink):
        sample = sink.emit('pull-sample')
        new_frame = self.gst_to_opencv(sample)
        self._frame = new_frame
        return Gst.FlowReturn.OK


if __name__ == '__main__':
    # Create the video object
    video = Video()

    while True:
        # Wait for the next frame
        if not video.frame_available():
            continue

        frame = video.frame()
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
