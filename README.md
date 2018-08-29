# Beb-manager task tracker #

## What is **Beb manager**? ##

Beb-manager is a simple task tracker library and CLI application written on Python 3. It enables you to to create cards with tasks, group them and assign to other users with different access types.

## Installation guide ##

### Clone the repo ###

```bash
$ git clone git@bitbucket.org:GLinnik/isp.git
```

### Install the library ###
CLI application requires *beb_lib* library:

```bash
$ cd beb-manager/library
$ python3 setup.py install
```

After installation you may import library in Python shell:

```python
import beb_lib
```

### Install CLI application

```bash
$ cd beb-manager/cli
$ python3 setup.py install
```

After that you may use **Beb manager** from the command line as follows:

```bash
$ beb-manager
usage: beb-manager [-h] <object> ...
beb-manager: error: the following arguments are required: <object>
```
