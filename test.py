
from __future__ import print_function

import numpy as np
import argparse
import cv2    
import csv

f = open('test.csv', 'wb')
writer=csv.writer(f, delimiter=' ',quoting=csv.QUOTE_MINIMAL)
writer.writerow(([1,2,3], [4, 5, 6]))
f.close()

f = open('test.csv', 'rb')
reader = csv.reader(f, delimiter=' ',quoting=csv.QUOTE_MINIMAL)
#data = [int(v) for v in next(reader)]
data1, data2 = next(reader)
data1 = data1.translate(None, '[],').split()
data1 = [int(v) for v in data1]

data2 = data2.translate(None, '[],').split()
data2 = [int(v) for v in data2]

print('data = {}, {}'.format(data1, data2))
f.close()