# Beb-manager task tracker #

## What is **Beb manager**? ##

Beb-manager is a simple task tracker library and CLI application written on Python 3. It enables you to to create cards with tasks, group them and assign to other users with different access types.

## Installation guide ##

### Clone the repo ###

```bash
$ git clone https://github.com/GLinnik21/BEBManager.git
```

### Install the library ###
CLI application requires *beb_lib* library.
Before installation run test:

```bash
$ cd beb-manager/library
$ python3 setup.py test
```

After that you may install the library itself:

```bash
$ python3 setup.py install
```

After installation you may import library in Python shell:

```python
import beb_lib
```

### Install CLI application ###

```bash
$ cd beb-manager/cli
$ python3 setup.py install
```

## Supported commands ##

### Usage ###

After installation you may use **Beb manager** from the command line as follows:

```bash
$ beb-manager
usage: beb-manager [-h] <object> ...
beb-manager: error: the following arguments are required: <object>
```

All commands in **Beb manager** are built like this:

```bash
$ beb-manager <object> <command> [options]
```

All available objects may be seen with the following command:

```bash
$ beb-manager -h
usage: beb-manager [-h] <object> ...

Achieve your goals with Beb manager issues tracker

optional arguments:
  -h, --help  show this help message and exit

available objects are:
  <object>
    user      Operate users. Users may own and have different access to cards,
              lists, etc.
    board     Operate boards. Boards contain lists of cards
    list      Operate list. Lists contain cards
    card      Operate cards. Cards are the basic structure that's meant to
              represent one task
    tag       Operate tags. Tags are used to group tasks even from different
              lists
```

### User ###

All actions in Beb manager have to be performed under the certain user.

Creating user:

```bash
$ beb-manager user add "Username"
```

Switching to the user:

```bash
$ beb-manager user login -n "Username"
```

### Board ###

Same as with user. All actions with lists and cards have to be performed on certain board.

Creating a board:

```bash
$ beb-manager board add "Board name"
```

Switching to board with id 1:

```bash
$ beb-manager board switch 1
```

### List ###

By default, all boards are created with 3 standard lists:

```bash
$ beb-manager list show -a
BoardID: 1   Name: Board name

Lists in this board:
ListID: 2   Name: To Do
ListID: 3   Name: In Progress
ListID: 4   Name: Done
```

They may be easily modified as follows:

```bash
$ beb-manager list edit 2 -n "Has to be done"
$ beb-manager list show -a
BoardID: 1   Name: New board

Lists in this board:
ListID: 2   Name: Has to be done
ListID: 3   Name: In Progress
ListID: 4   Name: Done
```

Adding a new list:

```bash
$ beb-manager list add "New list"
```

### Card ###

Cards are stored in lists, so you have to specify the name or id of the list where the new card would be created

```bash
$ beb-manager card add "Buy flowers" -ln "Has to be done"
```

To create a periodical card, use the following arguments:

```bash
$ beb-manager card add "Water flowers" -ln "Has to be done" -r "1 week" -sa "in 3 days"
```

### Tag ###

Tags are used to group tasks even from different lists.

Creating a tag:

```bash
$ beb-manager tag add Red
```

Adding the tag to the card:

```bash
$ beb-manager card edit 2 -at Red
```

Viewing cards with the certain tag:

```bash
$ beb-manager tag show -n Red
┌───────────────────────────────────────────┐
│CardID: 2   Name: Water flowers            │
│Priority: MEDIUM                           │
│Owner: 1 aka Username                      │
│Tags: ['Red']                              │
│Created: Sun Sep  9 23:51:01 2018          │
│Modified: Sun Sep  9 23:58:49 2018         │
│┌─────────────────────────────────────────┐│
││Periodical task plan                     ││
││Repeats every: 1 day, 0:00:00            ││
││Last created at: Sun Sep  9 23:19:40 2018││
│└─────────────────────────────────────────┘│
└───────────────────────────────────────────┘
```
