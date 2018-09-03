from __future__ import division
'''
Created on 2014-04-02

@author: Nich
'''

from warlight import Engine, Handler
import weights
import odds
import copy
import warlight


def generate_attacks(player, region, game_state):
    attacks = []
    for neighbour in region.region.neighbours:
        if neighbour.region_id in game_state:
            gsn = game_state[neighbour.region_id]
            if not gsn.owner == player:
                attacks.append((region, gsn))
            
    return attacks



def get_attack_set(player, game_state, attacks, placement_amount, enemy_placement_amount):
    new_state = copy.deepcopy(game_state)
    apply_enemy_attack(game_state, player, new_state)
    game_state_rating = evaluate_game_state(player, new_state)
    new_rating = game_state_rating*0.80
    scored_attacks = rank_and_cost_attacks(attacks, game_state)
    rated_attacks = rank_scored_attacks(scored_attacks)
    attack_list = []
    placement_list = []
    cost_available = placement_amount
    
    
    for score, attack in rated_attacks:
        us, _, _, cost = attack
        if cost < 0:
            cost = 0
        if cost <= cost_available:
            new_state = apply_attack_to_game_state(attack, game_state, enemy_placement_amount)
            new_game_state_rating = evaluate_game_state(player, new_state)
            if new_game_state_rating > game_state_rating:
                new_rating = new_game_state_rating
                game_state = new_state
                cost_available -= cost
                attack_list.append((score, attack))
                if cost > 0:
                    placement_list.append((us.region, cost))
    
    score, default = rated_attacks[0]
    us, _, _, _ = default
    placement_list.append((us.region, cost_available))
    
    return placement_list, attack_list
        
    
    
    


def update_attack(us, them, armies, new_state):
    them_region_id = them.region.region_id
    us_region_id = us.region.region_id
    armies_killed = armies * 0.6
    armies_lost = them.armies * 0.7
    
    new_state[them_region_id].armies = them.armies - armies_killed
    
    if new_state[them_region_id].armies <= 0:
        new_state[them_region_id].armies = armies - armies_lost
        new_state[them_region_id].owner = us.owner
        new_state[us_region_id].armies = us.armies - armies
    else:
        new_state[us_region_id].armies = us.armies - armies_lost
        new_state[them_region_id].armies = them.armies - armies_killed
    
    


def apply_enemy_attack(game_state, player, new_state):
    for region in game_state.values():
        if not region.owner == "neutral" or not region.owner == player:
            for n in region.region.neighbours:
                if n.region_id in new_state and new_state[n.region_id].owner == player:
                    if odds.get_attack_odds(region, new_state[n.region_id]) > 0.5:
                        update_attack(region, new_state[n.region_id], region.armies, new_state)

def apply_attack_to_game_state(attack, game_state, enemy_army_addition):
    
    us, them, armies, _ = attack
    new_state = copy.deepcopy(game_state)
    
    if not us.owner == them.owner:
        update_attack(us, them, armies, new_state)
            
        neighbours = new_state[them.region.region_id].region.neighbours
        for n in neighbours:
            if n.region_id not in new_state:
                new_state[n.region_id] = warlight.Ownership(n, enemy_army_addition, them.owner)
                
        apply_enemy_attack(game_state, us, new_state)
                            
        
        
    else:
        new_state[them_region_id].armies = them.armies + armies
        new_state[us_region_id].armies = us.armies - armies

    return new_state


def rank_and_cost_attacks(attacks, game_state):
    scored_attacks = []
    for attack in attacks:

        scored_attack = cost_and_evaluate_attack(attack, game_state)
        scored_attacks.append(scored_attack)
    
    return scored_attacks


def cost_and_evaluate_attack(attack, game_state):
    us, them = attack
    armies_needed = cost_attack(attack)
    cost = armies_needed - us.armies
    rating = evaluate_attack(attack, game_state)
    return rating, (us, them, armies_needed, cost)


def cost_attack(attack):
    us, them = attack
    armies_needed = odds.armies_needed_to_attack(weights.meta_attack_score_threshold, 500, them.armies)
    
    return armies_needed

def cost_attacks(attacks_by_region, game_state, max_cost):
    costed_attacks = []
    for region_id, attacks in attacks_by_region.items():
        
        for attack in attacks:
            cost = cost_attack(attack)
            if cost <= max_cost:
                costed_attacks.append((cost, attack))
    costed_attacks = sorted(costed_attacks, key = lambda sattack:sattack[0], reverse = True)
        
    return costed_attacks
        

def rank_scored_attacks(scored_attacks):
    return sorted(scored_attacks, key = lambda sattack:sattack[0], reverse = True)

def rank_attacks(attacks_by_region, game_state):
    
    scored_attacks = []
    for region_id, attacks in attacks_by_region.items():
        
        for attack in attacks:
            score = evaluate_attack(attack, game_state)
            scored_attacks.append((score, attack))
    scored_attacks = rank_scored_attacks(scored_attacks)
        
    
    return scored_attacks




def calculate_attack_results(att_armies, def_armies):
    expected_wins = 0.6*att_armies
    expected_losses = 0.7*def_armies
    
    expected_remaining_attackers = att_armies - expected_losses
    expected_remaining_defenders = def_armies - expected_wins
    
    return (expected_wins, expected_losses, expected_remaining_attackers, expected_remaining_defenders)

def calculate_troops_needed_to_make_attack_favorable(att_armies, def_armies):
    return int(0.7*def_armies/0.6 - att_armies)




def is_border(region):
    return any([(not n in region.super_region.regions for n in region.neighbours)])

def find_borders(super_region):
    borders = []
    for region in super_region.regions:
        if is_border(region):
            borders.append(region)
    return borders

def foreign_neighbours(border, super_region):
    f_n = []
    for n in border.neighbours:
        if not n in super_region.regions:
            f_n.append(n)
    return f_n



        


def count_owned(player, super_region):
    count = 0
    for region in super_region.regions:
        if region.owner == player:
            count = count + 1
    return count
    

def evaluate_super_regions(super_regions):
    '''
    score super regions based on value and number of connections
    '''
    for super_region in super_regions:
        num_border = len(find_borders(super_region))
        border_score = (num_border/6)*10*weights.super_region_connectivity
        num_territories = len(super_region.regions)
        region_score = ((7-num_territories)/7)*10*weights.super_region_num_territories
        bonus_score = (int(super_region.reward)/7)*10*weights.super_region_bonus
        
        super_region.score = (border_score+region_score+bonus_score)/3


def evaluate_regions(player, regions):
    for region in regions:
        score = 0
        #A region is at least as good as the region it belongs to
        super_region_score = region.super_region.score       
        
        score += super_region_score*weights.region_super_region_score
        connectivity = (len(region.neighbours)/7)*10*weights.region_connectivity
        score += connectivity
        score += 10*weights.region_is_border if is_border(region) else 0
        
        
        region.score = score/3
    

def evaluate_placement(ownership, game_state):
    region_score = ownership.region.score*weights.placement_region_value
    neighbour_score = 0
    neighbour_enemy_armies = 0
    neighbour_ally_armies = 0
    for n in ownership.region.neighbours:
        n_owner= game_state[n.region_id]
        neighbour_score += n.score
        if n_owner.owner == ownership.owner:
            neighbour_ally_armies += n_owner.armies
        else:
            neighbour_enemy_armies += n_owner.armies
    
    
            
        
    neighbour_score = (neighbour_score/len(ownership.region.neighbours))*weights.placement_neighbour_value*10
    ratio_score = 0 
    if neighbour_ally_armies > 0:
        army_ratio = (neighbour_enemy_armies/neighbour_ally_armies)
        army_ratio = 1 if army_ratio > 1 else army_ratio
        ratio_score = army_ratio*10*weights.placement_army_ratio
    else:
        ratio_score = 1
    
    
    border_score = 10*weights.placement_border if neighbour_enemy_armies > 0 else 0
    
    placement_score = (region_score + neighbour_score+border_score) /3
    return placement_score
    

def evaluate_game_state(player, game_state):
    we_own = []
    neutral = []
    enemy_owns = []
    
    super_regions = {}
    super_region_count = 0
    
    for region in game_state.values():
        if region.owner == player:
            we_own.append(region)
            sup = region.region.super_region
            if not sup in super_regions:
                super_regions[sup] = []
            super_regions[sup].append(region)
        elif region.owner == "neutral":
            neutral.append(region)
        else:
            enemy_owns.append(region)
    
    for sup in super_regions.keys():
        if len(sup.regions) == len(super_regions[sup]):
            super_region_count += 1
        
    num_regions_score = (len(we_own)/42)*10*weights.game_state_region_weight
    num_super_region_score = (super_region_count/6)*10*weights.game_state_super_region_weight
    num_available_region_score = ((len(neutral)+len(enemy_owns))/42)*10*weights.game_state_available_regions
    
    attacks_per_region = {}
    for region in we_own:
            
        if region.armies > 1:
            new_attacks = generate_attacks(player, region, game_state)
            if len(new_attacks) > 0:
                attacks_per_region[region.region.region_id] = new_attacks
    
    attack_score = 0
    count = 0
    for attack in rank_attacks(attacks_per_region, game_state):
        
        score, (me, them) = attack
        attack_score += score
        count += 1
    attack_score = 0
    if count > 0:
        attack_score = (attack_score/count)*weights.game_state_avg_attack_score
    
    attacks_per_region = {}
    for region in enemy_owns:
            
        if region.armies > 1:
            new_attacks = generate_attacks(region.owner, region, game_state)
            if len(new_attacks) > 0:
                attacks_per_region[region.region.region_id] = new_attacks
    
    enemy_attack_score = 0
    count = 0
    for attack in rank_attacks(attacks_per_region, game_state):
        
        score, (me, them) = attack
        enemy_attack_score += score
        count += 1
    if count > 0:
        enemy_attack_score = (enemy_attack_score/count)*weights.game_state_avg_enemy_attack_score*-1
        
    return (enemy_attack_score+attack_score+num_available_region_score+num_super_region_score+num_regions_score)/4
    
    
    
    

def evaluate_attack(attack, game_state):
    us, them = attack
    
    region_score = us.region.score*weights.attack_region_score
    defender_region_score = them.region.score*weights.attack_defender_region_score
    
    defender_neutral = 10*weights.attack_defender_neutral if them.owner == 'neutral' else 0
    defender_enemy = 10*weights.attack_defender_enemy if not them.owner == 'neutral' else 0
    
    armies = us.armies*weights.attack_region_armies
    defender_armies = them.armies*weights.attack_defender_armies
    
    attack_score = 10*weights.attack_threshold_adjustment
    if defender_armies > 0:
        attack_score = (armies/defender_armies)*10*weights.attack_threshold_adjustment
    
    
    we_own, they_own = count_armies(us.region.super_region, us.owner, game_state)
    
    
    
    region_count = len(us.region.super_region.regions)
    if region_count > 0:
        super_region_enemy_presence = (they_own/region_count)*10*weights.attack_super_region_enemy_presence
        super_region_enemy_absence = (1-(they_own/region_count))*10*weights.attack_super_region_enemy_absence
        super_region_presence = (we_own/region_count)*10*weights.attack_super_region_presence
        super_region_absence = (1-(we_own/region_count))*10*weights.attack_super_region_absence
        
        destination_super_region_enemy_presence = (they_own/region_count)*10*weights.attack_destination_super_region_enemy_presence
        destination_super_region_enemy_absence = (1-(they_own/region_count))*10*weights.attack_destination_super_region_enemy_absence
        destination_super_region_presence = (we_own/region_count)*10*weights.attack_destination_super_region_presence
        destination_super_region_absence = (1-(we_own/region_count))*10*weights.attack_destination_super_region_absence
    else:
        super_region_enemy_presence = 0
        super_region_enemy_absence = 0
        super_region_presence = 0
        super_region_absence = 0
        
        destination_super_region_enemy_presence = 0
        destination_super_region_enemy_absence = 0
        destination_super_region_presence = 0
        destination_super_region_absence = 0
    
    
    return (region_score + defender_region_score + defender_neutral + defender_enemy + attack_score + super_region_enemy_presence + super_region_enemy_absence + super_region_presence + super_region_absence + destination_super_region_enemy_presence + destination_super_region_enemy_absence + destination_super_region_presence + destination_super_region_absence) /15


def bfs(start, player, game_state):
    
    queue = []
    queue.append([start])
    
    while queue:
        path = queue.pop(0)
        node = path[-1]
        owner = game_state[node.region_id]
        if owner.owner != player:
            return path
        for adjacent in node.neighbours:
            if not adjacent in path:
                new_path = list(path)
                new_path.append(adjacent)
                queue.append(new_path) 
            
                

def find_nearest_unoccupied(region, player, engine):
    path = bfs(region, player, engine.active_regions)
    #engine.log("PATH: "+str([r.region_id for r in path]))
    return path[1]
    
    
    
    
def count_armies(super_region, player, game_state):
    
    we_own=0
    enemy_owns=0
    for region in super_region.regions:
        if region.region_id in game_state:
            owner = game_state[region.region_id]
            if owner.owner == player:
                we_own += owner.armies
            elif not owner.owner == 'neutral':
                enemy_owns += owner.armies
    
    return we_own, enemy_owns    
    


def sort_by_region(attack_queue):
    attacks_by_region = {}
    for scored_attack in attack_queue:
        score, attack = scored_attack 
        me, them, qty, _ = attack
        region_id = me.region.region_id
        if not region_id in attacks_by_region:
            attacks_by_region[region_id] = []
        attacks_by_region[region_id].append((score, attack))
    return attacks_by_region
    
    
        
        
    
        


class MyBot(Handler):
    
    def __init__(self):
        self.army_placements = []
        self.attack_queue = []
        self.transfers = []
    
    def on_pick_starting_regions(self, engine, time, regions):
        evaluate_super_regions(engine.super_regions.values())
        evaluate_regions(engine.me, engine.regions.values())
        
        scored_regions = sorted(regions, key = lambda reg:engine.regions[reg.region_id].score, reverse = True)
        
        #engine.log([(r.region_id, len(r.super_region.regions), r.score, r.super_region.score) for r in scored_regions])
            
        starting_regions = [r.region_id for r in scored_regions[0:6]]
        #starting_regions = [r.region_id for r in regions[0:6]]
        
        
        
        engine.do_starting_regions(starting_regions)

    def on_go_place_armies(self, engine, time):
        game_state = engine.active_regions
        
        placements, attack_queues_by_region, transfers = self.generate_attack_plan(engine, game_state)
        
        self.attack_queues_by_region = attack_queues_by_region
        self.transfers = transfers
        
        engine.log("placements")
        engine.log(placements)
        
        for p in placements:
            r, qty = p
            engine.do_placements(r, qty)
            
            
            
        
        
        #evaluate_super_regions(engine.super_regions.values())
        #evaluate_regions(engine.me, engine.regions.values())
        '''
        game_state = engine.active_regions
        placement_scores = []
        for region in game_state.values():
            if region.owner == engine.me:
                placement_scores.append((evaluate_placement(region, game_state), region))
           
        scored_placements = sorted(placement_scores, key = lambda pscore:pscore[0], reverse = True)
        
        #engine.log(scored_placements)
        
        num_placements = int(len(scored_placements)*weights.placement_proportion)+1
        truncated_scored_placements = scored_placements[0:num_placements]
        
        
        placed = 0
        while placed < engine.starting_armies:
            counter = 0
            for placement in truncated_scored_placements:
                
                score, region = placement
                
                
                
                remaining = engine.starting_armies - placed
                if remaining == 0:
                    break
                #engine.log("Placing score "+str(score))
                qty = int((score/10)*remaining*weights.placement_amount_per)+1
                if qty > 0:
                    amt = qty if qty < remaining else remaining
                    
                    engine.do_placements(region.region, amt)
                    placed += amt
                    region.armies += amt
                else:
                    break
                            
            counter = counter + 1
            #failsafe in case the values get small, just put the rest on the best
            if counter > 5:
                engine.do_placements(scored_placements[0], engine.starting_armies - placed)
                break
        '''
        
    def generate_attack_plan(self, engine, game_state):
        attacks_per_region, transfers = self.get_attacks_and_transfers(engine.active_regions)
        #attack_queue = self.choose_attacks(engine, attacks_per_region, game_state)
        placement, attack_queue = get_attack_set(engine.me, game_state, attacks_per_region, engine.starting_armies, engine.enemy_starting_armies)
        
        attack_queue_by_region = sort_by_region(attack_queue)
        return placement, attack_queue_by_region, transfers
           


    def choose_attacks(self, engine, attacks_per_region, game_state):
        attack_queue = []
        for region_id, attacks in rank_attacks(attacks_per_region, game_state).items():
            available = game_state[region_id].armies
            for attack in attacks:
                score, (me, them) = attack
                att_armies = available
                def_armies = them.armies + 1 if them.owner == "neutral" else them.armies + engine.enemy_starting_armies
                expected_wins, expected_losses, expected_remaining_attackers, expected_remaining_defenders = calculate_attack_results(att_armies, def_armies)
                #(expected_wins_next, expected_losses_next, _, _) = calculate_attack_results(expected_remaining_attackers+engine.starting_armies, expected_remaining_defenders+engine.enemy_starting_armies)
                if expected_wins > expected_losses:
                    qty = int(max(me.armies * weights.attack_proportion, me.armies / len(attacks)))
                    attack_queue.append((me, them, qty))
                    available -= qty
        
                else:
                    break
                if available <= 0:
                    break
        return attack_queue


    def get_attacks_and_transfers(self, game_state):
        attacks = []
        transfers = []
        for region in game_state.values():
            if region.owner == engine.me:
                new_attacks = generate_attacks(engine.me, region, game_state)
                if len(new_attacks) > 0:
                    attacks += new_attacks
                else:
                    dest = find_nearest_unoccupied(region.region, engine.me, engine)
                    dest_owner = game_state[dest.region_id]
                    transfers.append((region, dest_owner, region.armies))
        
        return attacks, transfers


    

    def on_go_attack_or_transfer(self, engine, time):
        
        
        engine.log("Attack queue")
        engine.log(self.attack_queue)
        
        new_attacks = []
        
        for attacks in self.attack_queues_by_region.values():
            sorted_attacks = rank_scored_attacks(attacks)
            armies_used = 1
            me_armies = 0
            for scored_attack in attacks:
                score, attack = scored_attack
                me, them, qty, _ = attack
                me_armies = me.armies
                if me.armies > 1:
                    armies_used += qty
                    new_attacks.append((me, them, qty))
            remaining = me_armies - armies_used
            if len(new_attacks) >= 1:
                first_attack = scored_attack[1]
                me, them, qty, _ = first_attack
                new_attacks[0] = (me, them, qty+remaining)
            
                    
        
        
        for attack in new_attacks:
            me, them, qty = attack
            if qty > 1:
                engine.do_attack_or_transfer(me.region, them.region, qty)
        
            
        for region, dest, armies in self.transfers:
            if armies > 1:
                engine.do_attack_or_transfer(region.region, dest.region, armies)
            
        
        engine.active_regions = {}
        self.army_placements = []
        self.attack_queue = []       
        self.transfers = []
                
            


if __name__ == "__main__":
    engine = Engine(MyBot())
    engine.run()