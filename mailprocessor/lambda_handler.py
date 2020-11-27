import email
import os
from email import policy
import boto3
from botocore.exceptions import ClientError
import time
from datetime import datetime

targetBucket = 'tv-freecycle'
attbucket = "tvf-att"


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
    ite = ite.replace(',', '&#44;').replace('"', '&ldquo;').replace('&', '&amp;')
    ite = ite.replace('£', '&#163;')
    ite = ite.replace("’", '&#39;')

    des = lines[2].rstrip('\n')[13:]
    i = 3
    nxl = lines[i].rstrip('\n')
    while nxl[:5] != 'Price':
        des = des + ' ' + nxl
        i += 1
        numlines -= 1
        nxl = lines[i].rstrip('\n')
    des = des.replace(',', '&#44;').replace('"', '&ldquo;').replace('&', '&amp;')
    des = des.replace('£', '&#163;')
    des = des.replace("’", '&#39;')
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

    idxname = os.getenv('INDEXFILE')
    idxfolder = os.getenv('INDEXFLDR')
    idxFile = idxfolder + '/' + idxname
    fileName = os.path.join(os.getenv('TMP'), idxname)
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

    record = event['Records'][0]
    assert record['eventSource'] == 'aws:ses'

    inuseflg = os.getenv('INDEXFLDR') + '/inuse.txt'
    inuse = True
    while inuse is True:
        try:
            s3.head_object(Bucket=targetBucket, Key=inuseflg)
            print('csv file in use, waiting')
            time.sleep(5)
            inuse = True
        except ClientError:
            inuse = False

    o = s3.get_object(Bucket=targetBucket, Key='freecycle/' + record['ses']['mail']['messageId'])
    raw_mail = o['Body'].read()
    msg = email.message_from_bytes(raw_mail, policy=policy.default)
    bdy = msg.get_body('plain')

    print('========')
    print(bdy.get_content())
    fileName = record['ses']['mail']['messageId'] + '.txt'
    filePath = os.path.join(os.getenv('TMP'), fileName)
    fp = open(filePath, 'w')
    msgbdy = bdy.get_content()
    fp.write(msgbdy.replace('\r', ''))
    print('========')

    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        imgName = part.get_filename()
        imgPath = os.path.join(os.getenv('TMP'), imgName)
        keyName = imgName
        ifp = open(imgPath, 'wb')
        ifp.write(part.get_payload(decode=True))
        ifp.close()
        s3.upload_file(Bucket=attbucket, Key=keyName, Filename=imgPath,
                ExtraArgs={'ContentType': "image/jpg", 'ACL': "public-read"})

        lin = 'url: ' + imgName + '\n'
        fp.write(lin)

    fp.close()

    createLine(filePath, targetBucket)

    tmpf = 'bodies/' + fileName
    s3.upload_file(Bucket=targetBucket, Key=tmpf, Filename=filePath,
        ExtraArgs={'ContentType': "text/html"})
    print('======== done')


if __name__ == '__main__':
    msg = {'messageId': 'ohcg2lg4t9jbqc57ghnk9cg4kt30u31unuagaeo1'}
    ml = {'mail': msg}
    ses = {'ses': ml, 'eventSource': 'aws:ses'}
    recs = []
    recs.append(ses)
    a = {'Records': recs}
    b = 0
    print(a)
    lambda_handler(a, b)
