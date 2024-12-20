import sys
import socket
try:
    from configparser import ConfigParser
except:
    from configparser import ConfigParser

from .constants import DEFAULT_BUFFER_SIZE
from .log import logmsg, logerr

class LoadBalancerMapping(object):
    '''
        Represents a mapping of a local listen to a series of workers
    '''

    def __init__(self, localAddr, localPort, workers):
        self.localAddr = localAddr or ''
        self.localPort = int(localPort)
        self.workers = workers

    def getListenerArgs(self):
        return [self.localAddr, self.localPort, self.workers]

    def addWorker(self, workerAddr, workerPort):
        self.workers.append({'port': int(workerPort), 'addr': workerAddr})

    def removeWorker(self, workerAddr, workerPort):
        newWorkers = []
        workerPort = int(workerPort)
        removedWorker = None
        for worker in self.workers:
            if worker['addr'] == workerAddr and worker['port'] == workerPort:
                removedWorker = worker
                continue
            newWorkers.append(worker)
        self.workers = newWorkers

        return removedWorker

class LoadBalancerConfig(ConfigParser):
    '''
        The class for managing LoadBalancer's Config File
    '''

    
    def __init__(self, configFilename):
        ConfigParser.__init__(self)
        self.configFilename = configFilename

        self._options = {
            'pre_resolve_workers': True,
            'buffer_size': DEFAULT_BUFFER_SIZE,
        }
        self._mappings = {}

    def parse(self):
        '''
            Parse the config file
        '''
        try:
            f = open(self.configFilename, 'rt')
        except IOError as e:
            logerr('Could not open config file: "%s": %s\n' % (self.configFilename, str(e)))
            raise e
        [self.remove_section(s) for s in self.sections()]
        self.read_file(f)
        f.close()

        self._processOptions()
        self._processMappings()

    def getOptions(self):
        '''
            Gets the options dictionary
        '''
        return self._options

    def getOptionValue(self, optionName):
        '''
            getOptionValue - Gets the value of an option
        '''

        return self._options[optionName]

    def getMappings(self):
        '''
            Gets the mappings dictionary
        '''
        return self._mappings

    def _processOptions(self):
        # I personally think the config parser interface sucks...
        if 'options' not in self._sections:
            return

        try:
            bufferSize = self.get('options', 'buffer_size')
            if bufferSize.isdigit() and int(bufferSize) > 0:
                self._options['buffer_size'] = int(bufferSize)
            else:
                logerr('WARNING: buffer_size must be an integer > 0 (bytes). Got "%s" -- ignoring value, retaining previous "%s"\n' % (bufferSize, str(self._options['buffer_size'])))
        except Exception as e:
            logerr('Error parsing [options]->buffer_size : %s. Retaining default, %s\n' % (str(e), str(DEFAULT_BUFFER_SIZE)))

        try:
            algorithm = self.get('options', 'algorithm')
            if algorithm in ['random', 'round_robin', 'weighted_round_robin']:  # Include 'weighted_round_robin'
                self._options['algorithm'] = algorithm
            else:
                logerr(f'WARNING: Unknown algorithm "{algorithm}". Defaulting to "random".\n')
                self._options['algorithm'] = 'random'  # Default to random if invalid
        except:
            self._options['algorithm'] = 'random'  # Default if option is missing



    def _processMappings(self):
        if 'mappings' not in self._sections:
            raise LoadBalancerConfigException('ERROR: Config is missing required "mappings" section.\n')

        preResolveWorkers = self._options['pre_resolve_workers']

        mappings = {}
        mappingSectionItems = self.items('mappings')
        
        for (addrPort, workers) in mappingSectionItems:
            addrPortSplit = addrPort.split(':')
            addrPortSplitLen = len(addrPortSplit)
            if not workers:
                logerr('WARNING: Skipping, no workers defined for %s\n' % (addrPort,))
                continue
            if addrPortSplitLen == 1:
                (localAddr, localPort) = ('0.0.0.0', addrPort)
            elif addrPortSplitLen == 2:
                (localAddr, localPort) = addrPortSplit
            else:
                logerr('WARNING: Skipping Invalid mapping: %s=%s\n' % (addrPort, workers))
                continue
            try:
                localPort = int(localPort)
            except ValueError:
                logerr('WARNING: Skipping Invalid mapping, cannot convert port: %s\n' % (addrPort,))
                continue

            workerLst = []
            for worker in workers.split(','):
                workerSplit = worker.split(':')
                if len(workerSplit) < 2:
                    logerr('WARNING: Skipping Invalid Worker %s\n' % (worker,))

                if preResolveWorkers is True:
                    try:
                        addr = socket.gethostbyname(workerSplit[0])
                    except:
                        logerr('WARNING: Skipping Worker, could not resolve %s\n' % (workerSplit[0],))
                else:
                    addr = workerSplit[0]

                try:
                    port = int(workerSplit[1])
                except ValueError:
                    logerr('WARNING: Skipping worker, could not parse port %s\n' % (workerSplit[1],))

                # If weight is not specified, default to 1
                weight = int(workerSplit[2]) if len(workerSplit) > 2 else 1

                workerLst.append({'addr': addr, 'port': port, 'weight': weight})

            keyName = "%s:%s" % (localAddr, addrPort)
            if keyName in mappings:
                logerr('WARNING: Overriding existing mapping of %s with %s\n' % (addrPort, str(workerLst)))
            mappings[addrPort] = LoadBalancerMapping(localAddr, localPort, workerLst)

        self._mappings = mappings




class LoadBalancerConfigException(Exception):
    pass

# vim: ts=4 sw=4 expandtab