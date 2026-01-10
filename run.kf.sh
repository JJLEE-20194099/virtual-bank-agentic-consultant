cd kafka
pkill -f kafka.Kafka
pkill -f zookeeper
nohup bin/zookeeper-server-start.sh config/zookeeper.properties > zk.log 2>&1 &
nohup bin/kafka-server-start.sh config/server.properties > kafka.log 2>&1 &
