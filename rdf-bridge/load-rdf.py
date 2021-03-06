import os
import sys
import redis

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf8')

r = redis.StrictRedis(host='localhost', port=6379, db=0)
prfix = sys.argv[1]
file_path = sys.argv[2]
mod = int(sys.argv[3])
db_key = sys.argv[4]
start = 0
current = 0

if len(sys.argv) >= 6:
    start = int(sys.argv[5])

fp = open(file_path+'-'+prfix+'-all')
for n,line in enumerate(fp):
    if current < start:
        current = current + 1
        continue
    
    line = line.replace("\n", '')
    r.set(db_key+'-'+prfix+'-'+line, str(n+1))
    r.set(db_key+'-'+prfix+'-'+str(n+1), line)

    if n%mod == 0:
        print str(n+1), ':' , line

