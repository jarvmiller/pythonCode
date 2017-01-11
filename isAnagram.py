def isAnagram(phrase1, phrase2):  # no special characters pls
	word1, word2 = phrase1.lower(), phrase2.lower()
	word1, word2 = re.sub(' ', '', word1), re.sub(' ', '', word2)

	if set(word1) != set(word2):
		return False
	for letter in set(word1):
		if word1.count(letter) != word2.count(letter):
			return False

	return True


def isAnagram2(phrase1, phrase2):
	word1, word2 = phrase1.lower(), phrase2.lower()
	word1, word2 = re.sub(' ', '', word1), re.sub(' ', '', word2)

	return sorted(word1) == sorted(word2)


def isAnagram3(phrase1, phrase2):
	word1, word2 = phrase1.lower(), phrase2.lower()
	word1, word2 = re.sub(' ', '', word1), re.sub(' ', '', word2)

	if set(word1) != set(word2):
		return False
	
	letterCount = {}
	for char in word1:
		try:
			letterCount[char] += 1
		except KeyError:
			letterCount[char] = 1

	for char in word2:
		letterCount[char] -= 1

	return sum(letterCount.values()) == 0
