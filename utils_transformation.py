from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext, SQLContext
from pyspark.util import fail_on_stopiteration, _parse_memory
from functools import reduce
from pyspark.serializers import AutoBatchedSerializer, BatchedSerializer, NoOpSerializer, \
    CartesianDeserializer, CloudPickleSerializer, PairDeserializer, PickleSerializer, \
    pack_long, read_int, write_int

class RDD(object):

    """
    A Resilient Distributed Dataset (RDD), the basic abstraction in Spark.
    Represents an immutable, partitioned collection of elements that can be
    operated on in parallel.
    """

    def __init__(self, jrdd, ctx, jrdd_deserializer=AutoBatchedSerializer(PickleSerializer())):
        self._jrdd = jrdd
        self.is_cached = False
        self.is_checkpointed = False
        self.has_resource_profile = False
        self.ctx = ctx
        self._jrdd_deserializer = jrdd_deserializer
        self._id = jrdd.id()
        self.partitioner = None

def split_space(x):
    ###Return txt to colletion of elements
    return x.split(' ')

def padding_word(x):
    return (x,1)

def add(x, y):
    return x + y

def glom(rdd):
    return rdd.glom()

def getNumPartitions(rdd): #Return the number of partitions in RDD
    return rdd._jrdd.partitions().size()

def zip(rdd1, rdd2):
    """
        Zips this RDD with another one, returning key-value pairs with the
        first element in each RDD second element in each RDD, etc. Assumes
        that the two RDDs have the same number of partitions and the same
        number of elements in each partition (e.g. one was made through
        a map on the other).
    """
    def get_batch_size(ser):
        if isinstance(ser, BatchedSerializer):
            return ser.batchSize
        return 1  # not batched

    def batch_as(rdd, batchSize):
        return rdd._reserialize(BatchedSerializer(PickleSerializer(), batchSize))

    my_batch = get_batch_size(rdd1._jrdd_deserializer)
    other_batch = get_batch_size(rdd2._jrdd_deserializer)
    if my_batch != other_batch or not my_batch:
        # use the smallest batchSize for both of them
        batchSize = min(my_batch, other_batch)
        if batchSize <= 0:
            # auto batched or unlimited
            batchSize = 100
        rdd2 = batch_as(rdd2, batchSize)
        rdd1 = batch_as(rdd1, batchSize)

    if getNumPartitions(rdd1) != rdd2.getNumPartitions(rdd1):
        raise ValueError("Can only zip with RDD which has the same number of partitions")

    # There will be an Exception in JVM if there are different number
    # of items in each partitions.
    pairRDD = rdd1._jrdd.zip(rdd2._jrdd)
    deserializer = PairDeserializer(rdd1._jrdd_deserializer,
                                    rdd2._jrdd_deserializer)
    return RDD(pairRDD, rdd1.ctx, deserializer)


def join(rdd1, rdd2, numPartitions=None):

    
    def python_join(rdd, other, numPartitions):
        def _do_python_join(rdd1, rdd2, numPartitions, dispatch):
            vs = rdd1.mapValues(lambda v: (1, v))
            ws = rdd2.mapValues(lambda v: (2, v))
            return vs.union(ws).groupByKey(numPartitions).flatMapValues(lambda x: dispatch(x.__iter__()))

        def dispatch(seq):
            vbuf, wbuf = [], []
            for (n, v) in seq:
                if n == 1:
                    vbuf.append(v)
                elif n == 2:
                    wbuf.append(v)
            return ((v, w) for v in vbuf for w in wbuf)
        return _do_python_join(rdd, other, numPartitions, dispatch)
    
    return python_join(rdd1, rdd2, numPartitions)


    

    