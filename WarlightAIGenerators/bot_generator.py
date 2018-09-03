'''
Created on 2014-04-10

@author: Nich



'''

import random
import os
import shutil

import uuid

def modify_member(member, count):
    purtubations = [[random.normalvariate(0, 0.01) for _ in range(len(member))] for _ in range(count)]
    
    population = []
    for p in purtubations:
        member = [b+pu for b, pu in zip(member, p)]
        population.append(member)
    
    return population

def create_population(count):
    base_values = [random.random() for _ in range(6)]
    return modify_member(base_values, count)
        

def load_member(file_name):
    with open(file_name) as weights:
        weights_string = weights.readline()
        weights = [float(w) for w in weights_string[1:].split(", ")]
    return weights


def create_member(pop_dir, p, n, member):
    print(member)
    directory = pop_dir + '/{id}pop{p}bot{n}/'.format(n=n, p=p, id=str(uuid.uuid4()))
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open("C:/Projects/WarlightAI/bot_template/weights_template.py") as template:
        file_text = "#"+", ".join([str(m) for m in member])+"\n"
        file_text += "".join(template.readlines())
        new_text = file_text.format(*member)
    with open(directory + "/weights.py", 'w') as new_weights:
        new_weights.write(new_text)
    shutil.copyfile("C:/Projects/WarlightAI/bot_template/attack_montecarlo.py", directory + "/attack_montecarlo.py")
    shutil.copyfile("C:/Projects/WarlightAI/bot_template/bot.py", directory + "/bot.py")
    shutil.copyfile("C:/Projects/WarlightAI/bot_template/goal.py", directory + "/goal.py")
    shutil.copyfile("C:/Projects/WarlightAI/bot_template/intel.py", directory + "/intel.py")
    shutil.copyfile("C:/Projects/WarlightAI/bot_template/map.py", directory + "/map.py")
    shutil.copyfile("C:/Projects/WarlightAI/bot_template/ratings.py", directory + "/ratings.py")
    shutil.copyfile("C:/Projects/WarlightAI/bot_template/trees.py", directory + "/trees.py")
    shutil.copyfile("C:/Projects/WarlightAI/bot_template/warlight.py", directory + "/warlight.py")
    
    with open(directory + "/rating.txt", 'w') as rating:
        rating.write("1500")


if __name__ == '__main__':
    
   
    
    
    population_dir = "../bots/"
    
    pop_dir = population_dir.format(n=0)
    prev_winner = load_member("C:/Projects/WarlightAI/bot_prev_winner/pop7bot17/weights.py")
    population = modify_member(prev_winner, 10)
    for n, member in enumerate(population):
        create_member(pop_dir, 0, n, member)
    
    
    
    for i in range(1, 10):
        pop_dir = population_dir.format(n=i)
        population = create_population(10)
        for n, member in enumerate(population):
            create_member(pop_dir, i, n, member)
            
        
            
    
    