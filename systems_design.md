# Systems Design Problem

## Design Choices

I chose a collection of out-of-the-box frameworks to design this metrics system. 

### Collection Service

This is a good use case for Kafka since it guarantees message ordering-- that is, messages will be stored in the log in the same order that they are produced. In addition, Kafka is highly scalable and fault tollerent since each Topic is partitioned by message key. Kafka self manages partition replication based on configuration settings, and handles leader election in case of failure. The size of each log is only limited by the memory of the machine it lives on. Kafka's pub-sub model also introduces consumer groups which allows for distributed processing of messages.

Once in the queue, messages are read by a Streaming instance. In my illustration I chose Spark Streaming, but other Streaming frameworks could be used. I thought Spark was a good choice because it has a robust API that already has our desired metrics (average, min, max, median). Median is tricky since it is less intuitive how to combine the results of a stream across a distributed network. Luckily, the Spark API implements `approxQuantile` which uses an approximate algorithm to produce a desired quantile, in our case 0.5 for the medium. Here I make a tradeoff for accuracy to gain a speed advantage. The error bound of the algorithm is configurable to meet stricter accuracy demands. 

Finally, Spark Streaming is implemented as configurable micro batches which would allows us to begin reading from the start of an hour window, stop once reaching the next window, and computing metrics on the current window's data. 

The following is Spark-esque psuedo code for aggregating the desired messages:
```
#initialize stream
message_stream = Kafka.createDirectStream(...)

#map to key-value pairs; keys are a tuple of endpoint parameters, values are the apps' response times
structured_messages = message_stream.map((app_id, response_date, response_hour), response_time)

#compute metrics
averages = structured_messages.reduceByKey(SparkAPI.average_function)
mins = structured_messages.reduceByKey(SparkAPI.min_function)
maxs = structured_messages.reduceByKey(SparkAPI.max_function)
medians = structured_messages.reduceByKey(SparkAPI.approxQuantile, 0.5)

#write metrics to DB
averages.forEachRDD(write_to_DB_function)
mins.forEachRDD(write_to_DB_function)
maxs.forEachRDD(write_to_DB_function)
medians.forEachRDD(write_to_DB_function)
```

#### Unavailability Scenarios

Using Kafka alows us to configure the number of partition replicas which are kept up to date by the partition leader. Instances of failure are automatically handled by switching to a healthy replica.

Spark worker and driver failures are also handled automatically. Spark uses a write-ahead log to ensure zero data loss.

#### High System Utilization

Out-of-the-box Kafka is well designed for high throughput systems. Some benchmarks place it at being able to write 1 million records/sec, with a decrease in speed if we want to ensure zero data loss in the event of a partition leader failure. So our system would reasonably be able to withstand 10-100x the message velocity it was designed for. 

However, increasing utilization enough would create a backlog of messages on the application machines. Further governance of Kafka would address this issue, particularly splitting out traffic to additional topics. Since topics are an abstraction of write-ahead logs, we'd be able to handle more writes/reads. This would also require changes to the Spark code. 

###Query Service

I chose Cassandra because it is write optimized and highly scalable, skewing AP of the CAP theorem. It guarantees eventual consistency which would be reasonable given the system specification. Below is the table schema:
```
CREATE TABLE query_service.app_metrics (
	app_id text,
	date datetime,
	hour int,
	average float,
	min float,
	max float,
	median float,
) WITH bloom_filter_fp_chance = 0.01

```

Additionally, I introduced a cache layer to live in between the endpoint and Cassandra to speed up response times. 

## Illustration

<img src="img/sytem_blocks_and_notes.png" width="1000px">


