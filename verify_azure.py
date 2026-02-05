"""
Verification script for Azure OpenAI Integration.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Ensure we are using Azure
os.environ["LLM_PROVIDER"] = "azure"

from app.services.llm_client import llm_client
from app.services.prompt_service import prompt_service

async def main():
    print("🚀 Testing Azure OpenAI Connection...")
    print(f"   Base URL: {os.getenv('LLM_AZURE_BASE_URL')}")
    print(f"   Deployment: {os.getenv('LLM_AZURE_DEPLOYMENT')}")
    
    system = prompt_service.get_system_prompt("en")
    user = prompt_service.format_story_prompt("A robot learning to paint in a quiet studio.", style="manga")
    
    try:
        print("\n⏳ Sending request to Azure...")
        result, usage = await llm_client.generate_json(system, user)
        print("✅ Azure Response Received!")
        print(f"   Usage: {usage}")
        print(f"   Pages: {len(result.get('pages', []))}")
        
    except Exception as e:
        print(f"❌ Azure Test Failed: {e}")
        # Print full traceback if needed
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
