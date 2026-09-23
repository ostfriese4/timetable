# qr.py
#
# Copyright 2026 Jonas
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import gi

gi.require_version('Gst', '1.0')
gi.require_version('Xdp', '1.0')
gi.require_version('Gio', '2.0')

from gi.repository import Gst
from gi.repository import Gtk
from gi.repository import Xdp

import zxingcpp
from PIL import Image

def getCameraStream(widget):
    portal = Xdp.Portal()

    def finish(portal, task, x):
        ok = portal.access_camera_finish(task)

        if ok:
            print("camera access granted")
            fd = portal.open_pipewire_remote_for_camera()

            print("fd:", fd)

            pipeline, sink, appsink = createStreamFromFd(fd)
            widget.setup(pipeline, sink, appsink)
        else:
            print("camera access denied")

    portal.access_camera(
        parent = None,
        flags = Xdp.CameraFlags.NONE,
        cancellable = None,
        callback = finish,
        data = None
    )

def createStreamFromFd(fd):
    Gst.init(None)

    pipeline = Gst.Pipeline.new("camera-pipeline")

    source = Gst.ElementFactory.make("pipewiresrc", "fd-source")
    source.set_property("fd", fd)

    tee = Gst.ElementFactory.make("tee", "tee")

    sink = Gst.ElementFactory.make("gtk4paintablesink", "sink")

    appsink = Gst.ElementFactory.make("appsink", "appsink")
    appsink.set_property("max-buffers", 1)
    appsink.set_property("drop", True)
    appsink.set_property("sync", False)

    queue_video = Gst.ElementFactory.make("queue", "video-queue")
    queue_scan = Gst.ElementFactory.make("queue", "scan-queue")

    videoconvert = Gst.ElementFactory.make("videoconvert", "scan-convert")

    capsfilter = Gst.ElementFactory.make("capsfilter", "scan-caps")
    capsfilter.set_property(
        "caps",
        Gst.Caps.from_string("video/x-raw,format=GRAY8")
    )

    pipeline.add(source)
    pipeline.add(tee)
    pipeline.add(queue_video)
    pipeline.add(queue_scan)
    pipeline.add(videoconvert)
    pipeline.add(capsfilter)
    pipeline.add(sink)
    pipeline.add(appsink)

    source.link(tee)

    tee_pad_video = tee.get_request_pad("src_%u")
    queue_video_pad = queue_video.get_static_pad("sink")
    tee_pad_video.link(queue_video_pad)

    queue_video.link(sink)

    tee_pad_scan = tee.get_request_pad("src_%u")
    queue_scan_pad = queue_scan.get_static_pad("sink")
    tee_pad_scan.link(queue_scan_pad)

    queue_scan.link(videoconvert)
    videoconvert.link(capsfilter)
    capsfilter.link(appsink)


    return pipeline, sink, appsink


class QrScanner(Gtk.Picture):
    __gtype_name__ = "QrScanner"

    def __init__(self):
        self.sink = None
        self.pipeline = None
        self.latest_pixbuf = None

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.set_size_request(300, 300)
        self.set_content_fit(Gtk.ContentFit.SCALE_DOWN)

    def enable(self, callback):
        self.callback = callback
        if self.sink is None:
            getCameraStream(self)
        else:
            self.pipeline.set_state(Gst.State.PLAYING)

    def scanImage(self, appsink):
        sample = appsink.emit("pull-sample")

        if sample is None:
            return Gst.FlowReturn.OK

        buffer = sample.get_buffer()
        caps = sample.get_caps()
        struct = caps.get_structure(0)

        _, width = struct.get_int("width")
        _, height = struct.get_int("height")

        success, mapinfo = buffer.map(Gst.MapFlags.READ)
        if not success:
            return Gst.FlowReturn.OK

        try:
            image_data = bytes(mapinfo.data)
        finally:
            buffer.unmap(mapinfo)

        image = Image.frombytes(
            "L",
            (width, height),
            image_data
        )

        barcodes = zxingcpp.read_barcodes(
            image,
            formats=zxingcpp.BarcodeFormat.QRCode
        )

        for barcode in barcodes:
            self.callback(barcode.text)

        return Gst.FlowReturn.OK

    def setup(self, pipeline, sink, appsink):
        print("setup")

        self.sink = sink
        self.appsink = appsink
        self.pipeline = pipeline

        self.set_paintable(sink.get_property("paintable"))

        self.appsink.set_property("emit-signals", True)
        self.appsink.connect("new-sample", self.scanImage)

        self.pipeline.set_state(Gst.State.PLAYING)

    def do_unrealize(self):
        if self.get_realized():
            self.disable()
            Gtk.Picture.do_unrealize(self)

    def disable(self):
        self.pipeline.set_state(Gst.State.NULL)
