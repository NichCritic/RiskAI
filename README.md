# RiskAI
An evolutionary algorithm based Risk AI in Python

## Details

Implements a genetic algorithm for the Warlight Risk AI tournament: http://theaigames.com/competitions/warlight-ai-challenge. The repository has 4 parts

### Warlight Server

This is the sample code downloaded in order to run the bots. It is still useful to run a pair of bots against each other and see how they perform. Credit for this goes to the developers at theaigames.com

### Warlight Server Tournament

Modified version of the above. Generates 50 bots from the template with random weights, then pairs them off in a tournament, calculating the fitness by the ELO Rating system https://en.wikipedia.org/wiki/Elo_rating_system

The Bottom 20 performers are dropped, and replaced with clones of the top performers, which are then mutated. In the end you should have a folder of 50 candidate bots

### Warlight AI Template

The base code for the bot. weights_template.py is used to generate weights.py, which is what is modified during training

### Warlight AI Gen

The scripts used to generate the bots
