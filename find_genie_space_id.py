"""
Find your Genie Space IDs in Databricks
"""
from databricks.sdk import WorkspaceClient
import streamlit as st

def find_genie_spaces():
    """List all Genie Spaces in your Databricks workspace"""
    try:
        # Load secrets
        token = st.secrets.databricks.token
        hostname = st.secrets.databricks.server_hostname
        
        print("\n" + "="*60)
        print("Finding Genie Spaces in Your Databricks Workspace")
        print("="*60 + "\n")
        
        # Connect to workspace
        client = WorkspaceClient(
            host=f"https://{hostname}",
            token=token
        )
        
        print("[OK] Connected to Databricks workspace\n")
        
        # List Genie Spaces
        print("Available Genie Spaces:")
        print("-" * 60)
        
        try:
            # The API might return directly or need to access .spaces attribute
            spaces_response = client.genie.list_spaces()
            
            # Handle different response formats
            if hasattr(spaces_response, 'spaces'):
                spaces = list(spaces_response.spaces) if spaces_response.spaces else []
            elif hasattr(spaces_response, '__iter__'):
                spaces = list(spaces_response)
            else:
                spaces = []
            
            if not spaces:
                print("[WARNING] No Genie Spaces found in your workspace\n")
                print("You may need to:")
                print("1. Create a Genie Space in Databricks Console")
                print("2. Go to AI/BI -> Genie Spaces")
                print("3. Click 'Create Genie Space'")
                print("4. Configure it with your data")
            else:
                for idx, space in enumerate(spaces, 1):
                    print(f"\n{idx}. Genie Space found!")
                    
                    # Try to get ID - it might be 'id', 'space_id', or other
                    space_id = None
                    for attr in ['id', 'space_id', 'genie_space_id']:
                        if hasattr(space, attr):
                            space_id = getattr(space, attr)
                            break
                    
                    if space_id:
                        print(f"   Space ID: {space_id}")
                    else:
                        print(f"   Space ID: (checking attributes...)")
                        # Show all attributes to help debug
                        attrs = [a for a in dir(space) if not a.startswith('_')]
                        print(f"   Available attributes: {', '.join(attrs[:10])}")
                    
                    # Try to get name
                    for attr in ['name', 'display_name', 'title']:
                        if hasattr(space, attr):
                            val = getattr(space, attr)
                            if val:
                                print(f"   Name: {val}")
                                break
                    
                    # Try to get description
                    if hasattr(space, 'description') and space.description:
                        print(f"   Description: {space.description}")
                    
                    # Try to get warehouse
                    for attr in ['warehouse_id', 'sql_warehouse_id']:
                        if hasattr(space, attr):
                            val = getattr(space, attr)
                            if val:
                                print(f"   Warehouse: {val}")
                                break
                
                print(f"\n\nTotal Genie Spaces found: {len(spaces)}")
                print("\n" + "="*60)
                print("Copy one of the Space IDs above to your .streamlit/secrets.toml")
                print("="*60)
                print("\nAdd this line to [databricks] section:")
                
                # Try to show first space ID
                first_space_id = None
                if spaces:
                    for attr in ['id', 'space_id', 'genie_space_id']:
                        if hasattr(spaces[0], attr):
                            first_space_id = getattr(spaces[0], attr)
                            break
                
                if first_space_id:
                    print(f'genie_space_id = "{first_space_id}"')
                else:
                    print('genie_space_id = "YOUR_SPACE_ID_FROM_ABOVE"')
                print("\n")
                
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                print("[WARNING] Genie API not available in your workspace\n")
                print("Possible reasons:")
                print("1. Genie is not enabled (requires specific Databricks tier)")
                print("2. Your workspace doesn't have Genie Spaces feature")
                print("3. You don't have permissions to list Genie Spaces")
                print("\nContact your Databricks admin to enable Genie.")
            else:
                raise
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}\n")
        print("Make sure your .streamlit/secrets.toml has valid credentials:")
        print("  - server_hostname")
        print("  - token")
        print("\nAlso ensure you have databricks-sdk installed:")
        print("  pip install databricks-sdk")

if __name__ == "__main__":
    find_genie_spaces()

