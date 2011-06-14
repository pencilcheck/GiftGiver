import os

import tornado.ioloop
import tornado.web

import divisi2
from divisi2 import examples

import pprint

import simplejson, json

import csv

pp = pprint.PrettyPrinter(indent=4)

def sortGift(arguments):
    occasion = arguments['occasion'][0]

    '''
    sender_occupation = arguments['sender_profile_occupation'][0]
    sender_gender = arguments['sender_profile_gender'][0]
    sender_age = arguments['sender_profile_age'][0]
    sender_religion = arguments['sender_profile_religion'][0]
    '''

    relationship = arguments['relationship'][0]

    receiver_occupation = arguments['receiver_profile_occupation'][0]
    receiver_gender = arguments['receiver_profile_gender'][0]
    receiver_age = arguments['receiver_profile_gender'][0]
    receiver_religion = arguments['receiver_profile_religion'][0]

    if 'types' in arguments:
        types = arguments['types'][0].split()
    else:
        types = []

    if 'features' in arguments:
        input_features = arguments['features'][0].split()
    else:
        input_features = []
    occasions = {}



    #reload conceptnet, change the cutoff default
    #cnet = divisi2.load('data:graphs/conceptnet_en.graph.gz')
    #A = divisi2.network.sparse_matrix(cnet, 'nodes', 'features', cutoff=0)

    cnet = divisi2.network.conceptnet_matrix('en')
    assoc = divisi2.network.conceptnet_assoc('en')

    concept_axes, axis_weights, feature_axes = cnet.svd(k=100)
    sim = divisi2.reconstruct_similarity(concept_axes, axis_weights, post_normalize=True)

    #U, S, _ = assoc.svd(k=100)
    #spread = divisi2.reconstruct_activation(U,S)
    spread = examples.spreading_activation()


    # gifts represent the gift list
    gifts = {}
    features = []
    table = csv.reader(open('gifts_60.csv', 'rb'))
    for i, row in enumerate(table):
        if i == 0:
            features = row[1:]
        if 0 < i < 4:
            occasions[row[0]] = dict(zip(features, row[1:]))
        if i > 4:
            gifts[row[0]] = dict(zip(features, row[1:]))


    #part 1
    diff = {}
    for name, features in gifts.items():
      diff[name] = 0
      for feature in features:
        diff[name] += pow( (float(occasions[occasion][feature]) - float(gifts[name][feature])),2)

    #pp.pprint( sorted (diff.items(), key=lambda x: x[1]) )
    #pp.pprint( sorted (diff.items(), key=diff.get) )
    sorted_gifts = sorted (diff.items(), key=lambda x: x[1])
    result_gifts = []
    for item in sorted_gifts:
        result_gifts.append((item[0], gifts[item[0]]))
    
    
    #part 2
    inferior_gifts = []
    for gift in result_gifts:
      for input_feature in input_features:
        if float(gift[1][input_feature]) < 0.4:
            inferior_gifts.append(gift)
            break
    for gift in inferior_gifts:
        for index, old_gift in enumerate(result_gifts):
            if old_gift[0] == gift[0]:
                del result_gifts[index]

    #print input_features    
    #print "result_gifts"
    #pp.pprint( result_gifts )
    #print "inferior_gifts"
    #pp.pprint( inferior_gifts )
    #print cnet.row_named('gift').to_dense().top_items()


    # part 3    

    results = []

    # Occasion, Relationship => Category
    scenario = divisi2.category(occasion,relationship)

    # find similarity between a gift and a category    
    candidates = spread.left_category(scenario).top_items(20)
    for gift in result_gifts:
        #sim_score = sim.left_category(scenario).entry_named(gift[0])
        score = 0.0
        
        for candidate in candidates:
            bait = float(candidate[1])
            # First level        
            if candidate[0] == gift:
                score += bait
            '''
            # Second level
            bait2 = bait * 0.25
            for relationTuple in cnet.row_named(candidate[0]).to_dense().top_items(5):    
                relation = relationTuple[0]            
                if relation[2] == gift:
                    # IsA
                    if relation[1] == 'IsA':
                        score += bait2
                    # PartOf
                    if relation[1] == 'PartOf':
                        score += bait2
                    # UsedFor
                    if relation[1] == 'UsedFor':
                        score += bait2
                    # AtLocation
                    if relation[1] == 'AtLocation':
                        score += bait2
                    # Desires
                    if relation[1] == 'Desires':
                        score += bait2
                    # CausesDesire
                    if relation[1] == 'CausesDesire':
                        score += bait2
                    # SymbolOf
                    if relation[1] == 'SymbolOf':
                        score += bait2
                    # LocatedNear
                    if relation[1] == 'LocatedNear':
                        score += bait2
            '''

        results.append ( (gift[0], score) )

    for gift in inferior_gifts:
        #sim_score = sim.left_category(scenario).entry_named(gift[0])
        score = 0.0
        
        for candidate in candidates:
            bait = float(candidate[1])
            # First level        
            if candidate[0] == gift:
                score += bait
            '''
            # Second level
            bait2 = bait * 0.25
            for relationTuple in cnet.row_named(candidate[0]).to_dense().top_items(5):    
                relation = relationTuple[0]            
                if relation[2] == gift:
                    # IsA
                    if relation[1] == 'IsA':
                        score += bait2
                    # PartOf
                    if relation[1] == 'PartOf':
                        score += bait2
                    # UsedFor
                    if relation[1] == 'UsedFor':
                        score += bait2
                    # AtLocation
                    if relation[1] == 'AtLocation':
                        score += bait2
                    # Desires
                    if relation[1] == 'Desires':
                        score += bait2
                    # CausesDesire
                    if relation[1] == 'CausesDesire':
                        score += bait2
                    # SymbolOf
                    if relation[1] == 'SymbolOf':
                        score += bait2
                    # LocatedNear
                    if relation[1] == 'LocatedNear':
                        score += bait2
            '''

        results.append ( (gift[0], score) )


    result_list = sorted (results, cmp=lambda x,y: cmp(x[1], y[1]), reverse=True)[:20]
    
    pp.pprint( result_list )

    return_list = [x[0] for x in result_list]
    return return_list


    """
    normalization_coefficient = 5.0

    sender_occupation_weight = 2.583 / normalization_coefficient
    sender_age_weight = 2.583 / normalization_coefficient
    sender_gender_weight = 2.75 / normalization_coefficient
    sender_religion_weight = 1.583 / normalization_coefficient

    occasion_weight = 4.583 / normalization_coefficient
    relationship_weight = 4.917 / normalization_coefficient

    receiver_occupation_weight = 3.75 / normalization_coefficient
    receiver_age_weight = 4.25 / normalization_coefficient
    receiver_gender_weight = 4.583 / normalization_coefficient
    receiver_religion_weight = 2.75 / normalization_coefficient

    interests_weight = 4.33 / normalization_coefficient


    sender_occupation_score = sender_occupation_weight * spread.entry_named(gift[0], sender_occupation)
    #if sender_occupation_score < 0: sender_occupation_score = 0

    sender_age_score = sender_age_weight * spread.entry_named(gift, sender_age)
    #if sender_age_score < 0: sender_age_score = 0

    sender_gender_score = sender_gender_weight * spread.entry_named(gift, sender_gender)
    #if sender_gender_score < 0: sender_gender_score = 0

    sender_religion_score = sender_religion_weight * spread.entry_named(gift, sender_religion)
    #if sender_religion_score < 0: sender_religion_score = 0


    occasion_score = occasion_weight * spread.entry_named(gift, occasion)
    #if occasion_score < 0: occasion_score = 0

    relationship_score = relationship_weight * spread.entry_named(gift, relationship)
    #if relationship_score < 0: relationship_score = 0


    receiver_occupation_score = receiver_occupation_weight * spread.entry_named(gift, receiver_occupation)
    #if receiver_occupation_score < 0: receiver_occupation_score = 0

    receiver_age_score = receiver_age_weight * spread.entry_named(gift, receiver_age)
    #if receiver_age_score < 0: receiver_age_score = 0

    receiver_gender_score = receiver_gender_weight * spread.entry_named(gift, receiver_gender)
    #if receiver_gender_score < 0: receiver_gender_score = 0

    receiver_religion_score = receiver_religion_weight * spread.entry_named(gift, receiver_religion)
    #if receiver_religion_score < 0: receiver_religion_score = 0


    total_score = sender_occupation_score * sender_age_score * sender_gender_score * sender_religion_score * occasion_score * relationship_score * receiver_occupation_score * receiver_age_score * receiver_gender_score * receiver_religion_score
    for interest in interests: total_score *= spread.entry_named(gift, interest) * interests_weight if spread.entry_named(gift, interest) * interests_weight > 0 else 0.0

    results.append ( (gift, total_score) )
    """
    

    

class MainHandler(tornado.web.RequestHandler):


    def get(self):
        self.render("static/index.html")

    def post(self):
        print self.request.arguments
        return_list = sortGift(self.request.arguments)

        self.write(json.dumps(return_list));


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static")
}

application = tornado.web.Application([
    (r"/", MainHandler),
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()




