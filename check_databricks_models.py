"""
Check available Databricks AI models and endpoints
"""
from databricks.sdk import WorkspaceClient
import streamlit as st

def check_available_models():
    """Check what AI endpoints are available in your workspace"""
    try:
        # Load secrets
        token = st.secrets.databricks.token
        hostname = st.secrets.databricks.server_hostname
        
        print(f"\n{'='*60}")
        print("Checking Databricks Workspace for AI Models...")
        print(f"{'='*60}\n")
        
        # Connect to workspace
        client = WorkspaceClient(
            host=f"https://{hostname}",
            token=token
        )
        
        print("[OK] Connected to Databricks workspace\n")
        
        # List all serving endpoints
        print("Available Serving Endpoints:")
        print("-" * 60)
        
        endpoints = client.serving_endpoints.list()
        endpoint_list = list(endpoints)
        
        if not endpoint_list:
            print("[WARNING] No serving endpoints found in your workspace\n")
        else:
            for endpoint in endpoint_list:
                print(f"  * {endpoint.name}")
                if endpoint.config:
                    print(f"     State: {endpoint.state.ready if endpoint.state else 'Unknown'}")
                print()
        
        print(f"\nTotal endpoints found: {len(endpoint_list)}\n")
        
        # Try common Foundation Model endpoints
        print("Testing Common Foundation Model Endpoints:")
        print("-" * 60)
        
        common_models = [
            "databricks-dbrx-instruct",
            "databricks-meta-llama-3-70b-instruct",
            "databricks-meta-llama-3-1-70b-instruct",
            "databricks-mixtral-8x7b-instruct",
            "databricks-llama-2-70b-chat",
        ]
        
        available_models = []
        for model in common_models:
            try:
                # Try to get endpoint details
                endpoint = client.serving_endpoints.get(model)
                print(f"  [OK] {model} - AVAILABLE")
                available_models.append(model)
            except Exception as e:
                print(f"  [X] {model} - Not available")
        
        print()
        
        if available_models:
            print(f"[SUCCESS] Found {len(available_models)} available Foundation Models!")
            print("\nUpdate your .streamlit/secrets.toml with one of these:")
            print("-" * 60)
            for model in available_models:
                print(f'  model_endpoint = "{model}"')
        else:
            print("\n[WARNING] No Foundation Model APIs found")
            print("\nAlternative Options:")
            print("-" * 60)
            print("1. Check with your Databricks admin if Foundation Models are enabled")
            print("2. Create a custom model serving endpoint")
            print("3. Use Databricks SQL AI Functions (ai_query, ai_analyze, etc.)")
            print("4. Continue using Claude (external API)")
        
        print(f"\n{'='*60}\n")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}\n")
        print("Make sure your .streamlit/secrets.toml has valid credentials:")
        print("  - server_hostname")
        print("  - token")

if __name__ == "__main__":
    check_available_models()

