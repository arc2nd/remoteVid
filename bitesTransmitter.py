import os
import sys
import json
import commands

from bites.BaseMessenger import *

def parse_args(all_args):
    parser = OptionParser(version = '%prog 1.0')
    parser.add_option('-c', '--cmd', action='store', dest='cmd', help='enter command: play/kill/refresh')
    parser.add_option('-v', '--vid', action='store', dest='vid', help='video to play')

    options, args = parser.parse_args(all_args)
    return options, args



def msg(cmd, *args):
    print('Msg: {}'.format(cmd))
    # Compose Message
    if cmd == 'play':
        msg_dict = {'command': cmd, 'video': args[0]}
    else:
        msg_dict = {'command': cmd}
    msg_str = json.dumps(msg_dict, sort_keys=True) # , indent=4)

    # Create Messenger Object
    my_msgr = BaseMessenger()
    my_conn = my_msgr.get_conn('192.168.1.3')
    my_msgr.talk(client=my_conn, topic='video_messenger', msg=msg_str)

if __name__ == '__main__':
    options, args = parse_args(sys.argv[1:])
    if options.cmd == 'play':
        if options.vid:
            msg(options.cmd, options.vid)
    if options.cmd == 'kill':
        msg('kill')
    if options.cmd == 'refresh':
        msg('refresh')
