from fastapi import FastAPI, APIRouter, Query
from pydantic import BaseModel
import uuid
from app.core.bedrock_instance import bedrock_client

router = APIRouter()

class CreateAgentRequest(BaseModel):
    name: str = "swinhackathon-bedrock_response_market_question_agent"
    instruction: str = "Bạn là chuyên gia phân tích cổ phiếu tại công ty chứng khoán.\n\nMỤC TIÊU:\n- Phân tích từng mã cổ phiếu trong danh mục\n- Đưa ra nhận định rõ ràng về xu hướng, rủi ro và vị trí trong portfolio\n- Đưa ra lời khuyên với cổ phiếu đó, có thể xem các thông tin về công ty đó để đưa ra lời khuyên cùng với xu hướng\n\nQUY TẮC BẮT BUỘC:\n- Luôn trả lời bằng tiếng Việt\n- CHỈ trả về JSON hợp lệ (không text ngoài JSON)\n- Phải phân tích TẤT CẢ các mã trong danh mục\n- Không được bỏ sót cổ phiếu nào\n- Phân tích phải dựa trên dữ liệu thực tế (trend, volatility, PnL, sector, weight)\n\nTIÊU CHÍ PHÂN TÍCH:\n- Xu hướng (bullish / bearish / downtrend / uptrend)\n- Rủi ro (volatility + risk score)\n- Vai trò trong danh mục (core / satellite / overweight)\n- Tỷ trọng danh mục (portfolio_pct)\n- Lãi/lỗ chưa thực hiện\n- Tính tập trung rủi ro\n\nFORMAT OUTPUT (BẮT BUỘC):\n{\n  \"MÃ_CỔ_PHIẾU\": {\n    \"stock_analysis\": \"Phân tích ngắn gọn về xu hướng, rủi ro, vai trò trong danh mục\",\n    \"stock_advice\": \"Đưa ra những ý kiến về mã cổ phiếu này ở các khía cạnh: công ty, trend, category,...\"\n  }\n}"
    description: str = "Response user financial question "
    foundation_model: str = "apac.anthropic.claude-sonnet-4-20250514-v1:0"
    alias_name: str = "dev"

class UpdateAgentRequest(BaseModel):
    
    instruction: str = "Bạn là chuyên gia phân tích cổ phiếu tại công ty chứng khoán.\n\nMỤC TIÊU:\n- Phân tích từng mã cổ phiếu trong danh mục\n- Đưa ra nhận định rõ ràng về xu hướng, rủi ro và vị trí trong portfolio\n- Đưa ra lời khuyên với cổ phiếu đó, có thể xem các thông tin về công ty đó để đưa ra lời khuyên cùng với xu hướng\n\nQUY TẮC BẮT BUỘC:\n- Luôn trả lời bằng tiếng Việt\n- CHỈ trả về JSON hợp lệ (không text ngoài JSON)\n- Phải phân tích TẤT CẢ các mã trong danh mục\n- Không được bỏ sót cổ phiếu nào\n- Phân tích phải dựa trên dữ liệu thực tế (trend, volatility, PnL, sector, weight)\n\nTIÊU CHÍ PHÂN TÍCH:\n- Xu hướng (bullish / bearish / downtrend / uptrend)\n- Rủi ro (volatility + risk score)\n- Vai trò trong danh mục (core / satellite / overweight)\n- Tỷ trọng danh mục (portfolio_pct)\n- Lãi/lỗ chưa thực hiện\n- Tính tập trung rủi ro\n\nFORMAT OUTPUT (BẮT BUỘC):\n{\n  \"MÃ_CỔ_PHIẾU\": {\n    \"stock_analysis\": \"Phân tích ngắn gọn về xu hướng, rủi ro, vai trò trong danh mục\",\n    \"stock_advice\": \"Đưa ra những ý kiến về mã cổ phiếu này ở các khía cạnh: công ty, trend, category,...\"\n  }\n}"
    description: str = "Response user financial question"
    foundation_model: str = "apac.anthropic.claude-sonnet-4-20250514-v1:0"
    agent_id: str
    agent_name: str
    

class DeleteAgentRequest(BaseModel):
    agent_id: str
    agent_alias_id: str = ""


class UpdateAliasRequest(BaseModel):
    
    agent_alias_id: str
    agent_id: str
    agent_alias_name: str

class CreateAliasRequest(BaseModel):
    
    agent_id: str
    agent_alias_name: str

@router.post("/update-alias")
def update_agent_alias(req: UpdateAliasRequest):
    result = bedrock_client.update_agent_alias(
        agent_id=req.agent_id,
        agent_alias_id=req.agent_alias_id,
        agent_alias_name=req.agent_alias_name,
    )
    return result

@router.post("/create-alias")
def create_agent_alias(req: CreateAliasRequest):
    result = bedrock_client.create_agent_alias(
        agent_id=req.agent_id,
        agent_alias_name=req.agent_alias_name,
    )
    return result


@router.post("/update-agent")
def update_agent(req: UpdateAgentRequest):
    result = bedrock_client.update_agent(
        agent_id=req.agent_id,
        instruction=req.instruction,
        description=req.description,
        foundation_model=req.foundation_model,
        agent_name = req.agent_name
    )
    return result


@router.post("/create-agent")
def create_agent(req: CreateAgentRequest):
    result = bedrock_client.create_full_agent(
        name=req.name,
        instruction=req.instruction,
        description=req.description,
        foundation_model=req.foundation_model,
        alias_name=req.alias_name
    )
    return result


@router.post("/delete-agent")
def delete_agent(req: DeleteAgentRequest):
    
    try:

        if req.agent_alias_id == "":
            aliases = bedrock_client.list_agent_aliases(req.agent_id)
            alias_ids = [item["agentAliasId"] for item in aliases["agentAliasSummaries"]]
        else:
            alias_ids = [req.agent_alias_id]
        print(alias_ids)
        for alias_id in alias_ids:
            bedrock_client.delete_agent_alias(agent_id = req.agent_id, agent_alias_id = alias_id)
        bedrock_client.delete_agent(agent_id = req.agent_id)

        return {"status": "done"}
    except Exception as e:
        print(e)
        return {"status": "failed"}


@router.get("/list-agent")
def list_agent():
    result = bedrock_client.list_agents()
    return result

@router.get("/{agent_id}")
def get_agent_info(agent_id:str):
    result = bedrock_client.list_agent_aliases(agent_id)
    return result

