import os
import PySimpleGUI as sg
import base64

IMAGES = 'images.py'


def parse_images():
    base_folder = './Images'
    names_only = [f for f in os.listdir(base_folder) if f.endswith('.png') or f.endswith('.ico') or f.endswith('.gif')]
    outfile = open(os.path.join(base_folder, IMAGES), 'w')

    for i, file in enumerate(names_only):
        contents = open(os.path.join(base_folder, file), 'rb').read()
        encoded = base64.b64encode(contents)
        outfile.write('\n{} = {}'.format(file[:file.index(".")], encoded))
        sg.OneLineProgressMeter('Base64 Encoding', i + 1, len(names_only), key='-METER-')

    outfile.close()


# parse_images()