# this class will inherit from hardware_service.py and overwrite all of its methods
# with hil-specific behaviors - mostly through api calls to the HIL server

from datetime import datetime
import calendar
import time
import yaml
import argparse
import os
import sys
import requests
import logging
import json
from subprocess import call
from subprocess import check_call

from hardware_services.network_service import NetworkService
from hardware_services.util import hilapi

class HilNetworkDriver(NetworkService):

    def __read_current_state(self, argv):
        """
        Reads actual current network of a node from the HIL database and returns name of this network
        """
        
        pass

    def __write_current_state(self, argv):
        """
        Writes/updates information about a new network of a node to the HIL database
        """
        
        pass
        
    def __move_one_host(self, host_to_move, old_cloud, new_cloud):
        node_nics = hilapi.show_node(host_to_move)['nics']
        if _DEBUG > 0:
            print("TESTING: Before move " + str(node_nics))
        for nic_json in node_nics:
            
            time.sleep(1)
            hilapi.node_detach_network(host_to_move,
                                nic_json['label'],
                                old_cloud)
            time.sleep(1)

            time.sleep(1)
            hilapi.node_connect_network(host_to_move,
                                nic_json['label'],
                                new_cloud,
                                'null')
            time.sleep(1)

        node_nics = hilapi.show_node(host_to_move)['nics']
        if _DEBUG > 0:
            print("TESTING: After move " + str(node_nics))    
    

    def move_hosts(self, quadsinstance, **kwargs):
        # move a host
        for h in sorted(quadsinstance.quads.hosts.data.iterkeys()):
            default_cloud, current_cloud, current_override = quadsinstance._quads_find_current(h, kwargs['datearg'])
            # make sure data in the HIL database is up to date
            quadsinstance.quads_sync_state()
            # read data from the HIL database
            current_state = self.__read_current_state(h)
            
            if current_state != current_cloud:
                quadsinstance.logger.info("Moving " + h + " from " + current_state + " to " + current_cloud)
                if not kwargs['dryrun']:
                    try:
                        self.__move_one_host(h, current_state, current_cloud)
                    except Exception, ex:
                        quadsinstance.logger.error("Move command failed: %s" % ex)
                        exit(1)
                    # change network of the node to the correct one in the HIL database
                    self.__write_current_state(h)
        return





