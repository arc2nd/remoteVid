#!/usr/bin/env python

import os
import json
import types
import signal
import psutil
import commands
import datetime
import subprocess

from bites.BaseMessenger import *

def parse_args(all_args):
    parser = OptionParser(version = '%prog 1.0')
    parser.add_option('-l', '--listen', action='store_true', help='enter listen mode')
    parser.add_option('-t', '--talk', action='store', dest='msg', help='message to send')

    options, args = parser.parse_args(all_args)
    return options, args


class VideoListener(BaseMessenger):
    def __init__(self, path):
        super(VideoListener, self).__init__(path)
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
            tmp_path = os.path.join(self.config_dict['config']['video_path'], avail_videos[v]['path'])
            avail_videos[v]['path'] = tmp_path
        print(avail_videos)
        return avail_videos

    def launch_video(self, video):
        cmd = 'omxplayer' # --aspect-mode fill --font-size 0'
        # cmd = 'vlc'
        vid_path = self.avail_videos[video]['path']
        loop = self.avail_videos[video]['loop'] 
        audio = self.avail_videos[video]['audio']

        if loop:
            loop = '--loop'
        else:
            loop = ''
        if not audio:
            audio = '-15000'
        else:
            audio = '0'

        print('{} {}'.format(cmd, vid_path))
        self.proc = subprocess.Popen([cmd, '--aspect-mode', 'fill', '--font-size', '0', loop, '--vol', audio, vid_path], 
                shell=False, preexec_fn=os.setsid, stdout=subprocess.PIPE)
        # status, output = commands.getstatusoutput('{} {} {}'.format(cmd, audio, vid_path))
        print('{} {}'.format(cmd, vid_path))
        print(self.proc.pid)
        # self.proc = subprocess.Popen([cmd, vid_path, '&'], shell=False, stdout=subprocess.PIPE)        
 
    def kill_video(self):
        try:
            for child in psutil.Process(self.proc.pid).children(recursive=True):
                child.kill()
            self.proc.terminate()
            self.proc.kill()
            self.proc = False
        except:
            os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
            print('failed to kill process')            

    def on_message(self, client, userdata, msg):
        # print(' [x] Received: {}'.format(msg.payload.decode('utf-8')))
        try:
            body_dict = json.loads(msg.payload.decode('utf-8'))
            print(' [x] Received a JSON at {} \n{}'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), body_dict))
        except:
            print(' [x] Received a string at {}\n {}'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), body))

        if 'command' in body_dict: # and 'video' in body_dict:
            cmd = body_dict['command']
            print('command: {}'.format(cmd))
            if cmd.lower() == 'play':
                video = body_dict['video']
                print('\tvid: {}'.format(video))
                print('\tpath: {}'.format(self.avail_videos[video]['path']))
                print(os.path.exists(self.avail_videos[video]['path']))
                if isinstance(video, types.ListType):
                    video = video[0]
                if video in self.avail_videos:
                    print('video: {}'.format(video))
                    self.launch_video(video)
                    print('video: {}'.format(video))
                else:
                    print('video not found')
            if cmd == 'kill':
                self.kill_video()
            if cmd == 'refresh':
                self.config_dict = self.load_config()
                self.avail_videos = self.find_videos()


    def listen(self, client, topic):
        while self.connected != True:    #Wait for connection
            time.sleep(0.1)
        client.subscribe(topic)
        client.loop_start()
        time.sleep(0.1)
        print(' [*] Waiting for messages, CTRL+C to exit')
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print "exiting"
            client.disconnect()
            client.loop_stop()




if __name__ == '__main__':
    options, args = parse_args(sys.argv[1:])
    my_msgr = VideoListener('/home/pi/scripts/bites/envs.crypt')
    my_conn = my_msgr.get_conn(my_msgr.creds['SERVER'])
    if options.listen:
        my_msgr.listen(my_conn, 'video_messenger')
    else:
        my_msgr.talk(client=my_conn, topic='video_messenger', msg=options.msg)



"""
example command dict:
{'command': 'play', 'video', 'eyes'}
{'command': 'kill'}
"""
