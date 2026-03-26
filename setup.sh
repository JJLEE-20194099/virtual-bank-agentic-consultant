sudo apt update
sudo apt install -y openjdk-11-jdk
java -version
cd /opt
sudo wget https://downloads.apache.org/kafka/3.8.0/kafka_2.12-3.8.0.tgz
sudo tar -xzf kafka_2.12-3.8.0.tgz
sudo mv kafka_2.12-3.8.0 kafka
sudo chown -R $USER:$USER kafka
echo 'export PATH=$PATH:/opt/kafka/bin' >> ~/.bashrc
source ~/.bashrc

kafka-storage.sh format \
  -t abcd-1234 \
  -c /opt/kafka/config/kraft/server.properties

kafka-server-start.sh /opt/kafka/config/kraft/server.properties

source ~/.bashrc
kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic transactions \
  --partitions 3 \
  --replication-factor 1

kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic transactions

kafka-topics.sh --bootstrap-server localhost:9092 --list

python3 /workspace/code/virtual-bank-agentic-consultant/backend/app/data/generator/generate.py
python3 /workspace/code/virtual-bank-agentic-consultant/backend/app/ingestion/kafka_consumer.py
python3 /workspace/code/virtual-bank-agentic-consultant/backend/app/ingestion/kafka_producer.py

sudo apt update
sudo apt install -y redis-server

redis-cli ping

pip install feast redis
feast version


service/feature_engine
mkdir feature_store
cd feature_store/repo

feast apply
feast materialize \
  $(date -u -d "5 months ago" +"%Y-%m-%dT%H:%M:%S") \
  $(date -u +"%Y-%m-%dT%H:%M:%S")

redis-cli
keys *

# Start redis => Start Kafka => Gen data & produce data => Consume data => feature_engine/job to create offline data => feast apply create features => feast materialize to push data to offline data


docker run -d \
  --name postgres \
  -e POSTGRES_USER=swin \
  -e POSTGRES_PASSWORD=swin \
  -e POSTGRES_DB=vbac \
  -p 5432:5432 \
  postgres

docker run -d --name redis -p 6379:6379 redis

docker run -d -p 8081:8080 adminer

docker rename festive_kirch adminer
docker network create swinnet
docker network connect swinnet postgres
docker network connect swinnet redis
docker network connect swinnet adminer

python save_trading_data.py
python append_new_stock_price.py
python calculate_portfolio.py
python gen_user_account.py

# Run behavior detection

cd backend

uvicorn main:app --host 0.0.0.0 --port 8080
sudo apt-get install redis-tools

docker-compose logs -f backend celery-worker celery-beat

cd /root/code/hackathon/virtual-bank-agentic-consultant
docker-compose down -v
docker-compose up -d --build
bash docker-init-data.sh