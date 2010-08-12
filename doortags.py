#!/usr/bin/env python

"""
Phil Adams (http://philadams.net)

what this code does
"""

import logging
import os
from csv import reader

import aggdraw
from PIL import Image, ImageOps, ImageFont, ImageDraw
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.platypus import Image as RLImage


class Student(object):
    """a cornell student"""

    def __init__(self, last, first, netid, address):
        self.last = last
        self.first = first
        self.netid = netid
        self.roomnumber, self.building = address.split()

    def __repr__(self):
        return 'Student<%s, %s (%s)>' % (self.last, self.first, self.netid)

def build_door_tags():
    """TODO: something here"""

    SIZE = (500, 340)
    FONTSIZE = 68
    SMALLFONTSIZE = 32
    CAPTION_HEIGHT = 100
    CAPTION_OPACITY = 120
    TMP_DIR = './gen'
    DPI, PPI = 72, 113 # 113 on the macbook pro...

    # read in bg image and resize
    original = Image.open('baker_tower.jpg')
    img = original.copy()
    img = ImageOps.fit(img, SIZE)

    # draw opaque caption region
    canvas = aggdraw.Draw(img)
    brush = aggdraw.Brush('white', opacity=CAPTION_OPACITY)
    canvas.rectangle((0, SIZE[1]-CAPTION_HEIGHT, SIZE[0], SIZE[1]), brush)
    canvas.flush()

    # for each name, grab the first name and add it to a cp of the img
    # save each image to a gen folder

    # TODO: confirm an empty TMP_DIR exists

    # TODO: read filenames from list of students
    lines = reader(open('residents.csv'))
    residents = [Student(*line) for line in lines]

    font = ImageFont.truetype('/Library/Fonts/HoboStd.otf', FONTSIZE)
    smallfont = ImageFont.truetype('/Library/Fonts/HoboStd.otf',
                                   SMALLFONTSIZE)
    for resident in residents:
        # add caption
        tag = img.copy()
        canvas = ImageDraw.Draw(tag)
        x, y = font.getsize(resident.first)
        canvas.text((SIZE[0]/2 - x/2, SIZE[1] - CAPTION_HEIGHT/2 - y/2.75),
                    resident.first, font=font, fill=0)
        canvas.text((12, 12), resident.roomnumber, font=smallfont, fill=0)

        fname = '-'.join([resident.netid, resident.first, resident.last])
        fname += '.jpg'
        tag.save(os.path.join(TMP_DIR, fname))

    # arrange the images on a pdf document using tables

    doc = SimpleDocTemplate('doortags.pdf', pagesize=landscape(LETTER))
    elements = []
    table_data = []
    images = os.listdir(TMP_DIR)

    # load images as reportlab images
    for image in images:
        table_data.append(RLImage(os.path.join(TMP_DIR, image),
        width=SIZE[0]*DPI/PPI, height=SIZE[1]*DPI/PPI))

    # cluster table data into groups of 2 for table cols
    if len(table_data) % 2 != 0:
        table_data.append(table_data[-1])
    table_data = zip(*[iter(table_data)]*2)

    table_styles = [('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6)]
    table = Table(table_data, style=table_styles)
    elements.append(table)

    # build and save the pdf doc
    doc.build(elements)

def main():
    """called with __name__ run as __main__"""
    import optparse

    # populate options
    optp = optparse.OptionParser()
    optp.add_option('-v', '--verbose', dest='verbose', action='count',
                    help='increase verbosity (specify multiple times for more)')
    # parse the arguments (defaults to parsing sys.argv)
    opts, args = optp.parse_args()

    # check incoming opts and call optp.error('msg') to exit if all not well

    # logging config
    log_level = logging.WARNING  # default
    if opts.verbose == 1:
        log_level = logging.INFO
    elif opts.verbose >= 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    build_door_tags()

if '__main__' == __name__:
    main()
