Title: Solving the Five Five-Letter Words Problem
Date: 2024-11-07
Category: projects
Authors: haondt
Tags: python
Summary: How I solved Matt Parkers five-word problem (how many combinations of five-letter words are there with 25 unique letters?) in under 5 minutes with python.

A friend presented this challenge to me: solve Matt Parkers [five five-letter words](https://www.youtube.com/watch?v=_-AfhLQfb6w) problem in under 5 minutes. I was able to get it solved in 4 minutes and 26 seconds. Nothing compared to the outlandish solutions others have found - well into the microseconds - but pretty reasonable for a python solution and leagues ahead of Matt's 30-day solution. Here's how I solved it.

<br />

[TOC]

<br />

### The Problem
Firstly a more rigorous definition of the problem. We will take a [known word list](https://github.com/dwyl/english-words) and find all the possible combinations of words that, together, use exactly 25 different letters. The order of the words is not relevant and we can consider anagrams to be the same word. We are trying to determine the number of combinations of words, i.e. the total number of possible sets.

Next, let's take a quick peek at the word list to see what exactly we're working with

```python
def get_words():
    words = set()
    with open('words_alpha.txt', 'r') as f:
        for line in f:
            word = line.strip()
            if len(word) != 5:
                continue
            if len(set(word)) != 5:
                continue
            word = ''.join(sorted(word))
            words.add(word)
    return list(words)

print(len(get_words()))
```

```shell
~ python3 five-letters.py
5977
```

Alright 5977 words to consider. Obviously a naive solution of just looping through all the words and checking if they form a set of 25 unique letters isn't gonna work - that would be 7.6x10^18 operations. We'll employ three strategies to speed things up: 1. bitmasking, 2. pruning and 3. vectorization.

<br />

### Bitmasking

My first thought was that since we don't care about the order of the letters and are interested in a unique set of letters, we can represent each word as a sparse array.

```
A B C D E F G H...
0 0 0 0 0 0 0 0...
```

The word "DEAF" would be encoded like so:

```
A B C D E F G H...
1 0 0 1 1 1 0 0...
```

Since there are only 26 letters in the alphabet, we can easily fit this mask in a single 32 bit integer. This allows us to perform set operations in a single cpu instruction, and store the words in contiguous memory. I'm not sure how applicable this is in python, due to the way numbers and arrays are implemented, but we're certainly giving it it's best shot. Let's define a function to convert a word to an integer.

```
alphabet = 'abcdefghijklmnopqrstuvwxyz'
ord_chart = {c:ord(c) - ord('a') for c in alphabet}
def numberify(word: str | list[str]):
    bitmask = 0
    for char in word:
        bitmask |= 1 << ord_chart[char]
    return bitmask

def get_words():
    ...
            word = numberify(sorted(word))
            words.add(word)
    ...
```

<br />

### Pruning

There is two pruning strategies we can employ. The first is keeping the sets ordered alphabetically. This way we can catch the creation of duplicate sets much earlier, by pruning a branch if the next word is out of order. We're just going to sort the numbers numerically, since they don't actually need to be in alphabetical order, just in a consistent order.

Let's start by selecting the first two words with a nested loop, pruning branches when the words lose alphabetical order or have repeated letters.

```python
def main():
    words = sorted(get_words())

    two_words: []
    for i, w1 in enumerate(words):
        for w2 in words[i:]: # maintain "alphabetical" order 
            if w1 & w2 == 0: # check for distinct letters
                two_words.append((w1, w2))
```

Great, now for the second type of pruning. Let's say we have a set of two words, ABCDE and FGHIJ (made up words). The combined mask for these two is ABCDEFGHIJ. Now lets say we have another set of two words, AFBGC and HDIEJ. The combined mask for these two is... also ABCDEFGHIJ. Any word that can be combined with the first tuple can also be combined with the second tuple, since they cover the same letters. As long as that word also maintains alphabetical order.

Going forward, we will make word selection a two step process: First we determine the compatible words based on the mask, and second we check the alphabetical order. For the above example, that brings 4 checks (mask, order, mask, order) down to three checks (mask, order, order). To enable this we'll need to store a map of the mask and all the pairs that combine to create that mask.

```python
def main():
    words = sorted(get_words())

    two_words: dict[int, list[tuple[int, ...]]] = {}
    for i, w1 in enumerate(words):
        for w2 in words[i:]:
            if w1 & w2 == 0:
                wc = w1 | w2 # create combined mask for two words
                two_words.setdefault(wc, []).append((w1, w2))

    print(len(two_words))
```

```shell
~ time python3 five-words.py
640023
python3 five-words.py  3.72s user 0.13s system 99% cpu 3.853 total
```

Not too bad, 4 seconds to build a list of 640,000 two word pairs. A basic nested loop would've produced 5977^2 = 35,724,529 pairs.

<br />

### Vectorization

For the third word, there's no magic here, we're just going to do another loop. Things are getting pretty dicey here time-complexity-wise, so we're going to bring in our pièce de résistance, numpy. Currently we have two lists of masks, one for our two word pairs and one for our single words. A mask list looks something like this:

```
abcdefghijk...
--------------
00100001101...
01101001101...
01001100100...
.
.
.
```

We need to combine these two lists, such that we get a list of all the combinations of two word masks and one word masks that fit together to form a three word mask with 15 different letters. Step one, compute the outer `or` and `and`s of the two masks, so we get two _n_ by _m_ masks.

```python
def combine_masks(m1, m2):
    combined_mask = np.bitwise_or.outer(m1, m2)
    overlap_mask = np.bitwise_and.outer(m1, m2)
```

Step two, use the overlap mask to select combinations that have two distinct sets of letters. Those cells will have a `0` value.

```python
def combine_masks(m1, m2):
    ...
    combined_allow_mask = overlap_mask == 0
```

Just to make it a little easier to rationalize everything, I'm going to ravel the mask. This is taking a 2 dimensional array and flattening it by just concatenating the rows.

```
[[ a b c ]
 [ d e f ]]
```

becomes

```
[ a b c d e f ]
```

```python
def combine_words(m1, m2):
    ...
    raveled_allow_mask = combined_allow_mask.ravel()
```

Step three, with the allow mask raveled, we can convert the mask to a list of indices. We want the indices of all the `True` values in the allow mask. If we were to ravel all the pairs of the two word and single word masks, this would be all the indices of the pairs that fit together. In fact that's what we plan to do, so we'll return that along with the raveled `or` mask, which we'll need for selecting the fourth and fifth words.

```python
def combine_words(m1, m2):
    ...
    allow_mask_indices = np.where(raveled_allow_mask)[0]
    raveled_combined_mask = combined_mask.ravel()
    return allow_mask_indices, raveled_combined_mask
```

Nice, so we've determined a list of all the three word sets. Next we need to prune all the sets where the third word will be out of alphabetical order. To do that we'll need to first unravel the index to get the two word tuples and single words.

```python
def main():
    ...
    three_words: dict[int, list[tuple[int, ...]]] = {}
    two_words_keys = list(two_words.keys())
    two_words_values = list(two_words.values())
    two_words_mask = np.array(two_words_keys, dtype='uint32')
    words_mask = np.array(words, dtype='uint32')
    raveled_indices, raveled_mask = combine_words(two_words_mask, words_mask)

    for i in raveled_indices:
        two_index = i // len(words)
        third_index = i % len(words)
        two_groups = two_words_values[two_index]
        third_mask = words[third_index]
```

Now for each two word pair that corresponds with that two word mask, we must check if the third word comes last alphabetically, and if so we can move forward with our three word triplet.

```python
def main():
    ...
    for i in raveled_indices:
        ...
        combined_mask = raveled_mask[i]
        for entry in two_groups:
            if entry[-1] < third_mask:
                three_words.setdefault(combined_mask, []).append(entry + (third_mask,))

    print(len(three_words))
```

```shell
~ time python3 five-words.py
1272060
python3 five-words.py  111.64s user 20.47s system 79% cpu 2:46.01 total
```

We've got 1,272,060 three-word masks computed in 2:46. Fairly respectable, and the vectorization saved so much time that we don't even have to bother with it when selecting the fourth and fifth numbers to meet our 5 minute target.

<br />

### My Final Trick

We can use some bitwise operations and hashing here to find the last two words. We know that a completed set will cover 25 out of 26 letters, which means there is only one letter not used. Instead of iterating the word list against the list of three-word masks, we can iterate the alphabet against the list of three-word masks, combine them and invert the result to get a two-word mask. This is a huge time savings, going from essentially O(n^3) to O(26n). 

```python
def main():
    ...
    full_mask = 2**26-1
    for missing_letter in alphabet:
        missing_letter_mask = numberify(missing_letter)
        for mask, three_entries in three_words.items():
            if missing_letter_mask & mask != 0:
                continue
            fourth_fifth_mask = missing_letter_mask | mask
            inverted = fourth_fifth_mask ^ full_mask
```

And because we already computed all the pairs of words that correspond to a given two-word mask, all we have to do is look them up. Then we can check the order before adding the pairs onto our final total.

```python
def main():
    ...
    final_total = 0
    for missing_letter in alphabet:
        ...
        for mask, three_entries in three_words.items():
            ...
            if inverted in two_words:
                for three_entry in three_entries:
                    for two_entry in two_words[inverted]:
                        if three_entry[-1] < two_entry[0]:
                            final_total += 1

    print('final answer:', final_total)
```

```shell
~ time python3 five-words.py
final answer: 538
python3 five-words.py  195.82s user 19.36s system 87% cpu 4:04.76 total
```

And there you have it, 538 possible combinations, computed in just over 4 minutes. Using numpy throughout the whole program and optimizing the number of comparisons during the alphabetical pruning could speed it up a bit, but I already hit my 5 minute goal so this is left as an exercise for the reader. You can find my completed code [here](https://github.com/haondt/five-letters).

Moving everything to a language with actual 32 bit integers and contiguous arrays could speed things up too. I could probably get it under 1 minute, but as it is I'm happy with what I've come up with. How fast can you solve the problem? See if you can beat my solution. 

