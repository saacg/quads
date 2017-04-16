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
import urllib
from subprocess import call
from subprocess import check_call
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from libquads import Quads

from hardware_services.inventory_service import InventoryService

# added for EC528 HIL-QUADS integration project
hil_url = 'http://127.0.0.1:5000'

class HilInventoryDriver(InventoryService):


    def update_cloud(self, quadsinstance, **kwargs):
        self.__project_create(quadsinstance.hardware_service_url, kwargs['cloudresource'])
        self.__project_create_network(quadsinstance.hardware_service_url, kwargs['cloudresource'])


    def update_host(self, quadsinstance, **kwargs):
        quadsinstance.quads_rest_call('POST', hil_url, '/project/' + kwargs['hostcloud'] + '/connect_node', json.dumps({'node': kwargs['hostresource']}))
        node_info = quadsinstance.quads_rest_call('GET', hil_url, '/node/' + kwargs['hostresource'])
        node = node_info.json()
        for nic in node['nics']:        # a node in quads will only have one nic per network
            quadsinstance.quads_rest_call('POST', hil_url, '/node/' + kwargs['hostresource'] + '/nic/' + nic['label'] + '/connect_network', json.dumps({'network': kwargs['hostcloud']}))



    def remove_cloud(self, quadsinstance, **kwargs):
        cloud = kwargs['rmcloud']
        #quadsinstance.quads_rest_call("DELETE", hil_url, '/network/'+ targetProject)
        #quadsinstance.quads_rest_call("DELETE", hil_url, '/project/'+ targetProject)
        self.__network_delete(quadsinstance.hardware_service_url, cloud)
        self.__project_delete(quadsinstance.hardware_service_url, cloud)


    def remove_host(self,quadsinstance, **kwargs):
        # first detach host from network
        node_info = quadsinstance.quads_rest_call('GET', hil_url, '/node/' + kwargs['rmhost'])
        node = node_info.json()
        for nic in node['nics']:        # a node in quads will only have one nic per network
            quadsinstance.quads_rest_call('POST', hil_url, '/node/' + kwargs['rmhost'] + '/nic/' + nic['label'] + '/detach_network', json.dumps({'network': node['project']}))


    def list_clouds(self, quadsinstance):
        #projects = quadsinstance.quads_rest_call("GET", hil_url, '/projects')
        #print projects.text
        print self.__list_projects(quadsinstance.hardware_service_url).text


    def list_hosts(self, quadsinstance):
        #hosts = quadsinstance.quads_rest_call("GET", hil_url, '/nodes/all')
        #hosts_yml = yaml.dump(json.loads(hosts.text), default_flow_style=False)
        hosts = self.__list_nodes(quadsinstance.hardware_service_url)
        print hosts.text


    def load_data(self, quads, force):
        """
        """

    def init_data(self, quads, force):
        """
        """

    def sync_state(self, quads):
        """
        """

    def write_data(self, quads, doexit = True):
        """
        """

    ######################################################################################################
    # the following private methods are based on the HIL cli and are wrappers for the hil rest api calls #
    ######################################################################################################

    def __list_projects(self, hil_url):
        url = Quads.quads_urlify(hil_url, 'projects')
        return Quads.quads_get(url)


    def __project_create_network(self, hil_url, project):
        """ creates network belonging to project of the same name """

        url = Quads.quads_urlify(hil_url, 'network', project)
        Quads.quads_put(url, data={'owner': project,
                              'access': project,
                              'net_id': ""})

    def __project_connect_node(self, hil_url, project, node):
        url = Quads.quads_urlify(hil_url, 'project', project, 'connect_node')
        Quads.quads_post(url, data={'node': node})


    def __network_delete(self, hil_url, network):
        url = Quads.quads_urlify(hil_url, 'network', network)
        Quads.quads_delete(url)


    def __project_create(self, hil_url, project):
        """ creates new project """
        url = Quads.quads_urlify(hil_url, 'project', project)
        Quads.quads_put(url)


    def __project_delete(self, hil_url, project):
        url = Quads.quads_urlify(hil_url, 'project', project)
        Quads.quads_delete(url)


    def __list_nodes(self, hil_url, is_free='all'):
        # if is_free is set to free, only lists unallocated nodes
        if is_free not in ('all', 'free'):
            sys.exit("error listing hosts. is_free is not set to all or free")
        url = Quads.quads_urlify(hil_url, 'nodes', is_free)
        return Quads.quads_get(url)





