#!/usr/bin/env python
import select, os, urllib
from time import sleep

baseUrl = 'http://localhost:4242'


class Button:

  def __init__(self, mode0name, gpio, edge, action):
    (self._mode0name, self._gpio, self._edge, self._action) = (mode0name, gpio, edge, action)

  def setup_pin(self):
    open("/sys/kernel/debug/omap_mux/%s" % (self._mode0name), 'wb').write("%X" % 55)  # mode 7, pull up enabled
    gpioDir = "/sys/class/gpio/gpio%d" % (self._gpio)
    if not os.path.exists(gpioDir):
      open("/sys/class/gpio/export", 'wb').write("%s\n" % (self._gpio))
    open("%s/edge" % (gpioDir), 'wb').write("%s\n" % (self._edge))
    open("%s/direction" % (gpioDir), 'wb').write("in\n")

  def add_to_poll(self, poll):
    self._fd = open("/sys/class/gpio/gpio%d/value" % (self._gpio), "rb")
    poll.register(self, select.POLLPRI)
    self._fd.read()

  def fileno(self):
    if (self._fd):
      return self._fd.fileno()
    return -1

  def debounce(self):
    if (self._edge == "both"):
      return True
    self._fd.seek(0)
    v1 = self._fd.read()
    sleep(0.02)
    self._fd.seek(0)
    v2 = self._fd.read()
    return (v1 == v2) and ('0' == v1[0])

  def action(self):
    if self._edge != "both":
      url = "%s/cmd/%s" % (baseUrl, self._action)
    else:
      self._fd.seek(0)
      value = self._fd.read()
      url = "%s/cmd/%s/%s" % (baseUrl, self._action, value[0])
    print "calling url: %s" % url
    try:
      urllib.urlopen(url)
    except:
      print "urlopen failed"
      pass


buttons = [
  Button('gpmc_ad6', 38, 'falling', 'prev'),
  Button('gpmc_ad7', 39, 'falling', 'next'),
  Button('gpmc_ad2', 34, 'falling', 'stop'),
  Button('gpmc_ad15', 47, 'both', 'configMode')
]

poll = select.poll()

for bt in buttons:
  bt.setup_pin()
  bt.add_to_poll(poll)

fdToButton = {}
for bt in buttons:
  fdToButton[bt.fileno()] = bt

while True:
  events = poll.poll()  # blocking
  for (fd, event) in events:
    bt = fdToButton[fd]
    if bt.debounce():
      bt.action()
