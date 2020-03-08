import regex as re

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
      deletion[first + '' + second] = deletion.get(first + '' + second, 0) + num_occurs
      i = i - 1
    elif operation == 'Substitution':
      substitution[first + '' + second] = substitution.get(first + '' + second, 0) + num_occurs
      i, j = i - 1, j - 1
    elif operation == 'Transpose':
      transpose[first + '' + second] = transpose.get(first + '' + second, 0) + num_occurs
      i, j = i - 2, j - 2

def normalizeConfusions():
  letters    = 'abcdefghijklmnopqrstuvwxyz-_.?'

  for first in letters:
    for second in letters:
      regex1 = len(re.findall(first, text))
      regex2 = len(re.findall(first + '' + second, text))

      if(regex1 > 0):
        insertion[first + '' + second] = insertion.get(first + '' + second, 0) / regex1
        substitution[first + '' + second] = substitution.get(first + '' + second, 0) / regex1
      if(regex2 > 0):
        deletion[first + '' + second] = deletion.get(first + '' + second, 0) / regex2
        transpose[first + '' + second] = transpose.get(first + '' + second, 0) / regex2

def createConfusion(true, false, num_occurs):
  edit_types = getEditTypes(true, false)
  fillConfusion(true, false, num_occurs, edit_types)
  #normalizeConfusions()

corpus = dict()

text = open('corpus.txt').read().lower()

insertion = {}
deletion = {}
substitution = {}
transpose = {}

with open('corpus.txt', 'r') as f:
  lines = f.readlines()
  for line in lines:
    words = re.findall(r'\w+', line.lower())
    for word in words:
      corpus[word] = corpus.get(word, 0) + 1

with open('spell-errors.txt', 'r') as f:
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