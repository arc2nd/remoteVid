import os
import json
import commands

from pellets.DurableMessenger import *

def msg(cmd, *args):
    print('Msg: {}'.format(cmd))
    # Compose Message
    if cmd == 'play':
        msg_dict = {'command': cmd, 'video': args[0]}
    elif cmd == 'kill':
        msg_dict = {'command': cmd}
    msg_str = json.dumps(msg_dict, sort_keys=True) # , indent=4)

    # Create Messenger Object
    my_msgr = DurableMessenger()
    my_msgr.talk(chan_name='video_messenger', msg=msg_str)


