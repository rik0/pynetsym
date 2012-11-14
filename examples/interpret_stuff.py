import os
from plfit import plfit
from numpy import dtype, loadtxt
import numpy

print os.getcwd()

#PDF_FILE = 'no_sync_clock_no_sync_agent_1352849705/pdf.csv'
#CCDF_FILE = 'no_sync_clock_no_sync_agent_1352849705/ccdf.csv'
#
#data_record = dtype([('nodes', float), ('ab', float), ('nx', float)])
#
#PDF_DATA = loadtxt(PDF_FILE, dtype=data_record,
#                   skiprows=11, delimiter=',')
#
#CCDF_DATA = loadtxt(CCDF_FILE, dtype=data_record,
#                   skiprows=11, delimiter=',')


FILE_NAME = 'no_sync_clock_1352885864/raw_degrees.csv'
RAW_DEGREES = loadtxt(FILE_NAME, dtype=float)

print plfit(RAW_DEGREES.astype(int).tolist())