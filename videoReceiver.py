#!/usr/bin/env python

import os
import json
import types
import datetime
import subprocess

from pellets.DurableMessenger import *

class VideoListener(DurableMessenger):
    def __init__(self):
        super(VideoListener, self).__init__()
        self.config_dict = self.load_config()
        self.avail_videos = self.find_videos()
        self.proc = False

    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as fp:
                config_dict = json.load(fp)
        return config_dict

    def find_videos(self):
        avail_videos = {}
        for v in self.config_dict['videos']:
            avail_videos[v] = self.config_dict['videos'][v]
            avail_videos[v]['path'] = os.path.join(self.config_dict['config']['video_path'], avail_videos[v]['path'])
        return avail_videos

    def launch_video(self, video):
        # cmd = 'omxplayer --aspect-mode fill --font-size 0'
        cmd = 'vlc'
        vid_path = self.avail_videos[video]['path']
        loop = self.avail_videos[video]['loop'] 
        audio = self.avail_videos[video]['audio']

        if loop:
            loop = '--loop'
        else:
            loop = ''
        if not audio:
            audio = '--vol -15000'
        else:
            audio = ''

        # self.proc = subprocess.Popen([cmd, loop, audio, vid_path, '&'], shell=False, stdout=subprocess.PIPE)
        self.proc = subprocess.Popen([cmd, vid_path, '&'], shell=False, stdout=subprocess.PIPE)        
 
    def kill_video(self):
        try:
            self.proc.terminate()
            self.proc = False
        except:
            print('failed to kill process')            

    def callback(self, ch, method, properties, body):
        try:
            body_dict = json.loads(body)
            print(' [x] Received a JSON at {} \n{}'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), body_dict))
        except:
            print(' [x] Received a string at {}\n {}'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), body))

        if 'command' in body_dict: # and 'video' in body_dict:
            cmd = body_dict['command']
            if cmd == 'play':
                video = body_dict['video']
                if isinstance(video, types.ListType):
                    video = video[0]
                if video in self.avail_videos:
                    self.launch_video(video)
            if cmd == 'kill':
                self.kill_video()

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def listen(self, chan_name):
        self.conn = self.get_conn()
        chan = self.make_channel(self.conn, chan_name)
        chan.basic_qos(prefetch_count=1)
        chan.basic_consume(self.callback, queue=chan_name)
        print(' [*] Waiting for video messages, CTRL+C to exit')
        chan.start_consuming()

if __name__ == '__main__':
    my_msgr = VideoListener()
    my_msgr.listen('video_messenger')


"""
example command dict:
{'command': 'play', 'video', 'eyes'}
{'command': 'kill'}
"""
