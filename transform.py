# -*- coding: utf-8 -*-

'''
APPROACH:
1. we can easily detect which sentences have been accidentally title-cased: the 1st letter of each word will be capitalized. we can easily lowercase the entire string for that row, and then capitalize the first letter. we may, however, lose some properly title-cased nouns along the way.

2. we can easily check words against a dictionary to find common proper nouns (ie, 'America', 'USA'); if the word doesn't exist in the dictionary (ie, 'america', 'usa') & the lowcased word is equal to the first dict suggestion, lowcased, then it's probably a situation where we can simply replace the word with that dictionary suggestion. this takes care of examples like the 2 already mentioned, as well state names, very famous people, etc. this takes a very long time, as its checking every word in 20,000 rows of data, but i dont think there's any way around that, except maybe with some memoization.

3. one more piece of low-hanging fruit: we can find '. ' and capitalize words after that

OPTIMIZATIONS?
we could iterate through the csv & add all capitalized nouns we find to some kind of dict, then check lowercased nouns against it

however, just because a noun is capitalized in one place (ie, 'Neighborly Care Network') doesn't mean it should always be capitalized...

there's a variety of mispelled words in the data, as well. can we do something about that without having to manually review the corrections?

NATURAL LANGUAGE PROCESSING?
there's a wide range of NLP modules and frameworks for Python. however, part of speech taggers aren't really able to detect improperly lowercased prooper nouns, so we are back at square 1...

with a large enough sample size & enough time, implementing something like this seems promising:
  
https://cs.cmu.edu/~llita/papers/lita.truecasing-acl2003.pdf

or, with the rapid rise of relatively simple machine-learning tools, it might be effective to train an ai on a large corpus of text & add the ai to the ETL pipeline

''' 

import csv, enchant, nltk, os, petl, re, string, sys

from nltk.tag import pos_tag

d = enchant.Dict("en_US")

input = petl.fromcsv('data.csv')

def reverse_titlecase(description):
  # check if this is one of the rows that was title-cased
  if all(word[0].capitalize() == word[0] for word in description):
    return ' '.join(description).lower().capitalize().split(' ')
  else:
    return description
    
def lookup_word(word):
  # if there's a simple suggestion that is titlecased, replace the word with that titlecased suggestion
  if not d.check(re.sub(r'[^0-9A-Za-z]', '', word)):
    if d.suggest(re.sub(r'[^0-9A-Za-z]', '', word)):
      if d.suggest(re.sub(r'[^0-9A-Za-z]', '', word))[0].lower() == re.sub(r'[^0-9A-Za-z]', '', word).lower():
        return d.suggest(re.sub(r'[^0-9A-Za-z]', '', word))[0] + word[len(re.sub(r'[^0-9A-Za-z]', '', word)):]
  return word

def check_dict_suggestions(description):
  # map over the description list using the lookup_word method
  return map(lookup_word, description)
  
def cap_sentences(description):
  split_on_period = ' '.join(description).split('. ')
  # map over the description list using the lookup_word method
  return map(lambda str_seg: str_seg.capitalize(), split_on_period)

def row_mapper(row):
  row_id = str(row[0])
  description = str(row[1]).split(' ')
  
  # check if this is one of the rows that was title-cased
  de_titled_desc = reverse_titlecase(description)
  
  # check some basic potential dictionary capitalization issues—low-hanging fruit
  dicted_desc = check_dict_suggestions(de_titled_desc)
  
  final = '. '.join(cap_sentences(dicted_desc))
      
  return [row_id, final]

petl.rowmap(input, row_mapper, ['id', 'description'], failonerror=True).tocsv('output.csv')
