# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
from __future__ import division, with_statement

import os
from os.path import exists

import fractions
import subprocess
import tempfile
import time
import math
from glob import glob

import numpy as np
import Image
import ox
import ox.image
from ox.utils import json

img_extension='jpg'

AVCONV = 'avconv'
#wafaa
convert = 'convert'

MAX_DISTANCE = math.sqrt(3 * pow(255, 2))


class AspectRatio(fractions.Fraction):

    def __new__(cls, numerator, denominator=None):
        if not denominator:
            ratio = map(int, numerator.split(':'))
            if len(ratio) == 1:
                ratio.append(1)
            numerator = ratio[0]
            denominator = ratio[1]
            #if its close enough to the common aspect ratios rather use that
            if abs(numerator/denominator - 4/3) < 0.03:
                numerator = 4
                denominator = 3
            elif abs(numerator/denominator - 16/9) < 0.02:
                numerator = 16
                denominator = 9
        return super(AspectRatio, cls).__new__(cls, numerator, denominator)

    @property
    def ratio(self):
        return "%d:%d" % (self.numerator, self.denominator)

def supported_formats():
    p = subprocess.Popen(['which', AVCONV],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if not stdout.strip():
        return None
    p = subprocess.Popen([AVCONV, '-codecs'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return {
        'ogg': 'libtheora' in stdout and 'libvorbis' in stdout,
        'webm': 'libvpx' in stdout and 'libvorbis' in stdout,
        'mp4': 'libx264' in stdout and 'libvo_aacenc' in stdout,
    }

def stream(video, target, profile, info, avconv=None):
    if not os.path.exists(target):
        ox.makedirs(os.path.dirname(target))

    '''
        WebM look into
            lag
            mb_static_threshold
            qmax/qmin
            rc_buf_aggressivity=0.95
            token_partitions=4
            level / speedlevel
            bt?
        H264, should bitrates be a bit lower? other stuff possible?
    '''
    profile, format = profile.split('.')
    bpp = 0.17

    if profile == '1080p':
        height = 1080

        audiorate = 48000
        audioquality = 6
        audiobitrate = None
        audiochannels = None
    if profile == '720p':
        height = 720

        audiorate = 48000
        audioquality = 5
        audiobitrate = None
        audiochannels = None
    if profile == '480p':
        height = 480

        audiorate = 44100
        audioquality = 3
        audiobitrate = None
        audiochannels = 2
    elif profile == '432p':
        height = 432
        audiorate = 44100
        audioquality = 3
        audiobitrate = None
        audiochannels = 2
    elif profile == '360p':
        height = 360

        audiorate = 44100
        audioquality = 1
        audiobitrate = None
        audiochannels = 1
    elif profile == '288p':
        height = 288

        audiorate = 44100
        audioquality = 0
        audiobitrate = None
        audiochannels = 1
    elif profile == '240p':
        height = 240

        audiorate = 44100
        audioquality = 0
        audiobitrate = None
        audiochannels = 1
    elif profile == '144p':
        height = 144

        audiorate = 22050
        audioquality = -1
        audiobitrate = '22k'
        audiochannels = 1
    else:
        height = 96

        audiorate = 22050
        audioquality = -1
        audiobitrate = '22k'
        audiochannels = 1

    #wafaa
    x = 'x'
    res_val = x + str(height)
    cmd = [convert, video, '-resize', res_val, target]    
    #cmd = [convert, video, target]    
    '''
    if not avconv:
        avconv = AVCONV
    cmd = [avconv, '-y', '-i', video, '-threads', '4'] \
          + audio_settings \
          + video_settings

    if format == 'webm':
        cmd += ['-f', 'webm', target]
    elif format == 'mp4':
        #mp4 needs postprocessing(qt-faststart), write to temp file
        cmd += ["%s.mp4" % target]
    else:
        cmd += [target]
    '''
    #print cmd
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()

    if p.returncode != 0:
        t = "%s.mp4" % target if format == 'mp4' else target
        if os.path.exists(t):
            os.unlink(t)
        return False, stdout
    if format == 'mp4':
        cmd = ['qt-faststart', "%s.mp4" % target, target]
        #print cmd
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                  stdout=open('/dev/null', 'w'),
                                  stderr=subprocess.STDOUT)
        p.communicate()
        os.unlink("%s.mp4" % target)
    return True, None


def run_command(cmd, timeout=10):
    #print cmd
    p = subprocess.Popen(cmd, stdout=open('/dev/null', 'w'),
                              stderr=subprocess.STDOUT)
    while timeout > 0:
        time.sleep(0.2)
        timeout -= 0.2
        if p.poll() != None:
            return p.returncode
    if p.poll() == None:
        os.kill(p.pid, 9)
        killedpid, stat = os.waitpid(p.pid, os.WNOHANG)
    return p.returncode


def frame(video, frame, position, height=128, redo=False):
    '''
        params:
            video     input
            frame     output
            position as float in seconds
            height of frame
            redo boolean to extract file even if it exists
    '''
    if exists(video):
        folder = os.path.dirname(frame)
        if redo or not exists(frame):
            ox.makedirs(folder)
            #wafaa commented
            '''if video.endswith('.mp4'):
                cmd = [
                    AVCONV, '-y',
                    '-ss', str(position),
                    '-i', video,
                    '-an', '-vframes', '1',
                    '-vf', 'scale=-1:%s' % height
                ]
                if not frame.endswith('.png'):
                    cmd += ['-f', 'mjpeg']
                cmd += [frame]
            else:
                cmd = ['oxframe', '-i', video, '-o', frame,
                    '-p', str(position), '-y', str(height)]
			'''
            #wafaa
            if video.endswith('.png'):
                #wafaa
                #x = 'x'
                #frame_height = x + str(height)
                cmd = [convert, video, '-thumbnail', 'x128', frame]
            run_command(cmd)


def resize_image(image_source, image_output, width=None, size=None):
    if exists(image_source):
        source = Image.open(image_source).convert('RGB')
        source_width = source.size[0]
        source_height = source.size[1]
        if size:
            if source_width > source_height:
                width = size
                height = int(width / (float(source_width) / source_height))
                height = height - height % 2
            else:
                height = size
                width = int(height * (float(source_width) / source_height))
                width = width - width % 2

        else:
            height = int(width / (float(source_width) / source_height))
            height = height - height % 2

        width = max(width, 1)
        height = max(height, 1)

        if width < source_width:
            resize_method = Image.ANTIALIAS
        else:
            resize_method = Image.BICUBIC
        output = source.resize((width, height), resize_method)
        output.save(image_output)


def timeline(video, prefix, modes=None, size=None):
    if modes is None:
        modes = ['antialias', 'slitscan', 'keyframes', 'audio', 'data']
    if size is None:
        size=[64, 16]
    if isinstance(video, basestring):
        video = [video]
    cmd = ['../bin/oxtimelines',
        '-s', ','.join(map(str, reversed(sorted(size)))),
        '-m', ','.join(modes),
        '-o', prefix,
        '-c', os.path.join(prefix, 'cuts.json'),
    ] + video
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #print cmd
    #p = subprocess.Popen(cmd)
    p.wait()


def average_color(prefix, start=0, end=0, mode='antialias'):
    height = 64
    frames = 0
    pixels = []
    color = np.asarray([0, 0, 0], dtype=np.float32)

    if end:
        start = int(start * 25)
        end = int(end * 25)
    mode = 'timeline' + mode
    timelines = ox.sorted_strings(filter(lambda t: t!= '%s%s%sp.jpg'%(prefix, mode, height),
                              glob("%s%s%sp*.jpg"%(prefix, mode, height))))
    for image in timelines:
        start_offset = 0
        if start and frames + 1500 <= start:
            frames += 1500
            continue
        timeline = Image.open(image)
        frames += timeline.size[0]
        if start and frames > start > frames-timeline.size[0]:
            start_offset = start - (frames-timeline.size[0])
            box = (start_offset, 0, timeline.size[0], height)
            timeline = timeline.crop(box)
        if end and frames > end:
            end_offset = timeline.size[0] - (frames - end)
            box = (0, 0, end_offset, height)
            timeline = timeline.crop(box)
        
        p = np.asarray(timeline.convert('RGB'), dtype=np.float32)
        p = np.sum(p, axis=0) / height               #average color per frame
        pixels.append(p)
        if end and frames >= end:
            break

    if end:
        frames = end - start
    if frames:
        for i in range(0, len(pixels)):
            p = np.sum(pixels[i], axis=0) / frames
            color += p
    color = list(map(float, color))
    return ox.image.getHSL(color)


def average_volume(prefix, start=0, end=0):
    return average_color(prefix, start, end, 'audio')[2]


def get_distance(rgb0, rgb1):
    # rgb distance, normalized so that black/white equals 1
    dst = math.sqrt(pow(rgb0[0] - rgb1[0], 2) + pow(rgb0[1] - rgb1[1], 2) + pow(rgb0[2] - rgb1[2], 2))
    return dst / MAX_DISTANCE


def cuts(prefix):
    fname = os.path.join(prefix, 'cuts.json')
    if not os.path.exists(fname):
        return []
    with open(fname) as f:
        cuts = json.load(f)
    return cuts


def divide(num, by):
    # >>> divide(100, 3)
    # [33, 33, 34]
    arr = []
    div = int(num / by)
    mod = num % by
    for i in range(int(by)):
        arr.append(div + (i > by - 1 - mod))
    return arr


def timeline_strip(item, cuts, info, prefix):
    _debug = False
    duration = info['duration']
    video_height = info['video'][0]['height']
    video_width = info['video'][0]['width']
    video_ratio = video_width / video_height

    line_image = []
    timeline_height = 64
    timeline_width = 1500
    fps = 25
    frames = int(duration * fps)
    if cuts[0] != 0:
        cuts.insert(0, 0)

    cuts = map(lambda x: int(round(x * fps)), cuts)

    for frame in range(frames):
        i = int(frame / timeline_width)
        x = frame % timeline_width
        if x == 0:
            timeline_width = min(timeline_width, frames - frame)
            timeline_image = Image.new('RGB', (timeline_width, timeline_height))
        if frame in cuts:
            c = cuts.index(frame)
            if c +1 < len(cuts):
                duration = cuts[c + 1] - cuts[c]
                frames = math.ceil(duration / (video_width * timeline_height / video_height))
                widths = divide(duration, frames)
                frame = frame
                if _debug:
                    print widths, duration, frames, cuts[c], cuts[c + 1]
                for s in range(int(frames)):
                    frame_ratio = widths[s] / timeline_height
                    if video_ratio > frame_ratio:
                        width = int(round(video_height * frame_ratio))
                        left = int((video_width - width) / 2)
                        box = (left, 0, left + width, video_height)
                    else:
                        height = int(round(video_width / frame_ratio))
                        top = int((video_height - height) / 2)
                        box = (0, top, video_width, top + height)
                    if _debug:
                        print frame, 'cut', c, 'frame', s, frame, 'width', widths[s], box
                    #FIXME: why does this have to be frame+1?
                    frame_image = Image.open(item.frame((frame+1)/fps))
                    frame_image = frame_image.crop(box).resize((widths[s], timeline_height), Image.ANTIALIAS)
                    for x_ in range(widths[s]):
                        line_image.append(frame_image.crop((x_, 0, x_ + 1, timeline_height)))
                    frame += widths[s]
        if len(line_image) > frame:
            timeline_image.paste(line_image[frame], (x, 0))
        if x == timeline_width - 1:
            timeline_file = '%sStrip64p%04d.png' % (prefix, i)
            if _debug:
                print 'writing', timeline_file
            timeline_image.save(timeline_file)


def chop(video, start, end):
    t = end - start
    tmp = tempfile.mkdtemp()
    ext = os.path.splitext(video)[1]
    choped_video = '%s/tmp%s' % (tmp, ext)
    cmd = [
        'ffmpeg',
        '-y',
        '-i', video,
        '-ss', '%.3f'%start,
        '-t', '%.3f'%t,
        '-vcodec', 'copy',
        '-acodec', 'copy',
        '-f', ext[1:],
        choped_video
    ]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                              stdout=open('/dev/null', 'w'),
                              stderr=open('/dev/null', 'w'))
    p.wait()
    f = open(choped_video, 'r')
    os.unlink(choped_video)
    os.rmdir(tmp)
    return f
