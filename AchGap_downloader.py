__author__ = 'G'

import sys
sys.path.append('../harvesterlib')

import pandas as pd
import re
import argparse
import json

import now
import openurl
import datasave as dsave


# url = "https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/418385/SFR_11-2015-Tables_16-24.xlsx"
# output_path = "tempAchGap.csv"
# sheet = "Table16a"
# required_indicators = ["2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014"]


def download(url, sheet, reqFields, outPath, col, keyCol, digitCheckCol, noDigitRemoveFields):
    yearReq = reqFields
    dName = outPath

    # open url
    socket = openurl.openurl(url, logfile, errfile)

    # operate this excel file
    logfile.write(str(now.now()) + ' excel file loading\n')
    print('excel file loading------')
    xd = pd.ExcelFile(socket)
    df = xd.parse(sheet)

    # indicator checking
    logfile.write(str(now.now()) + ' indicator checking\n')
    print('indicator checking------')
    for i in range(df.shape[0]):
        yearCol = []
        for k in yearReq:
            kk = []
            k_asked = "19 in " + k[2:]
            for j in range(df.shape[1]):
                if df.iloc[i, j] == k_asked:
                    kk.append(j)
                    restartIndex = i + 1

            if len(kk) == 4:
                yearCol.append(kk[3])

        if len(yearCol) == len(yearReq):
            break

    if len(yearCol) != len(yearReq):
        errfile.write(str(now.now()) + " Requested data " + str(yearReq).strip(
            '[]') + " don't match the excel file. Please check the file at: " + str(url) + " . End progress\n")
        logfile.write(str(now.now()) + ' error and end progress\n')
        sys.exit("Requested data " + str(yearReq).strip(
            '[]') + " don't match the excel file. Please check the file at: " + url)

    raw_data = {}
    for j in col:
        raw_data[j] = []

    # data reading
    logfile.write(str(now.now()) + ' data reading\n')
    print('data reading------')
    for i in range(restartIndex, df.shape[0]):
        if re.match(r'E\d{8}$', str(df.iloc[i, 0])):
            ii = 0
            for j in range(len(yearCol)):
                raw_data[col[0]].append(df.iloc[i, 0])
                raw_data[col[1]].append(df.iloc[i, 2])
                raw_data[col[2]].append(yearReq[ii])
                raw_data[col[3]].append(df.iloc[i, yearCol[ii]])
                ii += 1
    logfile.write(str(now.now()) + ' data reading end\n')
    print('data reading end------')

    # save csv file
    dsave.save(raw_data, col, keyCol, digitCheckCol, noDigitRemoveFields, dName, logfile)


parser = argparse.ArgumentParser(description='Extract online Achievement Gap Excel file Table16a to .csv file.')
parser.add_argument("--generateConfig", "-g", help="generate a config file called config_tempAchGap.json",
                    action="store_true")
parser.add_argument("--configFile", "-c", help="path for config file")
args = parser.parse_args()

if args.generateConfig:
    obj = {
        "url": "https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/418385/SFR_11-2015-Tables_16-24.xlsx",
        "outPath": "tempAchGap.csv",
        "sheet": "Table16a",
        "reqFields": ["2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014"],
        "colFields": ['ecode', 'name', 'year', 'value'],
        "primaryKeyCol": ['ecode', 'year'],#[0, 2],
        "digitCheckCol": ['value'],#[3],
        "noDigitRemoveFields": []
    }

    logfile = open("log_tempAchGap.log", "w")
    logfile.write(str(now.now()) + ' start\n')

    errfile = open("err_tempAchGap.err", "w")

    with open("config_tempAchGap.json", "w") as outfile:
        json.dump(obj, outfile, indent=4)
        logfile.write(str(now.now()) + ' config file generated and end\n')
        sys.exit("config file generated")

if args.configFile == None:
    args.configFile = "config_tempAchGap.json"

with open(args.configFile) as json_file:
    oConfig = json.load(json_file)

    logfile = open('log_' + oConfig["outPath"].split('.')[0] + '.log', "w")
    logfile.write(str(now.now()) + ' start\n')

    errfile = open('err_' + oConfig["outPath"].split('.')[0] + '.err', "w")

    logfile.write(str(now.now()) + ' read config file\n')
    print("read config file")

download(oConfig["url"], oConfig["sheet"], oConfig["reqFields"], oConfig["outPath"], oConfig["colFields"], oConfig["primaryKeyCol"], oConfig["digitCheckCol"], oConfig["noDigitRemoveFields"])
