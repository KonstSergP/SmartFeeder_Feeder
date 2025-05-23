# Copyright (c) 2021, Raspberry Pi
# This file is part of picamera2, licensed under the BSD 2-Clause License.
# Modified Petrov Konstantin in 2025 (function start)
# See the camera/picamera2_fix/LICENSE file for details.


import gc
import signal
import subprocess
import time
from ..camera import log

import prctl
from picamera2.outputs import Output



class CaptureAndStreamOutput(Output):
    """
    Copy of FfmpegOutput with small change to disable ffmpeg exit when thread in which popen was called dies
    """

    def __init__(self, output_filename, audio=False, audio_device="default", audio_sync=-0.3,
                 audio_samplerate=48000, audio_codec="aac", audio_bitrate=128000, audio_filter=None, pts=None):
        super().__init__(pts=pts)
        self.ffmpeg = None
        self.output_filename = output_filename
        self.audio = audio
        self.audio_device = audio_device
        self.audio_filter = audio_filter
        self.audio_sync = audio_sync
        self.audio_samplerate = audio_samplerate
        self.audio_codec = audio_codec
        self.audio_bitrate = audio_bitrate
        # If we run an audio stream, FFmpeg won't stop so we'll give the video stream a
        # moment or two to flush stuff out, and then we'll have to terminate the process.
        self.timeout = 1 if audio else None
        # A user can set this to get notifications of FFmpeg failures.
        self.error_callback = None
        # We don't understand timestamps, so an encoder may have to pace output to us.
        self.needs_pacing = True

    def start(self):
        general_options = ['-loglevel', 'warning',
                           '-y']  # -y means overwrite output without asking
        # We have to get FFmpeg to timestamp the video frames as it gets them. This isn't
        # ideal because we're likely to pick up some jitter, but works passably, and I
        # don't have a better alternative right now.
        video_input = ['-use_wallclock_as_timestamps', '1',
                       '-thread_queue_size', '64',  # necessary to prevent warnings
                       '-i', '-']
        video_codec = ['-c:v', 'copy']
        audio_input = []
        audio_codec = []
        if self.audio:
            audio_input = ['-itsoffset', str(self.audio_sync),
                           '-f', 'pulse',
                           '-sample_rate', str(self.audio_samplerate),
                           '-thread_queue_size', '1024',  # necessary to prevent warnings
                           '-i', self.audio_device]
            audio_codec = ['-b:a', str(self.audio_bitrate),
                           '-c:a', self.audio_codec]
            if self.audio_filter:  # Check if audio_filter is not empty or None
                audio_codec.extend(['-af', self.audio_filter])

        command = ['ffmpeg'] + general_options + audio_input + video_input + \
            audio_codec + video_codec + self.output_filename.split()
        
        self.ffmpeg = subprocess.Popen(command, stdin=subprocess.PIPE)
        #self.ffmpeg = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #log.error(self.ffmpeg.communicate())
        # With this, ffmpeg will die when the thread in which it was created dies
        #self.ffmpeg = subprocess.Popen(command, stdin=subprocess.PIPE, preexec_fn=lambda: prctl.set_pdeathsig(signal.SIGKILL))

        super().start()

    def stop(self):
        super().stop()
        if self.ffmpeg is not None:
            self.ffmpeg.stdin.close()  # FFmpeg needs this to shut down tidily
            try:
                # Give it a moment to flush out video frames, but after that make sure we terminate it.
                self.ffmpeg.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                # We'll always end up here when there was an audio strema. Ignore any further errors.
                try:
                    self.ffmpeg.terminate()
                except Exception:
                    pass
            self.ffmpeg = None
            # This seems to be necessary to get the subprocess to clean up fully.
            gc.collect()

    def outputframe(self, frame, keyframe=True, timestamp=None, packet=None, audio=False):
        if audio:
            raise RuntimeError("FfmpegOutput does not support audio packets from Picamera2")
        if self.recording and self.ffmpeg:
            # Handle the case where the FFmpeg prcoess has gone away for reasons of its own.
            try:
                self.ffmpeg.stdin.write(frame)
                self.ffmpeg.stdin.flush()  # forces every frame to get timestamped individually
            except Exception as e:  # presumably a BrokenPipeError? should we check explicitly?
                self.ffmpeg = None
                if self.error_callback:
                    self.error_callback(e)
            else:
                self.outputtimestamp(timestamp)
