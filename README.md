A namekox service is just a class:
```
# ping.py

from datetime import datetime
from namekox_timer.core.entrypoints.timer import timer


class Ping(object):
    name = 'ping'

    @timer(5, eager=True)
    def ping(self):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('pong at {}'.format(now))
```
You can run it in a shell:
```
# namekox run ping
2020-09-14 22:08:41,901 INFO starting services ['ping']
2020-09-14 22:08:41,902 INFO services ['ping'] started
pong at 2020-09-14 22:08:46
pong at 2020-09-14 22:08:51
pong at 2020-09-14 22:08:56
pong at 2020-09-14 22:09:01
pong at 2020-09-14 22:09:06
pong at 2020-09-14 22:09:11
pong at 2020-09-14 22:09:16
pong at 2020-09-14 22:09:21
^C2020-09-14 22:09:21,966 INFO stopping services ['ping']
2020-09-14 22:09:21,967 INFO services ['ping'] stopped
2020-09-14 22:09:21,967 INFO killing services: ['ping']
2020-09-14 22:09:21,967 INFO services ['ping'] killed
```
