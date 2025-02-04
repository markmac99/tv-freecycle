#
# Create and access dynamodb tables containing camera upload timings etc
#
# Copyright (C) 2018-2023 Mark McIntyre

import boto3
import os
import pandas as pd
import datetime


# remove a row from the table keyed on stationid adn datestamp in yyyymmdd_hhmmss format
def deleteRow(tblname='freecycle', ddb=None, uniqueid=None):
    if not uniqueid:
        return 
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = ddb.Table(tblname)
    try:
        table.delete_item(Key={'uniqueid': uniqueid})
    except Exception:
        pass
    return 


def addRow(tblname='freecycle', ddb=None, newdata=None):
    '''
    add a row to the CamDetails table
    '''
    if not newdata:
        return 
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = ddb.Table(tblname)
    response = table.put_item(Item=newdata)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print('error writing to table')
    return 


def dumpCamTable(outdir, tblname='freecycle', ddb=None):
    data = loadItemDetails(tblname, ddb)
    data.to_csv(os.path.join(outdir,f'{tblname}.csv'), index=False)


def loadItemDetails(table='freecycle', ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = ddb.Table(table)
    res = table.scan()
    values = res.get('Items', [])
    data = pd.DataFrame(values)
    data.sort_values(by=['uniqueid'], inplace=True)
    return data


def getLastUniqueid(table='freecycle', ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = ddb.Table(table)
    res = table.scan()
    values = res.get('Items', [])
    data = pd.DataFrame(values)
    data.sort_values(by=['uniqueid'], inplace=True)
    return int(data.uniqueid.max())


def initDatabase(isFS=True):
    bucket = 'tv-freecycle'
    if isFS:
        csvfile = 'fslist/freecycle-data.csv'
    else:
        csvfile = 'tslist/toycycle-data.csv'
    tmpfile = os.path.join(os.getenv('TMP'), 'fsraw.csv')
    s3 = boto3.client('s3')
    s3.download_file(bucket, csvfile, tmpfile)
    dataset = pd.read_csv(tmpfile)
    dataset.fillna(value='', inplace=True)
    uniqueid=0
    for _, data in dataset.iterrows():
        phno = str(data['contact_p'])
        if phno[0] != '0':
            phno = '0' + phno
        uniqueid = uniqueid + 1
        idstr = f'{uniqueid:09d}'
        print(data['recDt'])
        dtval = datetime.datetime.strptime(str(data['recDt']), '%Y%m%d%H%M%S')
        expdate = int((dtval + datetime.timedelta(days=50)).timestamp())
        newdata = {'uniqueid': idstr, 'recType': data['Type'], 
                   'Item': data['Item'], 'description':data['Description'], 'price': str(data['Price']), 
                   'contact_n': data['Contact_n'], 'contact_p': phno, 'contact_e': data['Contact_e'],
                   'url1': data['url1'], 'url2': data['url2'], 'url3': data['url3'], 
                   'isdeleted': data['deleted'], 'created': str(data['recDt']), 'expirydate': expdate}
        print(newdata)
        addRow(newdata=newdata)
    return 
