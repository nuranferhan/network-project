## Multiplayer 2D Game

## Overview

<p align="center">
  <img src="https://github.com/user-attachments/assets/04439242-8fa3-4536-8ccf-2ffbcdd15408" width="480" alt="Gameplay Demo"/>
</p>

This project is a 2D maze style multiplayer game created using Python and Pygame. The game runs on a client-server architecture and utilizes the TCP/IP protocol to allow players to connect and interact in real-time.

## Project Objective

The main goal is to design a real-time multiplayer game where players can connect over a network. The game reinforces the concepts learned in network programming by implementing socket communication, synchronization, and concurrent player interactions.

Players are assigned roles as either thieves or police. The thief tries to escape within a time limit, while the police attempt to catch the thief. Various boost items are available on the map to enhance gameplay, such as speed-ups, teleporters, and point bonuses.


## Technologies Used

- **Python 3.x**
- **Pygame** – For graphics and game mechanics
- **Socket Programming** – For network communication via TCP/IP
- **Pickle** – For data serialization
- **Threading** – To support multiple clients concurrently


## Key Features

- Real-time multiplayer gameplay
- Dynamic maze generation
- Boost items with effects (speed, teleport, points)
- Score tracking and countdown timer
- Animated characters and end-game screen
- Automatic new game session management


## Project Structure

```bash
network-project/
│
├── server.py              # Server-side game management
├── client.py              # Client-side game logic
├── homescreen.py          # Initial user interface
├── network.py             # Network connection handling
├── boosts.py              # Boost item mechanics
├── graphics.py            # Drawing and rendering
├── map.py                 # Maze generation and walls
├── player.py              # Player movement and animation
├── roles.py               # Role assignment (thief/police)
├── scoreboard.py          # Scoreboard and final results
├── timer.py               # Countdown timer
└── gameconfig.py          # Game configuration (FPS, colors, sizes)
