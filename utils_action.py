from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext, SQLContext
from pyspark.util import fail_on_stopiteration, _parse_memory
from functools import reduce
from utils_transformation import getNumPartitions

'''RDD/rdd : resilient distributed dataset'''

def max(rdd): #return max value of rdd
    return rdd.max()

def min(rdd): #return min value of rdd
    return rdd.min()

def sum(rdd): #return sum value of elements in rdd
    return rdd.sum()

def count(rdd): #return nums of elements in rdd
    return rdd.count()

def mean(rdd): #return mean value of elements in rdd 
    return rdd.mean()

def variance(rdd): #return variance value of elements in rdd 
    return rdd.variance()

def stdev(rdd): #return standard deviation of elements in rdd
    return rdd.stats().stdev()

def top(rdd, num, key = None):
    return

def take(rdd, num): #Take the first num elements of the RDD
    items = []
    totalParts = getNumPartitions(rdd)
    partsScanned = 0

    while len(items) < num and partsScanned < totalParts:
        # The number of partitions to try in this iteration.
        # It is ok for this number to be greater than totalParts because
        # we actually cap it at totalParts in runJob.
        numPartsToTry = 1
        if partsScanned > 0:
            # If we didn't find any rows after the previous iteration,
            # quadruple and retry.  Otherwise, interpolate the number of
            # partitions we need to try, but overestimate it by 50%.
            # We also cap the estimation in the end.
            if len(items) == 0:
                numPartsToTry = partsScanned * 4
            else:
                # the first parameter of max is >=1 whenever partsScanned >= 2
                numPartsToTry = int(1.5 * num * partsScanned / len(items)) - partsScanned
                numPartsToTry = min(max(numPartsToTry, 1), partsScanned * 4)

        left = num - len(items)

        def takeUpToNumLeft(iterator):
            iterator = iter(iterator)
            taken = 0
            while taken < left:
                try:
                    yield next(iterator)
                except StopIteration:
                    return
                taken += 1

        p = range(partsScanned, min(partsScanned + numPartsToTry, totalParts))
        res = rdd.context.runJob(rdd, takeUpToNumLeft, p)

        items += res
        partsScanned += numPartsToTry

    return items[:num]

def first(rdd): #Return first elements of RDD
    return rdd.first()

def collectAsMap(rdd): 
    """
    Return the key-value pairs in this RDD to the master as a dictionary.
    """
    return dict(rdd.collect())



def aggregate(rdd, zeroValue, seqOp, combOp):
    seqOp = fail_on_stopiteration(seqOp)
    combOp = fail_on_stopiteration(combOp)
    def func(iterator):
        acc = zeroValue
        for obj in iterator:
            acc = seqOp(acc, obj)
        yield acc

    vals = rdd.mapPartitions(func).collect()
    return reduce(combOp, vals, zeroValue)


def fold(rdd, zeroValue, op):
    op = fail_on_stopiteration(op)
    def func(iterator):
        acc = zeroValue
        for obj in iterator:
            acc = op(acc, obj)
        yield acc
    
    vals = rdd.mapPartitions(func).collect()
    return reduce(op,vals, zeroValue)




