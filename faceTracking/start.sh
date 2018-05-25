#!/bin/bash

python looking-glass.py --prototxt deploy.prototxt.txt --model res10_300x300_ssd_iter_140000.caffemodel -c 0.9
