import boto3
import json
import time
from dotenv import load_dotenv      
import os
load_dotenv()


aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region_name=os.getenv("AWS_REGION", "us-east-1")
bedrock_role = os.getenv("BEDROCK_ROLE")

class BedrockClient:
    def __init__(self, region_name="us-east-1"):

        self.bedrock_agent = None
        self.bedrock_runtime = None
    
    def setup(self):
        # session = boto3.Session(
        #     aws_access_key_id=aws_access_key_id,
        #     aws_secret_access_key=aws_secret_access_key,
        #     region_name=region_name
        # )


        self.bedrock_agent = boto3.client("bedrock-agent", region_name=region_name)
        self.bedrock_runtime = boto3.client("bedrock-agent-runtime", region_name=region_name)

    def update_agent(
        self,
        agent_id:str,
        instruction: str,
        description: str,
        foundation_model: str,
        agent_name:str
    ):
        response = self.bedrock_agent.update_agent(
            agentId=agent_id,
            instruction=instruction,
            description=description,
            foundationModel=foundation_model,
            agentName = agent_name,
            agentResourceRoleArn=bedrock_role
        )

        return response
    
    def create_agent(
        self,
        name: str,
        instruction: str,
        description: str,
        foundation_model: str,
        idle_session_ttl: int = 1800,
    ):
        response = self.bedrock_agent.create_agent(
            agentName=name,
            instruction=instruction,
            description=description,
            foundationModel=foundation_model,
            idleSessionTTLInSeconds=idle_session_ttl,
            agentResourceRoleArn=bedrock_role
        )

        return response["agent"]["agentId"]


    def delete_agent(self, agent_id: str):
        return self.bedrock_agent.delete_agent(agentId=agent_id)

    def delete_agent_alias(self, agent_id, agent_alias_id):
        return self.bedrock_agent.delete_agent_alias(agentId=agent_id, agentAliasId=agent_alias_id)

    def get_agent(self, agent_id: str):
        return self.bedrock_agent.get_agent(agentId=agent_id)


    def list_agents(self, max_results: int = 50):
        return self.bedrock_agent.list_agents(maxResults=max_results)

    def list_agent_aliases(self, agent_id: str):
        return self.bedrock_agent.list_agent_aliases(agentId=agent_id)

    def prepare_agent(self, agent_id: str):
        return self.bedrock_agent.prepare_agent(agentId=agent_id)

    def create_agent_alias(self, agent_id: str, name: str):
        response = self.bedrock_agent.create_agent_alias(
            agentId=agent_id,
            agentAliasName=name,
        )
        return response["agentAlias"]["agentAliasId"]

    def update_agent_alias(self, agent_id: str, agent_alias_id: str, agent_alias_name: str):
        response = self.bedrock_agent.update_agent_alias(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            agentAliasName = agent_alias_name
        )

    def invoke_agent(self, agent_id: str, agent_alias_id: str, session_id: str, input_text: str, session_state):
        response = self.bedrock_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=input_text,
            sessionState=session_state
        )

        full_text = ""

        print(agent_id, agent_alias_id)

        for event in response["completion"]:
            if "chunk" in event:
                chunk = event["chunk"]
                if "bytes" in chunk:

                    text = chunk["bytes"].decode("utf-8")
                    yield text + " "

                    full_text += text

    def offline_invoke_agent(self, agent_id: str, agent_alias_id: str, session_id: str, input_text: str, session_state):
        response = self.bedrock_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=input_text,
            sessionState=session_state
        )

        output = []

        print(agent_id, agent_alias_id)

        for event in response["completion"]:
            if "chunk" in event:
                chunk = event["chunk"]
                if "bytes" in chunk:
                    output.append(chunk["bytes"].decode("utf-8"))

        return "".join(output)
        
                    

    def create_full_agent(
        self,
        name: str,
        instruction: str,
        description: str,
        foundation_model: str,
        alias_name: str,
    ):
        agent_id = self.create_agent(name, instruction, description, foundation_model)
        time.sleep(5)  

        self.prepare_agent(agent_id)
        time.sleep(10) 

        alias_id = self.create_agent_alias(agent_id, alias_name)

        return {
            "agent_id": agent_id,
            "alias_id": alias_id,
        }