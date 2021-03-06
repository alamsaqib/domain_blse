import numpy as np
import sys, os
import argparse
sys.path.append('../Utils/twitter_nlp/python/')
from Utils.twokenize import *
from Utils.WordVecs import *
from Utils.Representations import *

def conv_tweet(tweet, word_vecs):
    rep = []
    for w in words(tweet, word_vecs):
        try:
            rep.append(word_vecs[w])
        except KeyError:
            rep.append(word_vecs['the'])

    rep = np.array(rep)
    maxv = rep.max(axis=0)
    minv = rep.min(axis=0)
    avev = rep.mean(axis=0)

    return np.concatenate((maxv, minv, avev))

def words(sentence, model):
    return rem_mentions_urls(tokenize(sentence.lower()))

def rem_mentions_urls(tokens):
    final = []
    for t in tokens:
        if t.startswith('@'):
            final.append('at')
        elif t.startswith('http'):
            final.append('url')
        else:
            final.append(t)
    return final

class Semeval_Dataset():

    def __init__(self, DIR, model, one_hot=True,
                 dtype=np.float32, rep=ave_vecs,
                 binary=False):

        self.rep = rep
        self.one_hot = one_hot
        self.binary = binary

        Xtrain, Xdev, Xtest, ytrain, ydev,  ytest = self.open_data(DIR, model, rep)

        self._Xtrain = Xtrain
        self._ytrain = ytrain
        self._Xdev = Xdev
        self._ydev = ydev
        self._Xtest = Xtest
        self._ytest = ytest

    def to_array(self, y, N):
        '''
        converts an integer-based class into a one-hot array
        y = the class integer
        N = the number of classes
        '''
        return np.eye(N)[y]

    def convert_ys(self, y):
        if 'negative' in y:
            return 0
        elif 'neutral' in y:
            return 1
        elif 'objective' in y:
            return 1
        elif 'positive' in y:
            if self.binary:
                return 1
            else:
                return 2


    def open_data(self, DIR, model, rep):

        train = []
        for line in open(os.path.join(DIR, 'train.tsv')):
            try:
                idx, sidx, label, tweet = line.split('\t')
            except ValueError:
                idx, label, tweet = line.split('\t', 2)
            if self.binary:
                if 'neutral' in label or 'objective' in label:
                    pass
                else:
                    train.append((label, tweet))
            else:   
                train.append((label, tweet))

        dev = []
        for line in open(os.path.join(DIR, 'dev.tsv')):
            try:
                idx, sidx, label, tweet = line.split('\t')
            except ValueError:
                idx, label, tweet = line.split('\t', 2)
            if self.binary:
                if 'neutral' in label or 'objective' in label:
                    pass
                else:
                    dev.append((label, tweet))
            else:
                dev.append((label, tweet))

        test = []
        for line in open(os.path.join(DIR, 'test.tsv')):
            try:
                idx, sidx, label, tweet = line.split('\t')
            except ValueError:
                idx, label, tweet = line.split('\t', 2)
            if self.binary:
                if 'neutral' in label or 'objective' in label:
                    pass
                else:   
                    test.append((label, tweet))
            else:
                test.append((label, tweet))


        ytrain, Xtrain = zip(*train)
        ydev,   Xdev   = zip(*dev)
        ytest,  Xtest  = zip(*test)
                    
        Xtrain = [rep(sent, model) for sent in Xtrain]
        ytrain = [self.convert_ys(y) for y in ytrain]

        Xdev = [rep(sent, model) for sent in Xdev]
        ydev = [self.convert_ys(y) for y in ydev]

        Xtest  = [rep(sent, model) for sent in Xtest]
        ytest = [self.convert_ys(y) for y in ytest]

        if self.one_hot:
            if self.binary:
                ytrain = [self.to_array(y, 2) for y in ytrain]
                ydev = [self.to_array(y,2) for y in ydev]
                ytest = [self.to_array(y,2) for y in ytest]
            else:
                ytrain = [self.to_array(y, 3) for y in ytrain]
                ydev = [self.to_array(y,3) for y in ydev]
                ytest = [self.to_array(y,3) for y in ytest]


        if self.rep is not words:
            Xtrain = np.array(Xtrain)
            Xdev = np.array(Xdev)
            Xtest = np.array(Xtest)

        ytrain = np.array(ytrain)
        ydev = np.array(ydev)
        ytest = np.array(ytest)
        
        return Xtrain, Xdev, Xtest, ytrain, ydev, ytest
