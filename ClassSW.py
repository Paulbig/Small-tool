from __future__ import print_function
from ClassConnect import *
from collections import OrderedDict
import re
import Source as s


def deco_Exception(func):
    def _deco(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as E:
            print(self._host, func.__name__, E)
    return _deco


class SANSW(object):
    def __init__(self, strIP, intPort, strUserName, strPasswd,
                 lstSWPort, intTimeout=2):
        self._host = strIP
        self._port = intPort
        self._username = strUserName
        self._password = strPasswd
        self._timeout = intTimeout
        self._allSWPort = lstSWPort
        self._strAllPortError = None
        self._dicPartPortError = None
        self._SWConn = None
        self._getporterrshow()
        self._PutErrorToDict()

    @deco_Exception
    def _getporterrshow(self):
        try:
            self._SWConn = SSHConn(self._host,
                                   self._port,
                                   self._username,
                                   self._password,
                                   self._timeout)
            self._strAllPortError = self._SWConn.exctCMD(
                'porterrshow')
            return True
        except Exception as E:
            s.ShowErr(self.__class__.__name__,
                      sys._getframe().f_code.co_name,
                      'Get PortErrorInfo for "{}" Fail with Error:'.format(
                          self._host),
                      '"%s"' % E)

    @deco_Exception
    def _PutErrorToDict(self):
        def _portInLine(intSWPort, strLine):
            lstLine = strLine.split()
            if (str(intSWPort) + ':') in lstLine:
                return True

        def _getErrorAsList(intPortNum, lstPortErrLines):
            for portErrLine in lstPortErrLines:
                if _portInLine(intPortNum, portErrLine):
                    reDataAndErr = re.compile(
                        r'(.*:)((\s+\S+){2})((\s+\S+){6})((\s+\S+){5})(.*)')
                    resultDataAndErr = reDataAndErr.match(portErrLine)
                    return(resultDataAndErr.group(2).split() +
                           resultDataAndErr.group(6).split())

        def _putToDict():
            oddPortError = OrderedDict()
            lstPortErrLines = str(self._strAllPortError).split('\n')
            for intPortNum in self._allSWPort:
                lstErrInfo = _getErrorAsList(intPortNum, lstPortErrLines)
                oddPortError[intPortNum] = lstErrInfo
            self._dicPartPortError = oddPortError

        if self._strAllPortError:
            _putToDict()

    @deco_Exception
    def _porterrshow(self):
        if self._strAllPortError:
            print('Porterrshow for SAN Switch {}:\n'.format(self._host))
            print(self._strAllPortError)

    @deco_Exception
    def _switchshow(self):
        if self._SWConn:
            try:
                print('Switchshow for SAN Switch {}:\n'.format(self._host))
                print(self._SWConn.exctCMD('switchshow'))
            except Exception as E:
                pass

    @deco_Exception
    def get_linkfail_by_port(self, intSWPort):
        if self._dicPartPortError:
            if intSWPort in self._dicPartPortError.keys():
                return self._dicPartPortError[intSWPort][4]
            else:
                return 'Please Correct the Port Number...'

    @deco_Exception
    def get_encout_by_port(self, intSWPort):
        if self._dicPartPortError:
            if intSWPort in self._dicPartPortError.keys():
                return self._dicPartPortError[intSWPort][2]
            else:
                print('Please Correct the Port Number...')

    @deco_Exception
    def get_discC3_by_port(self, intSWPort):
        if self._dicPartPortError:
            if intSWPort in self._dicPartPortError.keys():
                return self._dicPartPortError[intSWPort][3]
            else:
                print('Please Correct the Port Number...')

    @deco_Exception
    def get_encout_total(self):
        def _get_count():
            int_encoutTotal = 0
            for i in self._dicPartPortError:
                if 'k' in self._dicPartPortError[i][2]:
                    return 'Over Thousand Errors of encout detected...'
                elif 'm' in self._dicPartPortError[i][2]:
                    return 'Over Million Errors of encout detected...'
                int_encoutTotal += int(self._dicPartPortError[i][2])
            return int_encoutTotal
        if self._dicPartPortError:
            return _get_count()

    @deco_Exception
    def get_discC3_total(self):
        def _get_count():
            int_encoutTotal = 0
            for i in self._dicPartPortError:
                if 'k' in self._dicPartPortError[i][3]:
                    return 'Over Thousand Errors of encout detected...'
                elif 'm' in self._dicPartPortError[i][3]:
                    return 'Over Million Errors of encout detected...'
                int_encoutTotal += int(self._dicPartPortError[i][3])
            return int_encoutTotal
        if self._dicPartPortError:
            return _get_count()

    # @deco_Exception
    def clear_porterr_All(self):
        try:
            self._SWConn.exctCMD('statsclear')
            print('Clear Error Count for SW "{}" Completely...'.format(
                self._host))
            return True
        except Exception as E:
            print('Clear Error Count for SW "{}" Failed...'.format(self._host))

    @deco_Exception
    def clear_porterr_by_port(self, intSWPort):
        try:
            self._SWConn.exctCMD(
                'portstatsclear {}'.format(str(intSWPort)))
            print('Clear Error Count of Port {} for SW "{}" Completely...\
                '.format(str(intSWPort), self._host))
            return True
        except Exception as E:
            print('Clear Error Count Failed...')

    @deco_Exception
    def show_porterrors(self):
        def _show_porterrors():
            lstDesc = ['PortID', 'FramTX', 'FramRX', 'encout',
                       'Discc3', 'LinkFL', 'LossSC', 'LossSG']
            for strDesc in lstDesc:
                print(strDesc.center(8), end='')
            print()
            for intPort in self._dicPartPortError:
                print(str(intPort).center(8), end='')
                for strPortErr in self._dicPartPortError[intPort]:
                    print(strPortErr.center(8), end='')
                print()
        if self._dicPartPortError:
            print('\nThe Ports Errors of SAN Switch {} ...'.format(self._host))
            _show_porterrors()
            
    #获取交换机数据      
    def infoSwitch_lst(self):
        ip = self._host
        discC3 = self.get_discC3_total
        
        
        encout = self.get_encout_total
    
        
        
        return [ip,discC3,encout]
    

if __name__ == '__main__':
    pass
