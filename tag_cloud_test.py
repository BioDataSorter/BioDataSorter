import os
import numpy
import wordcloud

d = os.path.dirname(__file__)
cloud = wordcloud.WordCloud()
array = numpy.array([("hi", 6), ("seven"), 17])
cloud.generate_from_frequencies(array)  # <= what should go in the parentheses
