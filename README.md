# InfluxDB bandwidth checks for icinga2

This repo contains an Icinga plugin scripts for checking bandwidth metrics stored in InfluxDB.

To give a little context, those metrics are issued from network devices with SNMP.
Among other they are absolute in and out interfaces bytes counters.

Telegraf is used to retrieve and push the metrics.

The [Influx derivative function](https://docs.influxdata.com/influxdb/v1.7/query_language/functions/#derivative) gives ability to compute a rate of changes which give an amount of bytes per unit of time which are converted in bits per second (bps) in the derivative compute. 

## Requirements

This checks depends on the following python modules:
 * requests
 * argparse

## Usage

Edit the `in_bps` and `out_bps` requests to match your series and tag names.

`-s SPEED` MUST be given in Mbps

Optional parameters are `[-i INTERVAL] [-db DATABASE] [-w WARN] [-c CRIT]`

The thresholds `-w WARN` or `-c CRIT` MUST be given in Influx time format.


### check_influx_bw.py

```
check_influx_bw.py [-h] -H HOST -u USERNAME -p PASSWORD -if IFALIAS -a AGENT_HOST -s SPEED [-t TIME] [-i INTERVAL] [-db DATABASE] [-w WARN] [-c CRIT]

arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST
  -u USERNAME, --username USERNAME
  -p PASSWORD, --passwd PASSWORD
  -if IFALIAS, --ifAlias IFALIAS
  -a AGENT_HOST, --agent_host AGENT_HOST
  -s SPEED, --speed SPEED
  -t TIME, --time TIME
  -i INTERVAL, --interval INTERVAL
  -db DATABASE, --database DATABASE
  -w WARN, --warn WARN
  -c CRIT, --crit CRIT
```

### Example

```
./check_influx_bw.py -H influx.example.fr -u user -p secret -if CORE-INTERFACE:0/3/0 -a my-core-router.example.fr -s 1000 -i 5m
Input bandwidth usage is OK - 5.74Mbps use of 1000Mbits at 2019-06-14T09:55:00Z.
Input bandwidth usage is OK - 6.38Mbps use of 1000Mbits at 2019-06-14T10:00:00Z.
Output bandwidth usage is OK - 8.55Mbps use of 1000Mbits at 2019-06-14T09:55:00Z.
Output bandwidth usage is OK - 9.50Mbps use of 1000Mbits at 2019-06-14T10:00:00Z.

```

## Authors

* **Guillaume Noale** - *Initial work* - [Gnoale](https://github.com/Gnoale)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


## Acknowledgments
Inspired from https://github.com/miso231/icinga2-cloudera-plugin

