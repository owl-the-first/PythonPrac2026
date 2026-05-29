MOOD documentation
==================

MOOD is a multiplayer text-based MUD game.  A player connects to the
server with a unique username, moves around a 10x10 field, meets
monsters, attacks them with different weapons, sends chat messages to
other players, changes server locale, and can run commands from a file.

The project is split into a server and a client.  The server stores the
game state: players, monsters, hit points, movement, chat messages,
locales, and wandering monsters.  The client reads user commands,
translates them into the server protocol, receives server responses, and
prints them for the user.

Running the game
================

After installing the wheel package, the server is started with:

.. code-block:: bash

   mood-server

A client is started with a username:

.. code-block:: bash

   mood-client Denis

A second client can connect with another username:

.. code-block:: bash

   mood-client Sonya

Usernames must be unique.  If a username is already connected, the server
rejects the new client.

Main client commands
====================

Movement commands:

.. code-block:: text

   up
   down
   left
   right

The field is cyclic, so moving outside one border returns the player from
the opposite side.

Adding a monster:

.. code-block:: text

   addmon dragon hello "Who goes there?" hp 21 coords 1 2

The command creates a monster with a name, greeting phrase, hit points,
and coordinates.  If another monster is already placed at the same cell,
it is replaced.

Attacking a monster:

.. code-block:: text

   attack dragon with sword
   attack dragon with spear
   attack dragon with axe

Available weapons have different damage values:

.. code-block:: text

   sword: 10
   spear: 15
   axe: 20

Chat command:

.. code-block:: text

   sayall "Sonya, let's attack dragon at 1 2"

The message is sent to all connected players.

Wandering monsters can be enabled or disabled:

.. code-block:: text

   movemonsters on
   movemonsters off

For deterministic tests and demonstrations it is useful to disable
wandering monsters.

Running commands from a file
============================

The client supports script mode:

.. code-block:: bash

   mood-client DenisScript --file demo_exam.mood

Example command file:

.. code-block:: text

   movemonsters off
   addmon dragon hello "Who goes there?" hp 21 coords 1 2
   right
   down
   down
   attack dragon with sword

Localization
============

The server supports changing the locale for a client:

.. code-block:: text

   locale ru_RU.UTF8

After that, server messages for this client are translated into Russian,
including plural forms for health points:

.. code-block:: text

   1 очко здоровья
   2 очка здоровья
   5 очков здоровья

The English locale can be restored with:

.. code-block:: text

   locale en_US.UTF8

Documentation command
=====================

The client has a documentation command:

.. code-block:: text

   documentation

It opens the installed HTML documentation and also prints the local file
URL.  This is useful if the browser does not open local files
automatically.

API documentation
=================

Server
------

.. automodule:: mood.server.__main__
   :members:
   :undoc-members:

Client
------

.. automodule:: mood.client.__main__
   :members:
   :undoc-members:
