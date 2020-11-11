#
# python routine to create single csv separated line from mail message
#

import boto3
import os
from datetime import datetime


def createLine(fname, targetBucket):
    f = open(fname, 'r')
    lines = [line.rstrip('\n') for line in f]
    f.close()
    numlines = len(lines)
    print(lines, numlines)

    nowdt = datetime.now().strftime('%Y%m%d%H%M%S')
    csvline = nowdt + ','
    typ = lines[0].rstrip('\n')[7:]
    ite = lines[1].rstrip('\n')[6:]
    des = lines[2].rstrip('\n')[13:]
    i = 3
    nxl = lines[i].rstrip('\n')
    while nxl[:5] != 'Price':
        des = des + ' ' + nxl
        i += 1
        numlines -= 1
        nxl = lines[i].rstrip('\n')
    des = des.replace(',', '&#44;')
    des = des.replace('£', '&#163;')
    pri = nxl[7:]
    if len(pri) == 0:
        pri = '0'
    else:
        pri = pri.replace('£', '')
    nam = lines[i + 1].rstrip('\n')[6:]
    pho = lines[i + 2].rstrip('\n')[7:]
    ema = lines[i + 3].rstrip('\n')[7:]
    csvline = csvline + typ + ',' + ite + ',' + des + ','
    csvline = csvline + pri + ',' + nam + ',' + pho + ',' + ema
    if numlines == 7:
        csvline = csvline + ',,,,0'
    elif numlines == 8:
        url = lines[i + 4].rstrip('\n')[5:]
        csvline = csvline + ',' + url + ',,,0'
    elif numlines == 9:
        url = lines[i + 4].rstrip('\n')[5:]
        url1 = lines[i + 5].rstrip('\n')[5:]
        csvline = csvline + ',' + url + ',' + url1 + ',,0'
    else:
        url = lines[i + 4].rstrip('\n')[5:]
        url1 = lines[i + 5].rstrip('\n')[5:]
        url2 = lines[i + 6].rstrip('\n')[5:]
        csvline = csvline + ',' + url + ',' + url1 + ',' + url2 + ',0'

    csvline = csvline + '\n'

    s3 = boto3.client('s3')

    keyName = 'inputs/freecycle-data.csv'
    fileName = os.path.join(os.getenv('TMP'), 'freecycle-data.csv')

    print(keyName, fileName, targetBucket)
    s3.download_file(Bucket=targetBucket, Key=keyName, Filename=fileName)
    with open(fileName, "a+") as f:
        print('writing ', csvline)
        f.write(csvline)
    f.close()
    s3.upload_file(Bucket=targetBucket, Key=keyName, Filename=fileName)
    return csvline


if __name__ == '__main__':
    # csvline = createLine('bodies/4utml0omd2icueuku05q5so83ftb6kn9973leq81.txt', 'tv-freecycle')
    # csvline = createLine('bodies/0jsodvnr6i89b6ik68m7fhgkuoblt2vhpb65oog1.txt', 'tv-freecycle')
    csvline = createLine('bodies/0pgk272at81avismkc12tilqrovndob8qg4pj9o1.txt', 'tv-freecycle')
