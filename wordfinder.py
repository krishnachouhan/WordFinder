import gzip, os, re
from math import log


__version__ = '0.1.5'



from nltk.corpus import words
word_list = words.words()

words = word_list

# I did not author this code, only tweaked it from:
# http://stackoverflow.com/a/11642687/2449774
# Thanks Generic Human!


# Modifications by Scott Randal (Genesys)
#
# 1. Preserve original character case after splitting
# 2. Avoid splitting every post-digit character in a mixed string (e.g. 'win32intel')
# 3. Avoid splitting digit sequences
# 4. Handle input containing apostrophes (for possessives and contractions)
#
# Wordlist changes:
# Change 2 required adding single digits to the wordlist
# Change 4 required the following wordlist additions:
#   's
#   '
#   <list of contractions>


# # Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability).
# with gzip.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'wordninja','wordninja_words.txt.gz')) as f:
#   words = f.read().decode().split()

_wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
_maxword = max(len(x) for x in words)
_SPLIT_RE = re.compile("[^a-zA-Z0-9']+")
_numerics = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def split(s):
  """Uses dynamic programming to infer the location of spaces in a string without spaces."""
  l = [_split(x) for x in _SPLIT_RE.split(s)]
  print("LIST IS....")
  templist = [item for sublist in l for item in sublist]
  print(templist)
  newtemplist=[]
  string = ""
  for i in templist:
    if len(i)==1:
      if i not in _numerics:
        string = string+i
    else:
      newtemplist.append(i)
  templist=newtemplist
  tempresult=[]
  if len(string)>0:
    tempresult = split(string)
  templist += tempresult
  templist = confirmWords(templist)
  return templist


def confirmWords(word_list):
  new_word_list = []
  new_word_list.append(word_list[0])
  for index in range(0, len(word_list)-1):
    if not word_list[index+1] in words:
      words_match = False
      first_word = word_list[index]
      second_word = word_list[index+1]
      print("Working on ", first_word)
      while  len(first_word)>0 and not words_match:
        second_word = first_word[len(first_word)-1] + second_word
        first_word = first_word[:len(first_word)-1]
        print("\t", first_word)
        print("\t", second_word)
        if first_word not in words and second_word not in words:
          words_match = False
        else:
          words_match = True
      if words_match:
        new_word_list.append(first_word)
        new_word_list.append(second_word)
    else:
      new_word_list.append(word_list[index])
  return new_word_list


def _split(s):
    # Find the best match for the i first characters, assuming cost has
    # been built for the i-1 first characters.
    # Returns a pair (match_cost, match_length).
    def best_match(i):
        candidates = enumerate(reversed(cost[max(0, i-_maxword):i]))
        return min((c + _wordcost.get(s[i-k-1:i].lower(), 9e999), k+1) for k,c in candidates)
    # Build the cost array.
    cost = [0]
    for i in range(1,len(s)+1):
        c,k = best_match(i)
        cost.append(c)
    # Backtrack to recover the minimal-cost string.
    out = []
    i = len(s)
    while i>0:
        c,k = best_match(i)
        assert c == cost[i]
        # Apostrophe and digit handling (added by Genesys)
        newToken = True
        if not s[i-k:i] == "'": # ignore a lone apostrophe
            if len(out) > 0:
                # re-attach split 's and split digits
                if out[-1] == "'s" \
                  or (s[i-1].isdigit() and out[-1][0].isdigit()): # digit followed by digit
                    out[-1] = s[i-k:i] + out[-1] # combine current token with previous token
                    newToken = False
        # (End of Genesys addition)
        if newToken:
            out.append(s[i-k:i])
        i -= k
    return reversed(out)

