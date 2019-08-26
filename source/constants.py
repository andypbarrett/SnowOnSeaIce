import socket
import os

rootdir = '/home/apbarret'

datadir = {'nsidc-apbarret': os.path.join(rootdir, 'data/NPSNOW'),
           'nsidc-abarrett-442': os.path.join(rootdir, 'Data/NPSNOW')}
DATADIR = datadir[socket.gethostname()]

