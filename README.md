# A-Star Visualiser

This is a program that visualises my implementation of the A-star pathfinding algorithm in Python

## Features

### Pathfinding

The A-star algorithm will navigate the grid of nodes in order to find a path from the start position to the target position.  
When a path has been found it will be displayed on the screen as a red line going from the starting node (blue) to the target node (pink).

### Walls

The algorithm will be able to navigate around walls (obstacles) which are nodes that the path cannot go through.  
Using perlin noise, random walls are generated in order to provide different paths to try out.  
For repeatability the user can manually enter a seed for the random noise.

### User created walls

The user can draw their own walls to create different scenarios for the algorithm

## Usage

### Controls

`Left click` - Set starting position  
`Right click` - Set target position  
`Space` - Start search

`Escape` - Stop search / exit  
`Middle click` - Hold down to create walls (use with `shift` to delete walls)  
`c` - Clear screen  
`r` - Clear path from previous search  
`n` - New random set of walls  
`m` - Enter a seed manually  
`d` - Set distWeight  
`i` - Set the wall intensity  

### Settings

The A-star class contains the following program settings: gridSize, blockSize, defaultIntensity, distWeight

- gridSize
  - Sets numbers of blocks in the x and y axis, respectivley
- blockSize
  - Sets the height and width of each block in pixels
- defaultIntensity
  - Sets the intensity of the walls
  - Lower value = less walls
  - Between 0 and 1
- distWeight
  - Sets the weight of the distance from the target node
  - A higher value of distWeight can mean faster times but less efficient paths due to the algorithm prioritising nodes closer to the target node
  - Recommended between 1.25 and 2

## Installation and Setup

- Download Astar.py
- Install python and the noise library
- Run the Astar.py
