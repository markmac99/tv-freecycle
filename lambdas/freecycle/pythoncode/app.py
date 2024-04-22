import email
import os
import sys
from email import policy
import boto3
from botocore.exceptions import ClientError
import time
from datetime import datetime
import pyheif
from PIL import Image

targetBucket = 'tv-freecycle'
attbucket = "tvf-att"


def convertHEIC(srcfile):
    img=pyheif.read(srcfile)
    image = Image.frombytes(img.mode, img.size, img.data, "raw", img.mode, img.stride)
    fn, _ = os.path.splitext(srcfile)
    newn = fn + '.jpg'
    image.save(newn)
    return newn


def createLine(fname, targetBucket, attnames):
    f = open(fname, 'r')
    lines = [line.rstrip('\n') for line in f]
    lines = [x for x in lines if x.strip()]
    f.close()
    numlines = len(lines)
    print(lines, numlines)

    nowdt = datetime.now().strftime('%Y%m%d%H%M%S')
    csvline = nowdt + ','
    typ = lines[0].rstrip('\n')[7:]
    ite = lines[1].rstrip('\n')[6:]
    ite = ite.replace('&', '&amp;').replace(',', '&#44;').replace('"', '&rdquo;')
    ite = ite.replace('£', '&#163;').replace('“', '&ldquo;').replace('”', '&rdquo;')
    ite = ite.replace("'", '&#39;').replace('<', '&lt;').replace('>', '&gt;')
    ite = ite.replace('‘', '&lsquo;').replace('’', '&rsquo;')

    des = lines[2].rstrip('\n')[13:]
    i = 3
    nxl = lines[i].rstrip('\n')
    while nxl[:5] != 'Price':
        des = des + ' ' + nxl
        i += 1
        numlines -= 1
        nxl = lines[i].rstrip('\n')
    des = des.replace('&', '&amp;').replace(',', '&#44;').replace('"', '&rdquo;')
    des = des.replace('£', '&#163;').replace('“', '&ldquo;').replace('”', '&rdquo;')
    des = des.replace("'", '&#39;').replace('<', '&lt;').replace('>', '&gt;')
    des = des.replace('‘', '&lsquo;').replace('’', '&rsquo;')
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
        url = attnames[0]
        csvline = csvline + ',' + url + ',,,0'
    elif numlines == 9:
        url = attnames[0]
        url1 = attnames[1]
        csvline = csvline + ',' + url + ',' + url1 + ',,0'
    else:
        url = attnames[0]
        url1 = attnames[1]
        url2 = attnames[2]
        csvline = csvline + ',' + url + ',' + url1 + ',' + url2 + ',0'

    csvline = csvline + '\n'

    s3 = boto3.client('s3')

    idxname = os.getenv('INDEXFILE',default="freecycle-data.csv")
    idxfolder = os.getenv('INDEXFLDR', default="fslist")
    idxFile = idxfolder + '/' + idxname
    fileName = os.path.join(os.getenv('TMP', default='/tmp'), idxname)
    print(idxFile, fileName, targetBucket)

    s3.download_file(Bucket=targetBucket, Key=idxFile, Filename=fileName)
    with open(fileName, "a+") as f:
        print('writing ', csvline)
        f.write(csvline)
    f.close()
    s3.upload_file(Bucket=targetBucket, Key=idxFile, Filename=fileName)
    return csvline


def lambda_handler(event, context):
    s3 = boto3.client('s3')

    if 'Records' not in event:
        return 
    record = event['Records'][0]
    if 'eventSource' not in record:
        return 

    inuseflg = os.getenv('INDEXFLDR', default="fslist") + '/inuse.txt'
    inuse = True
    while inuse is True:
        try:
            s3.head_object(Bucket=targetBucket, Key=inuseflg)
            print('csv file in use, waiting')
            time.sleep(5)
            inuse = True
        except ClientError:
            inuse = False

    try:
        fsobj = s3.get_object(Bucket=targetBucket, Key='freecycle/' + record['ses']['mail']['messageId'])
    except:
        print('email object not found')
        return
    try:
        raw_mail = fsobj['Body'].read()
        msg = email.message_from_bytes(raw_mail, policy=policy.default)
        bdy = msg.get_body('plain')
    except:
        print('unable to find message body')
        return
    # print(bdy.get_content())
    fileName = record['ses']['mail']['messageId'] + '.txt'
    filePath = os.path.join(os.getenv('TMP', default='/tmp'), fileName)
    fp = open(filePath, 'w')
    msgbdy = bdy.get_content()
    fp.write(msgbdy.replace('\r', ''))

    attnames = []
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        imgName = part.get_filename()
        imgPath = os.path.join(os.getenv('TMP', default='/tmp'), imgName)
        keyName = imgName
        ifp = open(imgPath, 'wb')
        data = part.get_payload(decode=True)
        ifp.write(data)
        ifp.close()
        if b'ftypheic' in data:
            imgPath = convertHEIC(imgPath)
            keyName = os.path.split(imgPath)[1]
        print(f'attachment {keyName}')
        attnames.append(keyName)
        s3.upload_file(Bucket=attbucket, Key=keyName, Filename=imgPath,
                ExtraArgs={'ContentType': "image/jpg", 'ACL': "public-read"})

        lin = 'url: ' + imgName + '\n'
        fp.write(lin)
        print('saved attachment')
    fp.close()

    print('adding line to file')
    createLine(filePath, targetBucket, attnames)

    tmpf = 'bodies/' + fileName
    s3.upload_file(Bucket=targetBucket, Key=tmpf, Filename=filePath,
        ExtraArgs={'ContentType': "text/html"})
    print('done')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        msg = {'messageId': sys.argv[1]}
    else:
        msg = {'messageId': '1gb599l09j4gqdcmmakkr9ebi5oc4l1vfolbl101'}
    ml = {'mail': msg}
    ses = {'ses': ml, 'eventSource': 'aws:ses'}
    recs = []
    recs.append(ses)
    a = {'Records': recs}
    b = 0
    print(a)
    lambda_handler(a, b)
