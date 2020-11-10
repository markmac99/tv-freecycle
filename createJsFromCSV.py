#
# python routine to create .js files containing freecycle data
#

import boto3
from botocore import exceptions
import time

IMGBASEURL = 'https://tvf-att.s3.eu-west-2.amazonaws.com/'
MAX_ATTEMPTS = 5
ATHENA_DB = 'FREECYCLEDB'
ATHENA_TABLE = 'ENTRIES'
FIELD_DELIMITER = ","
LINE_DELIMITER = "\n"
QUOTE_CHAR = '"'
S3_BUCKET = "s3://tv-freecycle"
S3_INPUT_DIR = f"{S3_BUCKET}/inputs/"
S3_OUTPUT_DIR = f"{S3_BUCKET}/tmp/"
S3_TARGET = "tvf-att"

CREATE_DATABASE = f"CREATE DATABASE IF NOT EXISTS {ATHENA_DB};"
DROP_DATABASE = f"DROP DATABASE {ATHENA_DB};"
DROP_TABLE = f"DROP TABLE {ATHENA_DB}.{ATHENA_TABLE};"

CREATE_TABLE = f"CREATE EXTERNAL TABLE IF NOT EXISTS {ATHENA_DB}.{ATHENA_TABLE} (" \
    "recdt VARCHAR(32), rectyp VARCHAR(10), item VARCHAR(50), descr VARCHAR(300), price VARCHAR(32), " \
    "contact_n VARCHAR(64), contact_e VARCHAR(64), contact_p VARCHAR(32), " \
    "url1 VARCHAR(255), url2 VARCHAR(255), url3 VARCHAR(255), deleted INT ) " \
    "ROW FORMAT DELIMITED " \
    f"FIELDS TERMINATED BY '{FIELD_DELIMITER}' " \
    f"LINES TERMINATED BY '{LINE_DELIMITER}' " \
    f"LOCATION '{S3_INPUT_DIR}' " \
    "TBLPROPERTIES ('skip.header.line.count' = '1');"


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


def writeFSRecord(rw):
    fnam = open('freecycle.js', 'w')
    writeJSHeader(fnam, 'freecycle')
    result_row_count = len(rw)
    if result_row_count == 1:
        fnam.write('var row = table.insertRow(-1);\n')
        fnam.write('var cell = row.insertCell(0);\n')
        fnam.write('cell.innerHTML = "Nothing to show";\n')
    for i in range(result_row_count):
        rwdata = rw[i]['Data']
        typ = rwdata[1]['VarCharValue']
        if typ != 'rectyp':
            typ = rwdata[1]['VarCharValue']
            ite = rwdata[2]['VarCharValue'].replace('�', '-')
            des = rwdata[3]['VarCharValue'].replace('�', '-')
            nam = rwdata[5]['VarCharValue']
            ema = rwdata[6]['VarCharValue']
            phn = rwdata[7]['VarCharValue']
            url1 = rwdata[8]['VarCharValue']
            url2 = rwdata[9]['VarCharValue']
            url3 = rwdata[10]['VarCharValue']
            fnam.write('var row = table.insertRow(-1);\n')
            fnam.write('var cell = row.insertCell(0);\n')
            fnam.write('cell.innerHTML = "' + ite + '";\n')
            fnam.write('var cell = row.insertCell(1);\n')
            fnam.write('cell.innerHTML = "' + des + '";\n')
            fnam.write('var cell = row.insertCell(2);\n')
            fnam.write('cell.innerHTML = "' + nam + '";\n')
            fnam.write('var cell = row.insertCell(3);\n')
            fnam.write('cell.innerHTML = "' + ema + '";\n')
            fnam.write('var cell = row.insertCell(4);\n')
            fnam.write('cell.innerHTML = "' + phn + '";\n')
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
    fnam.close()


def writeSARecord(rw):
    fnam = open('forsale.js', 'w')
    writeJSHeader(fnam, 'forsale')
    result_row_count = len(rw)
    if result_row_count == 1:
        fnam.write('var row = table.insertRow(-1);\n')
        fnam.write('var cell = row.insertCell(0);\n')
        fnam.write('cell.innerHTML = "Nothing to show";\n')
    for i in range(result_row_count):
        rwdata = rw[i]['Data']
        typ = rwdata[1]['VarCharValue']
        if typ != 'rectyp':
            typ = rwdata[1]['VarCharValue']
            ite = rwdata[2]['VarCharValue'].replace('�', '-')
            des = rwdata[3]['VarCharValue'].replace('�', '-')
            pri = rwdata[4]['VarCharValue']
            nam = rwdata[5]['VarCharValue']
            ema = rwdata[6]['VarCharValue']
            phn = rwdata[7]['VarCharValue']
            url1 = rwdata[8]['VarCharValue']
            url2 = rwdata[9]['VarCharValue']
            url3 = rwdata[10]['VarCharValue']
            fnam.write('var row = table.insertRow(-1);\n')
            fnam.write('var cell = row.insertCell(0);\n')
            fnam.write('cell.innerHTML = "' + ite + '";\n')
            fnam.write('var cell = row.insertCell(1);\n')
            fnam.write('cell.innerHTML = "' + des + '";\n')
            fnam.write('var cell = row.insertCell(2);\n')
            fnam.write('cell.innerHTML = "&#163;' + pri + '";\n')
            fnam.write('var cell = row.insertCell(3);\n')
            fnam.write('cell.innerHTML = "' + nam + '";\n')
            fnam.write('var cell = row.insertCell(4);\n')
            fnam.write('cell.innerHTML = "' + ema + '";\n')
            fnam.write('var cell = row.insertCell(5);\n')
            fnam.write('cell.innerHTML = "' + phn + '";\n')
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
    fnam.close()


def writeWTRecord(rw):
    fnam = open('wanted.js', 'w')
    writeJSHeader(fnam, 'wanted')
    result_row_count = len(rw)
    if result_row_count == 1:
        fnam.write('var row = table.insertRow(-1);\n')
        fnam.write('var cell = row.insertCell(0);\n')
        fnam.write('cell.innerHTML = "Nothing to show";\n')
    for i in range(result_row_count):
        rwdata = rw[i]['Data']
        typ = rwdata[1]['VarCharValue']
        if typ != 'rectyp':
            typ = rwdata[1]['VarCharValue']
            ite = rwdata[2]['VarCharValue'].replace('�', '-')
            des = rwdata[3]['VarCharValue'].replace('�', '-')
            nam = rwdata[5]['VarCharValue']
            ema = rwdata[6]['VarCharValue']
            phn = rwdata[7]['VarCharValue']
            fnam.write('var row = table.insertRow(-1);\n')
            fnam.write('var cell = row.insertCell(0);\n')
            fnam.write('cell.innerHTML = "' + ite + '";\n')
            fnam.write('var cell = row.insertCell(1);\n')
            fnam.write('cell.innerHTML = "' + des + '";\n')
            fnam.write('var cell = row.insertCell(2);\n')
            fnam.write('cell.innerHTML = "' + nam + '";\n')
            fnam.write('var cell = row.insertCell(3);\n')
            fnam.write('cell.innerHTML = "' + ema + '";\n')
            fnam.write('var cell = row.insertCell(4);\n')
            fnam.write('cell.innerHTML = "' + phn + '";\n')
            fnam.write('var cell = row.insertCell(5);\n')
    writeJSFooter(fnam, 'wanted')
    fnam.close()


def execute_query(athena_client: boto3.client, query: str) -> dict:
    return athena_client.start_query_execution(
        QueryString=query,
        ResultConfiguration={
            "OutputLocation": S3_OUTPUT_DIR,
            "EncryptionConfiguration": {
                "EncryptionOption": "SSE_S3"
            }
        }
    )


def fetch_query_results(athena_client: boto3.client, amazon_response: dict) -> dict:
    query_result = None
    num_attempts = 0

    while not query_result and num_attempts < MAX_ATTEMPTS:
        time.sleep(3)
        num_attempts += 1

        try:
            query_result = athena_client.get_query_results(
                QueryExecutionId=amazon_response['QueryExecutionId']
            )
        except exceptions.ClientError:
            print(f"Attempt {num_attempts} of {MAX_ATTEMPTS} failed.")
            if num_attempts < MAX_ATTEMPTS:
                print("Trying again ...")
            else:
                print("No further retries.")

    return query_result


def main():
    athena_client = boto3.client('athena', region_name='eu-west-2')
    try:
        # print(CREATE_TABLE)
        print('Creating table and database')
        execute_query(athena_client, CREATE_DATABASE)
        execute_query(athena_client, CREATE_TABLE)

        print('executing query')
        amazon_response = execute_query(athena_client,
            f'SELECT DISTINCT * FROM {ATHENA_DB}.{ATHENA_TABLE} WHERE rectyp = \'Freecycle\' AND deleted=0 ORDER by 1 DESC;')

        print('fetching query results')
        query_results = fetch_query_results(athena_client, amazon_response)

        result_row_count = len(query_results['ResultSet']['Rows'])
        print('got ', result_row_count - 1, ' rows')
        if result_row_count > 0:
            r = query_results['ResultSet']['Rows']
            writeFSRecord(r)

        amazon_response = execute_query(athena_client,
            f'SELECT DISTINCT * FROM {ATHENA_DB}.{ATHENA_TABLE} WHERE rectyp = \'Wanted\' AND deleted=0 ORDER by 1 DESC;')
        query_results = fetch_query_results(athena_client, amazon_response)
        result_row_count = len(query_results['ResultSet']['Rows'])
        print('got ', result_row_count - 1, ' rows')
        if result_row_count > 0:
            r = query_results['ResultSet']['Rows']
            writeWTRecord(r)

        amazon_response = execute_query(athena_client,
            f'SELECT DISTINCT * FROM {ATHENA_DB}.{ATHENA_TABLE} WHERE rectyp = \'For Sale\' AND deleted=0 ORDER by 1 DESC;')
        query_results = fetch_query_results(athena_client, amazon_response)
        result_row_count = len(query_results['ResultSet']['Rows'])
        print('got ', result_row_count - 1, ' rows')
        if result_row_count > 0:
            r = query_results['ResultSet']['Rows']
            writeSARecord(r)

        execute_query(athena_client, DROP_TABLE)
        execute_query(athena_client, DROP_DATABASE)
    except exceptions.ClientError as err:
        exit(err.response['Error']['Message'])

    s3 = boto3.client('s3')
    keyName = 'freecycle.js'
    s3.upload_file(Bucket=S3_TARGET, Key=keyName, Filename=keyName,
            ExtraArgs={'ContentType': "text/javascript"})
    keyName = 'wanted.js'
    s3.upload_file(Bucket=S3_TARGET, Key=keyName, Filename=keyName,
            ExtraArgs={'ContentType': "text/javascript"})
    keyName = 'forsale.js'
    s3.upload_file(Bucket=S3_TARGET, Key=keyName, Filename=keyName,
            ExtraArgs={'ContentType': "text/javascript"})


if __name__ == '__main__':
    main()
