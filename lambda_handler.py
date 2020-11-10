import email
import os
from email import policy
import boto3

import updateCSV

targetBucket = 'tv-freecycle'
attbucket = "tvf-att"


def lambda_handler(event, context):
    s3 = boto3.client('s3')

    record = event['Records'][0]
    assert record['eventSource'] == 'aws:ses'

    o = s3.get_object(Bucket=targetBucket, Key='freecycle/' + record['ses']['mail']['messageId'])
    raw_mail = o['Body'].read()
    msg = email.message_from_bytes(raw_mail, policy=policy.default)
    bdy = msg.get_body('plain')

    print('========')
    print(bdy.get_content())
    fileName = record['ses']['mail']['messageId'] + '.txt'
    filePath = os.path.join('/tmp', fileName)
    fp = open(filePath, 'w')
    msgbdy = bdy.get_content()
    fp.write(msgbdy)
    print('========')

    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        imgName = part.get_filename()
        imgPath = os.path.join('/tmp', imgName)
        keyName = imgName
        ifp = open(imgPath, 'wb')
        ifp.write(part.get_payload(decode=True))
        ifp.close()
        s3.upload_file(Bucket=attbucket, Key=keyName, Filename=imgPath,
                ExtraArgs={'ContentType': "image/jpg", 'ACL': "public-read"})

        lin = 'url: ' + imgName
        fp.write(lin)

    fp.close()

    updateCSV.createLine(filePath, targetBucket)

    tmpf = 'bodies/' + fileName
    s3.upload_file(Bucket=targetBucket, Key=tmpf, Filename=filePath,
        ExtraArgs={'ContentType': "text/html"})
    print('======== done')
