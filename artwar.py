import re
from pyspark import SparkSession


# returns True if the `line` is the heading (starts with a Roman number followed by the dot)
# or the "THE END" marker
def is_heading(line):
    return re.match(r'^[IVX]+\..*', line) or line.startswith("THE END")


sc = SparkSession
# create an RDD with the lines of the text
aowTextRDD = sc.textFile('data/artwar.1b.txt')

# number each line using `zipWithIndex`
# and select the heading lines togehter with their indexes

chaptersAndBeginnings = aowTextRDD.zipWithIndex().filter(lambda (line, index): is_heading(line)).collect()
    
display(chaptersAndBeginnings)

# # let's create some useful intermediate variables

# chapterBeginnings = [ i for (title,i) in chaptersAndBeginnings]
# chapterTitles = [ title for (title,i) in chaptersAndBeginnings[0:-1]]
# noOfChapters = len(chapterTitles)

# print("Number of chapters: %s" % noOfChapters)
# print("Chapter titles: %s" % chapterTitles)
# print("Chapter start lines: %s " % chapterBeginnings)