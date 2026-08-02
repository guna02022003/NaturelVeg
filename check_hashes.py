import os,hashlib
folder='assets'
for fname in sorted(os.listdir(folder)):
    path=os.path.join(folder,fname)
    try:
        with open(path,'rb') as f:
            data=f.read()
        h=hashlib.sha256(data).hexdigest()
        print(fname, os.path.getsize(path), h)
    except Exception as e:
        print(fname, 'ERROR', e)
