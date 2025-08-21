import os
from function_app import TopDeskClient
from dotenv import load_dotenv

# ------------------------------
# Example Usage
# ------------------------------
if __name__ == "__main__":
    load_dotenv()
    base_url = "https://cartaoelo.topdesk.net/tas/api"
    user = os.getenv("TOPDESK_USER")
    password = os.getenv("TOPDESK_API_KEY")
    if not user or not password:
        raise RuntimeError("TOPDESK_USER or TOPDESK_API_KEY not set in .env file.")
    client = TopDeskClient(
        base_url=base_url,
        username=user,
        password=password
    )

    # List incidents
    incidents = client.list_incidents()
    print(f"Found {len(incidents)} incidents")

    print(incidents[0]['id'])
    incident = client.get_incident_by_id(incidents[0]['id'])
    if incident:
        print(f"Incident {incident['id']}: {incident['status']} - {incident['request']}")

    #if incidents:
    #    print(incidents[0])

    # Get transaction assets
    #assets = client.get_transaction_assets(
    #    template_id="561F3666-E5F0-429E-9508-1AAD5DB6EE04",
    #    fields=["name", "volume-debito", "numero-do-chamado"]
    #)
    #print(f"Found {len(assets)} assets")
    #if assets:
    #    print(assets[0])

    # List changes
    changes = client.list_changes(fields="all")
    print(f"Found {len(changes)} changes")

    change = client.get_change_by_id(changes[0]['id'])
    if change:
        print(f"Change {change['id']}: {change['status']['name']} - {change['briefDescription']}")
    

    