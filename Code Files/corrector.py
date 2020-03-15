import argparse
import regex as re

###
# Method in order to calculate frequencies of each character and each substring that has length 2.
# Those dictionaries are used in calculation in error probabilty with the help of confusion matrices.
###
def createNgrams():
  for item in corpus:
    value = corpus.get(item, 0)
    unigram['#'] = unigram.get('#', 0) + value
    
    prev = '#'
    
    for curr in item:
      unigram[curr] = unigram.get(curr, 0) + value
      
      concat = prev + '' + curr    
      bigram[concat] = bigram.get(concat, 0) + value
      
      prev = curr

###
# Method in order to get edit differences between two words.
# It gets true, and false words as input. And using DL algorithm it checks differences between those words.
###
def getEditTypes(true, false):
  distances = [[0 for j in range(len(false) + 1)] for i in range(len(true) + 1)]
  edit_types = [['None' for j in range(len(false) + 1)] for i in range(len(true) + 1)]

  for i in range(1, len(true) + 1):
    distances[i][0], edit_types[i][0] = i, 'Deletion'

  for j in range(1, len(false) + 1):
    distances[0][j], edit_types[0][j] = j, 'Insertion'

  for i in range(1, len(true) + 1):
    for j in range(1, len(false) + 1):
      left, top, corner = distances[i][j-1] + 1, distances[i-1][j] + 1,  distances[i-1][j-1]
      if(true[i-1] is not false[j-1]):
        corner = corner + 1
      
      cost = min(left, top, corner)

      if(cost is distances[i-1][j] + 1):
        edit_types[i][j] = "Deletion"
      elif(cost is distances[i][j-1] + 1):
        edit_types[i][j] = "Insertion"
      elif(cost is distances[i-1][j-1]):
        edit_types[i][j] = 'Copy'
      elif(cost is distances[i-1][j-1] + 1):
        edit_types[i][j] = 'Substitution'
      
      if(true[i-2] is false[j-1] and true[i-1] is false[j-2]):
        if(distances[i-2][j-2] + 1 < cost):
          cost = distances[i-2][j-2] + 1
          edit_types[i][j] = 'Transpose'
      
      distances[i][j] = cost
  
  return edit_types

###
# Method in order to fill confusion matrices.
# It gets true, false and number of occurences using spell_errors files.
# Also it gets edit type between those words and updates related confusion matrix.
###
def fillConfusion(true, false, num_occurs, edit_types):
  i, j = len(true), len(false)
  operation = edit_types[i][j]

  while (i >= 0 and j >= 0) and operation is not 'None':
    operation = edit_types[i][j]

    first = true[i-1] if i > 0 else '#'
    second = false[j-1] if j > 0 else '#'
      
    if operation is 'Copy':
      i, j = i - 1, j - 1
    elif operation is 'Insertion':
      insertion[first + '' + second] = insertion.get(first + '' + second, 0) + num_occurs
      j = j - 1
    elif operation == 'Deletion':
      deletion[second + '' + first] = deletion.get(second + '' + first, 0) + num_occurs
      i = i - 1
    elif operation == 'Substitution':
      substitution[second + '' + first] = substitution.get(second + '' + first, 0) + num_occurs
      i, j = i - 1, j - 1
    elif operation == 'Transpose':
      transpose[second + '' + first] = transpose.get(second + '' + first, 0) + num_occurs
      i, j = i - 2, j - 2

###
# Method in order to create confusion matrices.
# It calls related functions and constructs confusions.
###
def createConfusion(true, false, num_occurs):
  edit_types = getEditTypes(true, false)
  fillConfusion(true, false, num_occurs, edit_types)

###
# Method in order to correct given misspelled words.
# It gets misspelled word as input and try to estimate correct version.
# Parameter smooth indicates whether 1-alpha smoothing is going to implemented while calculating error or not.
###
def correction(word, smooth):
  if(word in corpus):
    return word
  
  candidates, max_val, result = getCandidates(word), 0, ''
  for candidate, operation, first, second in candidates:
    prob = calculateProbability(candidate, operation, first, second, smooth)
    if(prob > max_val):
      result, max_val = candidate, prob
    
  return result

###
# Method in order to calculate probabily of candidate.
# It calculates P(w) and P(x|w).
###
def calculateProbability(candidate, operation, first, second, smooth):
  alpha = 1 if smooth else 0
  l = 26 if smooth else 0

  prob_error = 1
  if(unigram.get(first, 0) > 0):
    if(operation is 'Insertion'):
      prob_error = (insertion.get(first + '' + second, 0) + alpha) / (unigram.get(first, 0) + l)
    elif(operation is 'Substitution'):
      prob_error = (substitution.get(first + '' + second, 0) + alpha) / (unigram.get(second, 0) + l)
  
  if(bigram.get(first + '' + second, 0) > 0):
    if(operation is 'Deletion'):
      prob_error = (deletion.get(first + '' + second, 0) + alpha) / (bigram.get(first + '' + second, 0) + l)
    elif(operation is 'Transpose'):
      prob_error = (transpose.get(first + '' + second, 0) + alpha) / (bigram.get(first + '' + second, 0) + l)

  prob_corpus = corpus.get(candidate, 0) / sum(corpus.values())
  
  return prob_corpus * prob_error

###
# It gets all candidates with edit distance 1 than given misspelled words.
# It calls necessary functions and find all words with edit distance 1 that exist in corpus.
###
def getCandidates(word): 
  splits = getSplits(word)
  inserts = getInserts(splits)
  deletes = getDeletes(splits)
  substitutions = getSubstitutions(splits)
  transposes = getTransposes(splits)

  return set(inserts + deletes + substitutions + transposes)

def getSplits(word):
  splits = []
  for i in range(len(word) + 1):
    splits.append((word[:i], word[i:]))
  
  return splits

def getDeletes(splits):
  letters    = 'abcdefghijklmnopqrstuvwxyz-_'
  deletes = []
  for (first, second) in splits:
    for char in letters:
      token = first + char + second
      if(corpus.get(token, 0) > 0):
        a = first[-1] if len(first) > 0 else '#'
        deletes.append((token, 'Deletion', a, char))
        
  return deletes

def getInserts(splits):
  inserts = []
  for (first, second) in splits:
    if(len(second) > 0):
      token = first + second[1:]
      if(corpus.get(token, 0) > 0):
        a = first[-1] if len(first) > 0 else '#'
        inserts.append((token, 'Insertion', a, second[0]))
  
  return inserts

def getSubstitutions(splits):
  letters    = 'abcdefghijklmnopqrstuvwxyz-_'
  substitutions = []
  for (first, second) in splits:
    if(len(second) > 0):
      for char in letters:
        token = first + char + second[1:]
        if(corpus.get(token, 0) > 0):
          substitutions.append((token, 'Substitution', second[0], char))
  
  return substitutions

def getTransposes(splits):
  transposes = []
  for (first, second) in splits:
    if(len(second) > 1):
      token = first + second[1] + second[0] + second[2:]
      if(corpus.get(token, 0) > 0):
        transposes.append((token, 'Transpose', second[1], second[0]))
  
  return transposes

###
# Parses arguments.
###
def parseArg():
  parser = argparse.ArgumentParser()

  parser.add_argument('--corpus', action="store", dest="corpus", required=True)
  parser.add_argument('--spell_errors', action="store", dest="spell_errors", required=True)
  parser.add_argument('--misspelled', action="store", dest="misspelled", required=True)
  parser.add_argument('--correct', action="store", dest="correct", required=False)
  parser.add_argument('--smooth', action="store_true", dest="smooth", default=False)
  parser.add_argument('--print_confusions', action="store_true", dest="print_confusions", default=False)
  return parser.parse_args()

###
# Prints corrected versions of misspelled words to file.
###
def printResults(corrected):
  with open('output.txt', 'w+') as f:
    for predict in corrected:
      f.write(predict + '\n')

###
# Method in order to print confusion matrices.
###
def printConfusions():
  printConfusion(insertion, 0)
  printConfusion(deletion, 1)
  printConfusion(substitution, 2)
  printConfusion(transpose, 3)

###
# Method in order to print given confusion matrix.
###
def printConfusion(confusion, id):
  name = 'insertion.txt' if id == 0 else 'deletion.txt' if id == 1 else 'substitution.txt' if id == 2 else 'transpose.txt'
  letters    = '#abcdefghijklmnopqrstuvwxyz'

  with open(name, 'w+') as f:
    f.write('  #    a    b    c    d    e    f    g    h    i    j    k    l    m    n    o    p    q    r    s    t    u    v    w    x    y    z    \n')
    for c in letters:
      f.write(c + ' ')
      for s in letters:
        val = str(confusion.get(c + '' + s, 0))
        l = len(val)
        f.write(val)
        for _ in range(5 - l):
          f.write(' ')

      f.write('\n')

###
# Calculates accuracy of spell-corrector system.
###
def calculateAccuracy(true, corrected):
  counter = 0
  for actual, predict in zip(true, corrected):
    if(actual != predict):
      counter += 1

  accuracy = 1 - (counter / len(true))
  print('Accuracy is %.2f'  %accuracy)

###
# Method in order to tokenize line.
# It replaces some character with space.
###
def tokenize(line):
  line = re.sub('[0-9]', ' ', line)
  line = line.replace('.', ' ')
  line = line.replace('?', ' ')
  line = line.replace('!', ' ')
  line = line.replace('"', ' ')
  line = line.replace(',', ' ')
  line = line.replace('\'', ' ')
  line = line.replace('-', ' ')
  line = line.replace('_', ' ')
  line = line.replace(';', ' ')
  line = line.replace(':', ' ')
  line = line.replace('=', ' ')
  line = line.replace('(', ' ')
  line = line.replace(')', ' ')
  line = line.replace('[', ' ')
  line = line.replace(']', ' ')
  line = line.replace('/', ' ')
  line = line.replace('#', ' ')
  line = line.replace('>', ' ')
  line = line.replace('<', ' ')
  line = line.replace('$', ' ')
  line = line.replace('*', ' ')
  return line
###
# Methods in order to read corpus, and fill dictionary.
###
def readCorpus(corpus_file):
  with open(corpus_file, 'r') as f:
    lines = f.readlines()
    for line in lines:
      line = tokenize(line)
      words = re.findall(r'\w+', line.lower())
      for word in words:
        corpus[word] = corpus.get(word, 0) + 1

###
# Methods in order to read spell_errors, and constructs confusion matrices.
###
def readSpellErrors(spell_errors):
  with open(spell_errors, 'r') as f:
    lines = f.readlines()
    for line in lines:
      words = line.split(':')
      true = words[0].lower()
      falses = re.sub(r'\s+', '', words[1].lower()).split(',')
      value_list = []
      for false in falses:
        num_occurs = 1
        if('*' in false):
          token = false.split('*')
          false = token[0]
          num_occurs = int(token[1])
          
        createConfusion(true, false, num_occurs)

###
# Methods in order to read misspelled words in file and finds corrected words.
###
def getCorrections(misspelled, smooth):
  corrected = []
  with open(misspelled, 'r') as f:
    lines = f.readlines()
    for line in lines:
      misspelled = re.sub(r"\s+", "", line.lower())
      corrected.append(correction(misspelled, smooth))

  return corrected

###
# Methods in order to read correct version of misspelled ones, and calculates accuracy of system.
###
def checkCorrections(correct, corrected):
  true = []
  with open(correct, 'r') as f:
    lines = f.readlines()
    for line in lines:
      correct = re.sub(r"\s+", "", line.lower())
      true.append(correct)

  calculateAccuracy(true, corrected)

###
# All execution.
###
def execute(corpus_file, spell_errors, misspelled, correct, smooth, print_confusions):
  readCorpus(corpus_file)
  createNgrams()
  readSpellErrors(spell_errors)

  if(print_confusions):
    printConfusions()
  
  corrected = getCorrections(misspelled, smooth)
  printResults(corrected)

  if(correct is not None):
    checkCorrections(correct, corrected)

if __name__ == '__main__':

  arguments = parseArg()

  corpus_file, spell_errors, misspelled, correct, smooth, print_confusions = arguments.corpus, arguments.spell_errors, arguments.misspelled, arguments.correct, arguments.smooth, arguments.print_confusions  

  corpus = dict()
  insertion = {}
  deletion = {}
  substitution = {}
  transpose = {}
  unigram = {}
  bigram = {}

  execute(corpus_file, spell_errors, misspelled, correct, smooth, print_confusions)
