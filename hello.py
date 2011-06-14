import os

import tornado.ioloop
import tornado.web

import divisi2
from divisi2 import examples

import pprint

import simplejson, json


def test():
    cnet = divisi2.network.conceptnet_matrix('en')
    U, S, V = cnet.normalize_all().svd(k=100)

    '''
    new_cnet, row_shift, coln_shift, total_shift = cnet.mean_center()
    U, S, V = new_cnet.svd(k=100)
    '''

    '''
    recommend = divisi2.reconstruct(U, S, V, shifts=(row_shift, coln_shift, total_shift))
    print recommend.col_labels
    print recommend.row_named('gift').top_items()
    '''

    similarity = divisi2.reconstruct_similarity(U, S, post_normalize=False)
    print similarity.row_named('gift').top_items()

    '''
    assoc = divisi2.network.conceptnet_assoc('en')
    U, S, _ = assoc.svd(k=100)
    spread = divisi2.reconstruct_activation(U,S)
    spread = examples.spreading_activation()
    '''

def sortGift(arguments):
    # spreading parameter
    sender_occupation = arguments['sender_profile_occupation'][0]
    sender_gender = arguments['sender_profile_gender'][0]
    sender_age = arguments['sender_profile_age'][0]
    sender_religion = arguments['sender_profile_religion'][0]

    occasion = arguments['occasion'][0]
    relationship = arguments['relationship'][0]

    receiver_occupation = arguments['receiver_profile_occupation'][0]
    receiver_gender = arguments['receiver_profile_gender'][0]
    receiver_age = arguments['receiver_profile_gender'][0]
    receiver_religion = arguments['receiver_profile_religion'][0]

    interests = arguments['interests'][0].split()


    cnet = divisi2.network.conceptnet_matrix('en')
    #concept_axes, axis_weights, feature_axes = cnet.svd(k=100)
    #sim = divisi2.reconstruct_similarity(concept_axes, axis_weights, post_normalize=True)

    # reconstruct association operation from U and Signa
    # load association matrix
    assoc = divisi2.network.conceptnet_assoc('en')
    U, S, _ = assoc.svd(k=100)
    # load spreading activation matrix
    spread = divisi2.reconstruct_activation(U,S)
    #spread = examples.spreading_activation()


    # gifts represent the gift list
    #gifts = set([x.strip() for x in open('gift_list.txt').readlines()])
    #gifts = set([' '.join(x.strip().split('(')[0].split('\xef\xbc\x88')[0].split()) if x.find(':') < 0 and len(x.strip()) > 0 else '' for x in open('list.txt').readlines()])
    #gifts = set([' '.join(x.strip().split('(')[0].split('\xef\xbc\x88')[0].split()) if x.find(':') < 0 and len(x.strip()) > 0 else '' for x in open('gift_list_0613.txt').readlines()])
    gifts = [x[0] for x in spread.row_named('gift').top_items(1000)]

    results = []

    for gift in gifts:
        if gift == '': continue

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


        sender_occupation_score = sender_occupation_weight * spread.entry_named(gift, sender_occupation)
        if sender_occupation_score < 0: sender_occupation_score = 0

        sender_age_score = sender_age_weight * spread.entry_named(gift, sender_age)
        if sender_age_score < 0: sender_age_score = 0

        sender_gender_score = sender_gender_weight * spread.entry_named(gift, sender_gender)
        if sender_gender_score < 0: sender_gender_score = 0

        sender_religion_score = sender_religion_weight * spread.entry_named(gift, sender_religion)
        if sender_religion_score < 0: sender_religion_score = 0


        occasion_score = occasion_weight * spread.entry_named(gift, occasion)
        if occasion_score < 0: occasion_score = 0

        relationship_score = relationship_weight * spread.entry_named(gift, relationship)
        if relationship_score < 0: relationship_score = 0


        receiver_occupation_score = receiver_occupation_weight * spread.entry_named(gift, receiver_occupation)
        if receiver_occupation_score < 0: receiver_occupation_score = 0

        receiver_age_score = receiver_age_weight * spread.entry_named(gift, receiver_age)
        if receiver_age_score < 0: receiver_age_score = 0

        receiver_gender_score = receiver_gender_weight * spread.entry_named(gift, receiver_gender)
        if receiver_gender_score < 0: receiver_gender_score = 0

        receiver_religion_score = receiver_religion_weight * spread.entry_named(gift, receiver_religion)
        if receiver_religion_score < 0: receiver_religion_score = 0


        total_score = sender_occupation_score * sender_age_score * sender_gender_score * sender_religion_score * occasion_score * relationship_score * receiver_occupation_score * receiver_age_score * receiver_gender_score * receiver_religion_score
        for interest in interests: total_score *= spread.entry_named(gift, interest) * interests_weight if spread.entry_named(gift, interest) * interests_weight > 0 else 0.0

        results.append ( (gift, total_score) )

    result_list = sorted (results, cmp=lambda x,y: cmp(x[1], y[1]), reverse=True)[:20]
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint( result_list )

    return_list = [x[0] for x in result_list]
    return return_list

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
    '''
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
    '''
    test()




