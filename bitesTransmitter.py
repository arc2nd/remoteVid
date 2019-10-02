import os
import json
import commands

from bites.BaseMessenger import *

def msg(cmd, *args):
    print('Msg: {}'.format(cmd))
    # Compose Message
    if cmd == 'play':
        msg_dict = {'command': cmd, 'video': args[0]}
    elif cmd == 'kill':
        msg_dict = {'command': cmd}
    msg_str = json.dumps(msg_dict, sort_keys=True) # , indent=4)

    # Create Messenger Object
    my_msgr = BaseMessenger()
    my_conn = my_msgr.get_conn('192.168.1.3')
    my_msgr.talk(client=my_conn, topic='video_messenger', msg=msg_str)

if __name__ == '__main__':
    #msg('play', 'eyes')
    msg('kill')
