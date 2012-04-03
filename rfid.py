#!/usr/bin/python
import serial, urllib

open('/sys/kernel/debug/omap_mux/uart1_rxd', 'wb').write('20\n')

ttyRfid = "/dev/ttyO1"
se = serial.Serial(ttyRfid, 9600)

baseUrl = 'http://localhost:4242'

while True:
  tag = ''
  c = se.read()
  if (c != '\x02'):
    print "Error, unexpected character. skipping..."
    while (c != '\x03'):
      se.read()
    continue
  c = se.read()
  while c != '\x03':
    tag += c
    c = se.read()
  url = "%s/tag/%s" % (baseUrl, tag)
  print "Seen tag %s, calling url %s" % (tag, url)
  try:
    urllib.urlopen(url)
  except:
    print "urlopen failed"
    pass
