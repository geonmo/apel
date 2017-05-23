'''
   Copyright (C) 2012 STFC

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

A parser for HTCondorCE record file.

    @author: Jordi Casals modified Blahd from Konrad Jopek
'''

from apel.db.records.htcondorce import HTCondorCERecord
from apel.common import valid_from, valid_until, parse_timestamp
from apel.common.parsing_utils import parse_fqan
from apel.parsers import Parser

import re,datetime

class HTCondorCEParser(Parser):
    '''
    HTCondorCE parses accounting files from HTCondorCE system.
    '''
    def __init__(self, site, machine_name, mpi) :
        Parser.__init__(self, site, machine_name, mpi)
        log.info('Site: %s; batch system: %s'%(self.site_name, self.machine_name))
    def parse(self, line):
        '''
        Parses single line from accounting log file.

        Example line of accounting log file:
        "cms-t2-ce01.sdfarm.kr#2.0#1492418148|geonmo|/C=KR/O=KISTI/O=GRID/O=KISTI/CN=58079576 Geonmo Ryu|/C=KR/O=KISTI/O=GRID/O=KISTI/CN=58079576 Geonmo Ryu,/cms/Role=NULL/Capability=NULL,/cms/uscms/Role=NULL/Capability=NULL|1|0|0|1492418156|1492418167|0|100|1|"
        Line was split, if you want to rejoin use ' ' as a joiner.
        '''
        values = line.strip().split('|')
        dates = datetime.datetime.fromtimestamp(values[9]).isoformat()
        mapping = {
            'TimeStamp'      : lambda x: dates+'Z',
            'GlobalUserName' : lambda x: x[2],
            'FQAN'           : lambda x: x[4].split(',')[1],
            'VO'             : lambda x: x[5],
            'VOGroup'        : lambda x: x[5],
            'VORole'         : lambda x: x[4].split(',')[1].split("/")[2].split('=')[-1]
            'CE'             : lambda x: self.machine_name + ":" + "9619" + "/" + self.machine_name + "-" + "condor",
            'GlobalJobId'    : lambda x: x[0],
            'LrmsId'         : lambda x: x[1]+'.'+self.machine_name,
            'Site'           : lambda x: self.site_name,
            'ValidFrom'      : lambda x: valid_from(dates),
            'ValidUntil'     : lambda x: valid_until(dates),
            'Processed'      : lambda x: Parser.UNPROCESSED
        }
        rc = {}

        for key in mapping:
            rc[key] = mapping[key](values)

        record = HTCondorCERecord()
        record.set_all(rc)
        return record
