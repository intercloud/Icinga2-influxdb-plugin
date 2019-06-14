#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
import argparse
from decimal import Decimal


def build_parser():
    parser = argparse.ArgumentParser(description='Check bandwidth status')
    parser.add_argument('-H', '--host', type=str, required=True,  dest='host')
    parser.add_argument('-u', '--username', type=str, required=True,  dest='username')
    parser.add_argument('-p', '--passwd', type=str, required=True,  dest='password')
    parser.add_argument('-if', '--ifAlias', type=str, required=True, dest='ifAlias')
    parser.add_argument('-a', '--agent_host', type=str, required=True, dest='agent_host')
    parser.add_argument('-s', '--speed', type=int, required=True, dest='speed')
    parser.add_argument('-t', '--time', type=str, required=False, dest='time', default='10m')
    parser.add_argument('-i', '--interval', type=str, required=False, dest='interval', default='2m')
    parser.add_argument('-db', '--database', type=str, required=False, dest='database', default='network_metrics')
    parser.add_argument('-w', '--warn', type=int, required=False,  dest='warn', default=50)
    parser.add_argument('-c', '--crit', type=int, required=False,  dest='crit', default=80)
    return parser


def main():

    # provision args
    parser = build_parser()
    args = parser.parse_args()
    host = args.host
    password = args.password
    username = args.username
    ifAlias = args.ifAlias
    agent_host = args.agent_host
    speed = args.speed
    time = args.time
    interval = args.interval
    database = args.database
    warn = args.warn
    crit = args.crit


    # prepare request
    auth = requests.auth.HTTPBasicAuth(username, password)
    uri = 'https://{0}:8086/query'.format(host)
    in_bps = ("select non_negative_derivative(mean(ifHCInOctets),1s)*8 from interface_snmp where ifAlias::tag='{0}'"
               "and agent_host='{1}'and time > now() - {2} group by time({3})".format(ifAlias, agent_host, time, interval))
    out_bps = ("select non_negative_derivative(mean(ifHCOutOctets),1s)*8 from interface_snmp where ifAlias::tag='{0}'"
               "and agent_host='{1}'and time > now() - {2} group by time({3})".format(ifAlias, agent_host, time, interval))
    payload_in_bps = {'q':in_bps, 'db':database}
    payload_out_bps = {'q':out_bps, 'db':database}
    
    # if any exception report and return unknown state
    try:
        get_in_bps = requests.get(uri, params=payload_in_bps, auth=auth)
        get_out_bps = requests.get(uri, params=payload_out_bps, auth=auth)
    except Exception as e:
        print('Could not connect to InfluxDB server :', host, " - ", str(e))
        exit(3)
    
    # check for status code
    if get_in_bps.status_code != 200:
        print('Issue while request to InfluxDB server', host, str(get_in_bps.status_code), get_in_bps.text)
        exit(3)
    if get_out_bps.status_code != 200:
        print('Issue while request to InfluxDB server', host, str(get_out_bps.status_code), get_out_bps.text)
        exit(3)

    # store metrics
    ok_list = []
    warn_list = []
    crit_list = []
   
    try:

        # check the input bps metric
        for e in get_in_bps.json()['results'][0]['series'][0]['values']:
        
            mbps = round(Decimal(e[1]/1000000),2)

            if mbps >= (speed*crit/100):
                crit_list.append("Input bandwidth usage is CRITICAL - {0}Mbps use of {1}Mbits at {2}.".format(mbps, speed, e[0]))
            
            elif mbps >= (speed*warn/100):
                warn_list.append("Input bandwidth usage is WARNING - {0}Mbps use of {1}Mbits at {2}.".format(mbps, speed, e[0]))
            
            else: ok_list.append("Input bandwidth usage is OK - {0}Mbps use of {1}Mbits at {2}.".format(mbps, speed, e[0]))
    
        # check the output bps metric
        for e in get_out_bps.json()['results'][0]['series'][0]['values']:
       
            mbps = round(Decimal(e[1]/1000000),2)

            if mbps >= (speed*crit/100):
                crit_list.append("Output bandwidth usage is CRITICAL - {0}Mbps use of {1}Mbits at {2}.".format(mbps, speed, e[0]))
            
            elif mbps >= (speed*warn/100):
                warn_list.append("Output bandwidth usage is WARNING - {0}Mbps use of {1}Mbits at {2}.".format(mbps, speed, e[0]))
            
            else: ok_list.append("Output bandwidth usage is OK - {0}Mbps use of {1}Mbits at {2}.".format(mbps, speed, e[0]))
    
    except KeyError:
        print("The request didn't return any value")
        exit(3)
        
    # return states
    if len(crit_list) > 0:
        for e in crit_list:
            print(e)
        exit(2)
        
    elif len(warn_list) > 0:
        for e in warn_list:
            print(e)
        exit(1)
        
    elif len(ok_list) > 0:
        for e in ok_list:
            print(e)
        exit(0)

    else:
        print("Unknown exception occured")
        exit(3)

if __name__ == "__main__":
    main()
    sys.exit(0)
