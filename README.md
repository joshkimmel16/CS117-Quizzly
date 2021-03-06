# Quizzly

This is a quiz game that is facilitated by a server to up to 4 players. All connections are maintained via Bluetooth. A description of the repository structure and installation instructions can be found below.

## Repository Description

The following is a high-level overview of the repository:

### Bluetooth

This folder contains the Bluetooth API that is used by the server. There is also a client-side implementation that is primarily used for testing purposes. Each library also has a corresponding sample (in /test) to demonstrate usage.

### Server

This folder contains the Quizzly server implementation. The root level contains the Quizzly Server implementation (in QuizzlyServer.py) as well as a configuration file (Config.py) to be used by the server.

There is also a /data subfolder containing the implementation of the data structures used by the Quizzly Server (DataStructures.py) as well as JSON files containing questions to be used by the game and a data contract that defines the structure of valid messages to/from the server.

TODO: Shouldn't be committing actual values in the config.

### Client

This folder contains sample command line applications to simulate players for testing. One (SampleQuizzlyClient.py) is entirely automated. The other (SampleQuizzlyPlayer.py) is an interactive command line interface to play the game. 

## Installing

See below for installation instructions for the various components of the Quizzly application.

### Server

#### Dependencies

* [Python 3.x](https://www.python.org/downloads/) - Implementation framework
* [PyBluez](https://github.com/pybluez/pybluez) - Bluetooth socket library for Python

To run the server:
```
python QuizzlyServer.py
```

TODO: create an installer for all platforms.

### Client

#### Dependencies

* [Python 2.7.x](https://www.python.org/downloads/) - Implementation framework
* [PyBluez](https://github.com/pybluez/pybluez) - Bluetooth socket library for Python

## Authors

* **Josh Kimmel** - *Quizzly Server, Bluetooth Libraries* - (https://github.com/joshkimmel16)