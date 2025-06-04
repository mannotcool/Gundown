*This is a copy from my ICS3U1 final culminating project report*
# **Gundown**

*A shooter with some may say, a tactical twist.*
## Overview:
At a basic level, shooter games are the same every round, every game, every time you want to play them. Why not make something that is unique depending on who you play it with, and depending on how you strategize? Heavily inspired by the popular Steam shooter game “Rounds”, **Gundown** will be a shooter that lets users select from 3 different “ability” game modifier cards, and pick up another one on death. The game would also be 2 player multiplayer, and ideally have full support for Controller. The game would begin with the players being able to select 1 out of a selection of 3 cards. As a whole, there is a rotation of nearly 20 different cards, some with minor changes such as giving the player extra health, more bullet damage, faster moving bullets and some that can change the game completely, perhaps by giving a player exploding bullets. With this approach, the technical complexity of the ability cards can be determined near the end side of the game’s development. Players may also get the choice to switch weapons, instead of an ability card.

Once the players have selected their cards, they will be sent into a simple level(s). Nothing too fancy, perhaps just some blocks players can hide behind. Some blocks/walls may not be affected by physics/collisions, and some will. The level would be a simple battle ground for the players. Players (max 2 total) will have 100 HP, a block ability (on cooldown) that does a mini “explosion” around the player destroying any bullets perhaps coming at them, a crouch, and the ability to climb and jump off of walls. When a player dies, the dead player may pick up one more card for the next round. Movement is key in a game like this, as one wrong move can kill you. Bullets will be affected by gravity. There is no passive healing; it will be an ability card. It is the first to 5 points to beat the other player.

## Sprite Classes:
Due to the complexity of the game, *polymorphism* is absolutely necessary to ensure all different sprite classes behave correctly with each other. 

*“Examples” in the classes listed before are just more classes that will inherit from the aforementioned class above.*

- **Entity Class**
  - This class will be used by objects that need to be affected by gravity and require movement as a core characteristic.
  - As such, they would have variables for screen placement (x, y), image, health, anything needed by something you could consider in motion (speed). 
  - In entities whose purpose is to damage a player, (such as a bullet object), the *health variable* may be used to deal damage on collision. 
  - Examples of entities (more classes):
    - The Player(s)
      - Aside from the basic variables, they would house a whole set of modifiers for bullet speed, bullet damage, and whatever else, depending on their cards.
      - This would be the most complicated class, housing further information about input types, what gun is equipped, jump height, etc.
    - Bullet(s)
      - With this approach, they are easily replicable.
    - Explosive shield(s)
      - Attached with a cooldown to the player, activatable in game.

- **MapObject Class**
  - Every wall, floor, block, or part of a map would be under this class.
  - As a result, this class would store horizontal and vertical size of the surface. the X and Y, coordinates of preferably the center of a MapObject, this would allow for simple level creation.
  - They can also house different types (more classes) of MapObjects‘s, such as:
    - Climbable surface(s)
      - Jumping off from wall to wall would be a critical movement type for a game of this genre.
    - Explode on collision with bullet block(s)
      - These would be used to spice up a map, making it more fun.
    - Standard surface(s)
    - Physics enabled blocks(s)
    - Circle surface(s)


- **Weapon Class**
  - These would outline the image of the weapon, base firing speed, base damage, how many bullets can be shot at once, firing distance, etc.
  - The weapon class is extremely simple, examples of weapons include
    - AR-15s
    - Base Pistol
    - Shotguns
      - This would have a larger bullet spread, but closer distance.

- **GameEffect Class**
  - Extremely simple class used for one off visual effects such as an explosion.
  - It would only house the image, position (x, y), applyDamageInRadius, etc variables.
  - You would see this class to display:
    - Block Explosions
    - “Blox” effects on player death
    - Shield(s)

- **AbilityCard Class**
  - Ability cards are an essential core mechanic of the game, completely changing the scales and balance to add a fun twist to the game.
  - The class is responsible for holding the name, display image and modifiers for a variety of game 
  - AbilityCard would likely not be inherited by any other classes.
    - NOTE: The *exploding bullet ability card* would just be a condition check passer for a function built into the parent weapon class.

- **ScoreKeeper Class**
  - **Required by the requirements of the summative.**
  - As the name suggests, it would hold a running count of the score of the score and allow for easy displayability.  
  - As per the game rules discussed on page 1, it is a first to 5 “points” in order to win.

**As the game development progresses, it is important to note that classes may be reworked, and additional classes may be added. This is not a definitive list.**

## List of steps:
A game of this degree might sound like a nightmare to make, but is far from it as long as you create a stable framework in the beginning. As such, it is crucial to…

**Non-crutial things such as GUI, explosions, just fun stuff would be saved for after the core mechanics are created. Code commenting is ideally done while coding.**

1. Establish the most important parent classes (MapObjects, Entities, Etc) and the absolute need-be variables such as position variables.
1. Create a simple box-like map, just to have a space for the player to run in.
1. Create the Player and Gravity. It is imperative that the player has gravity.
1. Implement basic collision detection with the map. Climbing, etc is saved for later.
1. Work and create a movement system that meets all the requirements that are outlined in the game overview.
1. Ensure there is a working movement system for both players, and establish the input systems.
1. Begin working on the base weapon, attaching them to the players. Creating the bullet entity and equivalent would come around here too.
1. Add a health system, and a score system to follow closely.
1. Add the ability cards. They will apply *modifiers* to the player and weapon classes after all. 
1. Add the ability card selection screen which will appear at the beginning of the game, and on death.
1. Add the shielding system, which is created alongside the GameEffects class.
1. Finalize any and all GUIs.

## Additional Screenshots
![map diagram](https://media.mannot.cool/raw/U8DkVp.jpg)
![math](https://media.mannot.cool/raw/u5Qhua.png)






