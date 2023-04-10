#
# python routine to create .js files containing freecycle data
#

import boto3
from botocore import exceptions
import time
import os
import configparser
from cryptography.fernet import Fernet
import string


IMGBASEURL = 'https://tvf-att.s3.eu-west-2.amazonaws.com/'
MAX_ATTEMPTS = 3
PAUSETIME = 3
ATHENA_TABLE = 'ENTRIES'
FIELD_DELIMITER = ","
LINE_DELIMITER = "\n"
QUOTE_CHAR = '"'
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
    f.write('var cell = row.insertCell(' + str(i) + ');\n')
    f.write('cell.innerHTML = "\\<b\\>Contact";\n')
    i = i + 1
    f.write('var cell = row.insertCell(' + str(i) + ');\n')
    f.write('cell.innerHTML = "\\<b\\>phone";\n')
    i = i + 1
    f.write('var cell = row.insertCell(' + str(i) + ');\n')
    f.write('cell.innerHTML = "\\<b\\>email";\n')
    if sec != 'wanted':
        i = i + 1
        f.write('var cell = row.insertCell(' + str(i) + ');\n')
        f.write('cell.innerHTML = "\\<b\\>Photos";\n')


def writeJSFooter(f, sec):
    msgstr = 'var outer_div = document.getElementById("' + sec + '");\n outer_div.appendChild(table);\n})'
    f.write(msgstr)


def writeFSRecord(rw, f):
    fnam = open(f, 'w')
    # print('opened', f)
    writeJSHeader(fnam, 'freecycle')
    result_row_count = len(rw)
    if result_row_count == 1:
        fnam.write('var row = table.insertRow(-1);\n')
        fnam.write('var cell = row.insertCell(0);\n')
        fnam.write('cell.innerHTML = "Nothing at the moment";\n')
    for i in range(result_row_count):
        rwdata = rw[i]['Data']
        typ = rwdata[1]['VarCharValue']
        if typ != 'rectyp':
            typ = rwdata[1]['VarCharValue']
            ite = ''.join(filter(lambda x:x in string.printable, rwdata[2]['VarCharValue']))
            des = ''.join(filter(lambda x:x in string.printable, rwdata[3]['VarCharValue']))
            nam = rwdata[5]['VarCharValue']
            phn = rwdata[6]['VarCharValue']
            ema = rwdata[7]['VarCharValue']
            url1 = rwdata[8]['VarCharValue']
            url2 = rwdata[9]['VarCharValue']
            url3 = rwdata[10]['VarCharValue']
            fnam.write('var row = table.insertRow(-1);\n')
            fnam.write('var cell = row.insertCell(0);\n')
            fnam.write('cell.innerHTML = "' + ite + '";\n')
            fnam.write('var cell = row.insertCell(1);\n')
            fnam.write(f'cell.innerHTML = "{des}";\n')
            fnam.write('var cell = row.insertCell(2);\n')
            fnam.write('cell.innerHTML = "' + nam + '";\n')
            fnam.write('var cell = row.insertCell(3);\n')
            fnam.write('cell.innerHTML = "' + phn + '";\n')
            fnam.write('var cell = row.insertCell(4);\n')
            fnam.write('cell.innerHTML = "' + ema + '";\n')
            fnam.write('var cell = row.insertCell(5);\n')
            lstr = '"'
            if len(url1.strip()) > 0:
                lstr = lstr + '\\<a href=\\"' + IMGBASEURL + url1 + '\\"\\>link\\</a\\>;'
            if len(url2.strip()) > 0:
                lstr = lstr + '\\<a href=\\"' + IMGBASEURL + url2 + '\\"\\>link\\</a\\>;'
            if len(url3.strip()) > 0:
                lstr = lstr + '\\<a href=\\"' + IMGBASEURL + url3 + '\\"\\>link\\</a\\>;'
            lstr = lstr + '"'
            fnam.write('cell.innerHTML = ' + lstr + '\n')
    writeJSFooter(fnam, 'freecycle')
    #print('closed', f)
    fnam.close()


def writeSARecord(rw, f):
    fnam = open(f, 'w')
    # print('opened', f)
    writeJSHeader(fnam, 'forsale')
    result_row_count = len(rw)
    if result_row_count == 1:
        fnam.write('var row = table.insertRow(-1);\n')
        fnam.write('var cell = row.insertCell(0);\n')
        fnam.write('cell.innerHTML = "Nothing at the moment";\n')
    for i in range(result_row_count):
        rwdata = rw[i]['Data']
        typ = rwdata[1]['VarCharValue']
        if typ != 'rectyp':
            typ = rwdata[1]['VarCharValue']
            ite = rwdata[2]['VarCharValue'].replace('�', '')
            des = rwdata[3]['VarCharValue'].replace('�', '')
            pri = rwdata[4]['VarCharValue']
            pri = '{:.2f}'.format(float(pri))
            nam = rwdata[5]['VarCharValue']
            phn = rwdata[6]['VarCharValue']
            ema = rwdata[7]['VarCharValue']
            url1 = rwdata[8]['VarCharValue']
            url2 = rwdata[9]['VarCharValue']
            url3 = rwdata[10]['VarCharValue']
            fnam.write('var row = table.insertRow(-1);\n')
            fnam.write('var cell = row.insertCell(0);\n')
            fnam.write('cell.innerHTML = "' + ite + '";\n')
            fnam.write('var cell = row.insertCell(1);\n')
            fnam.write('cell.innerHTML = "' + des + '";\n')
            fnam.write('var cell = row.insertCell(2);\n')
            fnam.write('cell.setAttribute("style","text-align:right");\n')
            fnam.write('cell.innerHTML = "&#163;' + pri + '";\n')
            fnam.write('var cell = row.insertCell(3);\n')
            fnam.write('cell.innerHTML = "' + nam + '";\n')
            fnam.write('var cell = row.insertCell(4);\n')
            fnam.write('cell.innerHTML = "' + phn + '";\n')
            fnam.write('var cell = row.insertCell(5);\n')
            fnam.write('cell.innerHTML = "' + ema + '";\n')
            fnam.write('var cell = row.insertCell(6);\n')
            lstr = '"'
            if len(url1.strip()) > 0:
                lstr = lstr + '\\<a href=\\"' + IMGBASEURL + url1 + '\\"\\>link\\</a\\>;'
            if len(url2.strip()) > 0:
                lstr = lstr + '\\<a href=\\"' + IMGBASEURL + url2 + '\\"\\>link\\</a\\>;'
            if len(url3.strip()) > 0:
                lstr = lstr + '\\<a href=\\"' + IMGBASEURL + url3 + '\\"\\>link\\</a\\>;'
            lstr = lstr + '"'
            fnam.write('cell.innerHTML = ' + lstr + '\n')
    writeJSFooter(fnam, 'forsale')
    # print('closed', f)
    fnam.close()


def writeWTRecord(rw, f):
    fnam = open(f, 'w')
    # print('opened', f)
    writeJSHeader(fnam, 'wanted')
    result_row_count = len(rw)
    if result_row_count == 1:
        fnam.write('var row = table.insertRow(-1);\n')
        fnam.write('var cell = row.insertCell(0);\n')
        fnam.write('cell.innerHTML = "Nothing at the moment";\n')
    for i in range(result_row_count):
        rwdata = rw[i]['Data']
        typ = rwdata[1]['VarCharValue']
        if typ != 'rectyp':
            typ = rwdata[1]['VarCharValue']
            ite = rwdata[2]['VarCharValue'].replace('�', '')
            des = rwdata[3]['VarCharValue'].replace('�', '')
            nam = rwdata[5]['VarCharValue']
            phn = rwdata[6]['VarCharValue']
            ema = rwdata[7]['VarCharValue']
            fnam.write('var row = table.insertRow(-1);\n')
            fnam.write('var cell = row.insertCell(0);\n')
            fnam.write('cell.innerHTML = "' + ite + '";\n')
            fnam.write('var cell = row.insertCell(1);\n')
            fnam.write('cell.innerHTML = "' + des + '";\n')
            fnam.write('var cell = row.insertCell(2);\n')
            fnam.write('cell.innerHTML = "' + nam + '";\n')
            fnam.write('var cell = row.insertCell(3);\n')
            fnam.write('cell.innerHTML = "' + phn + '";\n')
            fnam.write('var cell = row.insertCell(4);\n')
            fnam.write('cell.innerHTML = "' + ema + '";\n')
            fnam.write('var cell = row.insertCell(5);\n')
    writeJSFooter(fnam, 'wanted')
    # print('closed', f)
    fnam.close()


def execute_query(athena_client: boto3.client, query: str, outdir) -> dict:
    return athena_client.start_query_execution(
        QueryString=query,
        ResultConfiguration={
            "OutputLocation": outdir,
            "EncryptionConfiguration": {
                "EncryptionOption": "SSE_S3"
            }
        }
    )


def fetch_query_results(athena_client: boto3.client, amazon_response: dict) -> dict:
    query_result = None
    num_attempts = 0

    time.sleep(5)
    while not query_result and num_attempts < MAX_ATTEMPTS:
        num_attempts += 1

        try:
            query_result = athena_client.get_query_results(
                QueryExecutionId=amazon_response['QueryExecutionId']
            )
        except exceptions.ClientError:
            print(f"Attempt {num_attempts} of {MAX_ATTEMPTS} failed.")
            if num_attempts < MAX_ATTEMPTS:
                print("Trying again ...")
                time.sleep(PAUSETIME)
            else:
                print("No further retries.")

    return query_result


def main(cfgfile):
    config = configparser.ConfigParser()
    config.read(cfgfile)
    srcBucket = config['source']['BUCKET']
    listfldr = config['source']['LISTFLDR']
    athenadb = config['source']['ATHENADB']

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

    CREATE_DATABASE = f"CREATE DATABASE IF NOT EXISTS {athenadb};"
    DROP_DATABASE = f"DROP DATABASE {athenadb};"
    DROP_TABLE = f"DROP TABLE {athenadb}.{ATHENA_TABLE};"
    S3_BUCKET = f's3://{srcBucket}'
    indir = f"{S3_BUCKET}/{listfldr}/"
    outdir = f"{S3_BUCKET}/tmp/"

    CREATE_TABLE = f"CREATE EXTERNAL TABLE IF NOT EXISTS {athenadb}.{ATHENA_TABLE} (" \
        "recdt VARCHAR(32), rectyp VARCHAR(10), item VARCHAR(50), descr VARCHAR(300), price VARCHAR(32), " \
        "contact_n VARCHAR(64), contact_p VARCHAR(64), contact_e VARCHAR(64), " \
        "url1 VARCHAR(255), url2 VARCHAR(255), url3 VARCHAR(255), deleted INT ) " \
        "ROW FORMAT DELIMITED " \
        f"FIELDS TERMINATED BY '{FIELD_DELIMITER}' " \
        f"LINES TERMINATED BY '{LINE_DELIMITER}' " \
        f"LOCATION '{indir}' " \
        "TBLPROPERTIES ('skip.header.line.count' = '1');"

    athena_client = boto3.client('athena', region_name='eu-west-2',
        aws_access_key_id=dkey, aws_secret_access_key=dsec)
    try:
        print('Creating table and database')
        execute_query(athena_client, CREATE_DATABASE, outdir)
        execute_query(athena_client, CREATE_TABLE, outdir)

        print('executing query 1')
        amazon_response = execute_query(athena_client,
            f'SELECT DISTINCT * FROM {athenadb}.{ATHENA_TABLE} WHERE rectyp = \'Freecycle\' AND deleted=0 ORDER by 1 DESC;', outdir)

        query_results = fetch_query_results(athena_client, amazon_response)

        result_row_count = len(query_results['ResultSet']['Rows'])
        print('got ', result_row_count - 1, ' rows')
        if result_row_count > 0:
            r = query_results['ResultSet']['Rows']
            writeFSRecord(r, fslocName)

        print('executing query 2')
        amazon_response = execute_query(athena_client,
            f'SELECT DISTINCT * FROM {athenadb}.{ATHENA_TABLE} WHERE rectyp = \'Wanted\' AND deleted=0 ORDER by 1 DESC;', outdir)
        query_results = fetch_query_results(athena_client, amazon_response)
        result_row_count = len(query_results['ResultSet']['Rows'])
        print('got ', result_row_count - 1, ' rows')
        if result_row_count > 0:
            r = query_results['ResultSet']['Rows']
            writeWTRecord(r, wtlocName)

        print('executing query 3')
        amazon_response = execute_query(athena_client,
            f'SELECT DISTINCT * FROM {athenadb}.{ATHENA_TABLE} WHERE rectyp = \'For Sale\' AND deleted=0 ORDER by 1 DESC;', outdir)
        query_results = fetch_query_results(athena_client, amazon_response)
        result_row_count = len(query_results['ResultSet']['Rows'])
        print('got ', result_row_count - 1, ' rows')
        if result_row_count > 0:
            r = query_results['ResultSet']['Rows']
            writeSARecord(r, salocName)

        print('Dropping tables and database')
        execute_query(athena_client, DROP_TABLE, outdir)
        execute_query(athena_client, DROP_DATABASE, outdir)
    except:
        return False

    print('updating website')
    s3 = boto3.client('s3', aws_access_key_id=dkey, aws_secret_access_key=dsec)  # , region_name='eu-west-2')
    s3.upload_file(Bucket=S3_TARGET, Key=fskeyName, Filename=fslocName,
            ExtraArgs={'ContentType': "text/javascript"})
    s3.upload_file(Bucket=S3_TARGET, Key=wtkeyName, Filename=wtlocName,
            ExtraArgs={'ContentType': "text/javascript"})
    s3.upload_file(Bucket=S3_TARGET, Key=sakeyName, Filename=salocName,
            ExtraArgs={'ContentType': "text/javascript"})
    return True


if __name__ == '__main__':
    main('config.ini')
