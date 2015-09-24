# -*- coding: utf-8 -*-

__author__ = 'my'

"""
LAA1_downloader.py
Created on Fri Sep 23 10:05:48 2015

@author: G
"""

import sys
import urllib
import pandas as pd
import re
import argparse
import json

# url = "https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/418385/SFR_11-2015-Tables_16-24.xlsx"
# output_path = "tempAchGap.csv"
# sheet = "Table16a"
# required_indicators = ["2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014"]


def download(url, sheet, reqFields, outPath):
    yearReq = reqFields
    dName = outPath

    col = ['ecode', 'name', 'year', 'value']

    try:
        socket = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        sys.exit('excel download HTTPError = ' + str(e.code))
    except urllib.error.URLError as e:
        sys.exit('excel download URLError = ' + str(e.args))
    except Exception:
        print('excel file download error')
        import traceback

        sys.exit('generic exception: ' + traceback.format_exc())

    # operate this excel file
    xd = pd.ExcelFile(socket)
    df = xd.parse(sheet)

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
        sys.exit("Requested data " + str(yearReq).strip(
            '[]') + " don't match the excel file. Please check the file at: " + url)

    raw_data = {}
    for j in col:
        raw_data[j] = []

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

    # save csv file
    print('writing to file ' + dName)
    dfw = pd.DataFrame(raw_data, columns=col)
    dfw.to_csv(dName, index=False)
    print('Requested data has been extracted and saved as ' + dName)
    print("finished")


parser = argparse.ArgumentParser(description='Extract online Achievement Gap Excel file Table16a to .csv file.')
parser.add_argument("--generateConfig", "-g", help="generate a config file called config_Alevels.json",
                    action="store_true")
parser.add_argument("--configFile", "-c", help="path for config file")
args = parser.parse_args()

if args.generateConfig:
    obj = {
        "url": "https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/418385/SFR_11-2015-Tables_16-24.xlsx",
        "outPath": "tempAchGap.csv",
        "sheet": "Table16a",
        "reqFields": ["2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014"]
    }

    with open("config_AchGap.json", "w") as outfile:
        json.dump(obj, outfile, indent=4)
        sys.exit("config file generated")

if args.configFile == None:
    args.configFile = "config_AchGap.json"

with open(args.configFile) as json_file:
    oConfig = json.load(json_file)
    print("read config file")

download(oConfig["url"], oConfig["sheet"], oConfig["reqFields"], oConfig["outPath"])
