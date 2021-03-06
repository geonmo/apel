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

import re,datetime,logging
log = logging.getLogger(__name__)

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
        "cms-t2-ce01.sdfarm.kr#2.0#1492418148|3.0|geonmo|/C=KR/O=KISTI/O=GRID/O=KISTI/CN=58079576
Geonmo Ryu|/cms/Role=NULL/Capability=NULL|cms|1|0|0|1492418156|1492418167|0|100|1|"
        ['cms-t2-ce01.sdfarm.kr#2.0#1492418148', '3.0', 'geonmo',
        '/C=KR/O=KISTI/O=GRID/O=KISTI/CN=58079576 Geonmo Ryu', '/cms/Role=NULL/Capability=NULL',
        'cms', '1', '0', '0', '1492418156', '1492418167', '0', '100', '1', '']

        '''
        values = line.strip().split('|')
        dateinfo = datetime.datetime.fromtimestamp(float(values[9]))
        dates = dateinfo.isoformat(' ')
        mapping = {
            'TimeStamp'      : lambda x: 'T'.join(dates.split())+'Z',
            'VO'             : lambda x: parse_fqan( x[5])[2],
            'VOGroup'        : lambda x: parse_fqan( x[5])[1],
            'VORole'         : lambda x: parse_fqan( x[5])[0],
            'FQAN'           : lambda x: x[3],
            'CE'             : lambda x: self.machine_name + ":" + "9619" + "/" + self.machine_name + "-" + "condor",
            'GlobalUserName' : lambda x: x[3],
            'GlobalJobId'    : lambda x: x[0],
            'LrmsId'         : lambda x: x[1]+'.'+self.machine_name,
            'Site'           : lambda x: self.site_name,
            'ValidFrom'      : lambda x: valid_from(dateinfo),
            'ValidUntil'     : lambda x: valid_until(dateinfo),
            'Processed'      : lambda x: Parser.UNPROCESSED
        }
        rc = {}

        for key in mapping:
            rc[key] = mapping[key](values)
            #print key, rc[key]

        record = HTCondorCERecord()
        record.set_all(rc)
        return record
