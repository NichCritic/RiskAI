import bot_generator

import sys

if __name__ == '__main__':
    
    path = sys.argv[1]
    count = int(sys.argv[2])
    
    population_dir = "C:/Projects/WarlightAI/bots/"
    
    if path == "new":
        for i in range(int(count)):
        
            population = bot_generator.create_population(1)
            for n, member in enumerate(population):
                bot_generator.create_member(population_dir, i, n, member)
    
    
    
    else:
        
        prev_winner = bot_generator.load_member(path+"/weights.py")
        population = bot_generator.modify_member(prev_winner, int(count))
        for n, member in enumerate(population):
            bot_generator.create_member(population_dir, 0, n, member)
    
    
    
    