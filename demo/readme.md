## CarDream AutoGen demo  

CarDream is an online car retailer that want to make the experience of buying a car be enjoyable as possible.  
The system, based on your inputs will guide you through the available models and will let you pick the one that fits you.
You can then buy it, or, in case you have already made some order, see them and cancel them.

### How to run it
use `uv run main.py` to run the demo.

### How to use it
Due to 'educational' role of this project all the interaction is done via console where you will also see several logs
whose goal is to give you an idea of what is going on under the hood.  
The agent is not rock solid, but browsing through code maybe you can have some ideas of how to structure you next AutoGen
project.

<add some interaction samples>


### How to reset the database
The projects creates a SQLlite database at startup and imports all the cars included in the `data/cars.csv`.  
If you want, after some tests, start from scratch, just delete the `data/cars.db` and it will be recreated at the next run.