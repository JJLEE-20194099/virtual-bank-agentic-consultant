cd /root/code/hackathon/virtual-bank-agentic-consultant
docker rmi -f $(docker images -a -q)
docker-compose down -v
docker-compose up -d --build