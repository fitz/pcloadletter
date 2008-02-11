#!/usr/bin/python
#
# createfeed.py pulls together a few xml templates, a datafile, and a
# timestamp file to create an rss feed for the pcloadletter podcast
#
# The players:
# * channel.xml: xml fragment representing the container for the whole podcast
# * item.xml: xml fragment representing one podcast
# * data.txt: file containing information needed for the podcast
# * timestamps.txt: maps episodes to timestamps representing the date the
#                   podcast was first released.  Automatically generated.
#                   DO NOT EDIT
#
# The keywords:
#   Channel:
#     DATE
#     ITEMS
#
#   Item:
#     MP3
#     SHOW_DESC
#     LEN
#     DURATION
#     WIKI_PAGE
#     DATE
#     TITLE
#
# Usage: ./createfeed.py # to be run from inside the gen directory
#
# After running, inspect changed files and commit to Subversion

import time

class Item:
  def __init__(self, itemfile):
    self.info = {}
    self.valid = 0
    count = 0
    while 1:
      line = itemfile.readline()
      if not line or line[:3] == "END":
        break
      if line[0] == '#':
        continue
      key, val = line.split(':', 1)
      self.valid = 1
      self.info[key] = val.strip()

  def get(self, key):
    return self.info[key]


def parse_datafile():
  itemfile = open('data.txt', 'r')
  items = []
  while 1:
    item = Item(itemfile)
    if item.valid:
      items.append(item)
    else:
      break
  return items


def now():
  return time.strftime('%a, %e %b %Y %H:%M:%S %z')


def gen_timestamps():
  # Append a timestamp for newest podcast
  ts = open('timestamps.txt', 'a')
  ts.write(str(len(items)) + ':' + now() + '\n')
  ts.close()

  # Read in timestamps
  times = {}
  timelist = open('timestamps.txt', 'r').readlines()
  for time in timelist:
    key, val = time.split(':', 1)
    times[key] = val

  return times


if __name__ == '__main__':
  # Read in item data
  items = parse_datafile()

  # Set current time and get existing timestamps
  times = gen_timestamps()

  # read in item template
  item_template = ''.join(open('item.xml', 'r').readlines())

  # Run substitutions to create xml fragments for each item
  fragments = []
  for item in items:
    # copy template
    fragment = item_template

    episode_num = item.get('EPISODE')
    fragment = fragment.replace('DATE', times[episode_num])

    keywords = ['MP3', 'SHOW_DESC', 'LEN', 'DURATION',
                'WIKI_PAGE', 'TITLE']
    for keyword in keywords:
      fragment = fragment.replace(keyword, item.get(keyword))

    fragments.append(fragment)

  # Create all of our item content
  content = '\n'.join(fragments)

  # Run substitutions on the entire channel
  channel = ''.join(open('channel.xml', 'r').readlines())
  channel = channel.replace('DATE', now())
  channel = channel.replace('ITEMS', content)

  # And print it out
  rss_out = open ('../feed/rss.xml', 'w')
  rss_out.write(channel)

