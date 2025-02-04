#
# python routine to create .js files containing freecycle data
#

import boto3
import os
import sys
import configparser
from cryptography.fernet import Fernet
import string

from ddbTables import loadItemDetails

IMGBASEURL = 'https://tvf-att.s3.eu-west-2.amazonaws.com/'
S3_TARGET = "tvf-att"


def writeJSHeader(f, sec):
    f.write('$(function() {\n'
        'var table = document.createElement("table");\n'
        'table.className = "table table-striped table-bordered table-hover table-condensed";\n '
        'var header = table.createTHead(); \nheader.className = "h4"; \n')
    f.write('var row = header.insertRow(0);\n')
    f.write('var cell = row.insertCell(0);\n')
    f.write('cell.innerHTML = "\\<b\\>Item";\n')
    f.write('var cell = row.insertCell(1);\n')
    f.write('cell.innerHTML = "\\<b\\>Description";\n')

    if sec == 'forsale':
        i = 3
        f.write('var cell = row.insertCell(2);\n')
        f.write('cell.innerHTML = "\\<b\\>Price";\n')
    else:
        i = 2
    f.write(f'var cell = row.insertCell({i});\n')
    f.write('cell.innerHTML = "\\<b\\>Contact";\n')
    f.write(f'var cell = row.insertCell({i+1});\n')
    f.write('cell.innerHTML = "\\<b\\>phone";\n')
    f.write(f'var cell = row.insertCell({i+2});\n')
    f.write('cell.innerHTML = "\\<b\\>email";\n')
    if sec != 'wanted':
        f.write(f'var cell = row.insertCell({i+3});\n')
        f.write('cell.innerHTML = "\\<b\\>Photos";\n')


def writeJSFooter(f, sec):
    msgstr = 'var outer_div = document.getElementById("' + sec + '");\n outer_div.appendChild(table);\n})'
    f.write(msgstr)


def writeFSRecord(datadf, f, section):
    fnam = open(f, 'w')
    #print('opened', f)
    writeJSHeader(fnam, section)
    result_row_count = len(datadf)
    if result_row_count == 1:
        fnam.write('var row = table.insertRow(-1);\n')
        fnam.write('var cell = row.insertCell(0);\n')
        fnam.write('cell.innerHTML = "Nothing at the moment";\n')
    
    for _, rwdata in datadf.iterrows():
        if int(rwdata.isdeleted) == 1:
            continue
        ite = ''.join(filter(lambda x:x in string.printable, rwdata.Item))
        des = ''.join(filter(lambda x:x in string.printable, rwdata.description))
        if section == 'forsale':
            pri = rwdata.price
            pri = '{:.2f}'.format(float(pri))
        nam = rwdata.contact_n
        phn = rwdata.contact_p
        ema = rwdata.contact_e
        url1 = rwdata.url1
        url2 = rwdata.url2
        url3 = rwdata.url3

        fnam.write('var row = table.insertRow(-1);\n')
        fnam.write('var cell = row.insertCell(0);\n')
        fnam.write('cell.innerHTML = "' + ite + '";\n')
        fnam.write('var cell = row.insertCell(1);\n')
        fnam.write(f'cell.innerHTML = "{des}";\n')
        if section == 'forsale':
            fnam.write('var cell = row.insertCell(2);\n')
            fnam.write('cell.setAttribute("style","text-align:right");\n')
            fnam.write('cell.innerHTML = "&#163;' + pri + '";\n')
            i = 3
        else:
            i = 2
        fnam.write(f'var cell = row.insertCell({i});\n')
        fnam.write('cell.innerHTML = "' + nam + '";\n')
        fnam.write(f'var cell = row.insertCell({i+1});\n')
        fnam.write('cell.innerHTML = "' + phn + '";\n')
        fnam.write(f'var cell = row.insertCell({i+2});\n')
        fnam.write('cell.innerHTML = "' + ema + '";\n')
        fnam.write(f'var cell = row.insertCell({i+3});\n')
        if section != 'wanted':
            lstr = '"'
            if len(url1.strip()) > 0:
                lstr = lstr + '\\<a href=\\"' + IMGBASEURL + url1 + '\\"\\>link\\</a\\>;'
            if len(url2.strip()) > 0:
                lstr = lstr + '\\<a href=\\"' + IMGBASEURL + url2 + '\\"\\>link\\</a\\>;'
            if len(url3.strip()) > 0:
                lstr = lstr + '\\<a href=\\"' + IMGBASEURL + url3 + '\\"\\>link\\</a\\>;'
            lstr = lstr + '"'
            fnam.write('cell.innerHTML = ' + lstr + '\n')
    writeJSFooter(fnam, section)
    #print('closed', f)
    fnam.close()


def main(cfgfile, upload=True, df=None):
    config = configparser.ConfigParser()
    config.read(cfgfile)
    listtype = config['source']['listtype']

    fskeyName = config['website']['FSFILE']
    fslocName = os.path.join(os.getenv('TMP'), fskeyName)
    wtkeyName = config['website']['WTFILE']
    wtlocName = os.path.join(os.getenv('TMP'), wtkeyName)
    sakeyName = config['website']['SAFILE']
    salocName = os.path.join(os.getenv('TMP'), sakeyName)

    with open('freecycle.key', 'rb') as keyf:
        privatekey = keyf.read()
    decor = Fernet(privatekey)
    dkey = decor.decrypt(config['aws']['KEY'].encode()).decode()
    dsec = decor.decrypt(config['aws']['SEC'].encode()).decode()

    if df is None:
        df = loadItemDetails(listtype)

    df.sort_values(by=['uniqueid'], ascending=False, inplace=True)
    df = df[df.isdeleted==0]

    # Freecycle 
    fsdf = df[df.recType=='Freecycle']
    print(f'got {len(fsdf)} free entries')
    if len(fsdf) > 0:
        writeFSRecord(fsdf, fslocName, 'freecycle')

    # Wanted
    fsdf = df[df.recType=='Wanted']
    print(f'got {len(fsdf)} wanted entries')
    if len(fsdf) > 0:
        writeFSRecord(fsdf, wtlocName, 'wanted')

    # For Sale
    fsdf = df[df.recType=='For Sale']
    print(f'got {len(fsdf)} for-sale entries')
    if len(fsdf) > 0:
        writeFSRecord(fsdf, salocName, 'forsale')

    if upload:
        print('updating website')
        s3 = boto3.client('s3', aws_access_key_id=dkey, aws_secret_access_key=dsec) 
        s3.upload_file(Bucket=S3_TARGET, Key=fskeyName, Filename=fslocName,
                ExtraArgs={'ContentType': "text/javascript"})
        s3.upload_file(Bucket=S3_TARGET, Key=wtkeyName, Filename=wtlocName,
                ExtraArgs={'ContentType': "text/javascript"})
        s3.upload_file(Bucket=S3_TARGET, Key=sakeyName, Filename=salocName,
                ExtraArgs={'ContentType': "text/javascript"})
        print('done')
    return True


if __name__ == '__main__':
    main(sys.argv[1], False)
