# NIVIDIA GPU-Info to Beats

The objective of GPU-Info to Beats is get information of Nvidia GPU hardware like nvidia-smi command and send to ELK or Graylog, through Beats protocol. This project is based on another 2 projects.

- [NVIDIA GPU exporter](https://gist.github.com/ozancaglayan/40aaae8397edca78d9d473a3e1ef6e78)
- [PyLogBeat](https://github.com/eht16/pylogbeat)

# Installation

This project is write in Python 3.7 and you required library can installed with `pip` and his `requirements` file.

```buildoutcfg
pip3 install -U -r requirements
```

# Usage

To usage is simple, just pass some arguments.

`-- `