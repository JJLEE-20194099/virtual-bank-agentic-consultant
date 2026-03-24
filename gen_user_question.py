import requests
from backend.app.utils.stock import generate_question_set
url = f"http://localhost:8080/api/v1/user/list/"
res = requests.get(url)
if res.status_code == 200:
    users = res.json()

for user_id in users[:100]:

    url = f"http://localhost:8080/api/v1/user/summary/{user_id}"
    res = requests.get(url)
    if res.status_code == 200:
        portfolio_data = res.json()
        portfolio_symbols = list(portfolio_data["detail"].keys())

        questions = generate_question_set(portfolio_symbols)

        print(questions)

        break



