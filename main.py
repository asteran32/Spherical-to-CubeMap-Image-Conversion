from transform import cvt_cubemap
import numpy as np
import argparse
import os
from tqdm import tqdm
from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument('--path', '-p', type=str, required=True)
parser.add_argument('--out', '-o', type=str, required=True)

def make_dirs(path:str):
    if not os.path.exists(path):
        os.makedirs(path)
        
if __name__=='__main__':
    
    args = parser.parse_args()
    parttern = os.path.join(args.path, '*\\*.jpg')
    files = glob(parttern)

    # make new directories
    make_dirs(args.out)

    for f in tqdm(files, desc='Processing : '):
        sub_dir = f.split('\\')[-2]
        fname = f.split('\\')[-1]

        cvt_cubemap(f, args.out)
