from fastapi import APIRouter

router = APIRouter()

def fetch_from_postgres(user_id):
    return None

@router.get("/{user_id}")
def get_transactions(user_id: str):
    return fetch_from_postgres(user_id)