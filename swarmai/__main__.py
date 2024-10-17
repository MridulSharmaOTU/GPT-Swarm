import sys
import os
import json
from pathlib import Path
sys.path.append('..')

from swarmai.Swarm import Swarm

# Import custom agents
from agents.handler_behavior import HandlerAgent
from agents.recon_behavior import ReconAgent
from agents.bond_behavior import BondAgent
from agents.sleeper_behavior import SleeperAgent

def load_keys():
    keys_file = Path(__file__).parent.parent / "keys.json"
    with open(keys_file) as f:
        keys = json.load(f)
    os.environ["OPENAI_API_KEY"] = keys["OPENAI_API_KEY"]
    try:
        os.environ["GOOGLE_API_KEY"] = keys["GOOGLE_API_KEY"]
        os.environ["CUSTOM_SEARCH_ENGINE_ID"] = keys["CUSTOM_SEARCH_ENGINE_ID"]
        os.environ["GOOGLE_CSE_ID"] = keys["CUSTOM_SEARCH_ENGINE_ID"]
    except:
        print("WARNING: GOOGLE_API_KEY and GOOGLE_CSE_ID not found in keys.json. Googler agent will be treated as a general-purpose agent.")

    try:
        os.environ["APIFY_API_TOKEN"] = keys["APIFY_API_TOKEN"]
    except:
        print("WARNING: APIFY_API_TOKEN not found in keys.json. WebScraper agent will not work.")

def run_swarm():
    # Initialize agents
    handler = HandlerAgent()
    recon = ReconAgent()
    bond = BondAgent()
    sleeper = SleeperAgent()

    # Shared resources
    shared_resources = {}

    # Shared resource manager functions
    def share_resource(key, value):
        shared_resources[key] = value

    def get_shared_resource(key):
        return shared_resources.get(key)

    # Assign shared resource methods to agents
    for agent in [handler, recon, bond, sleeper]:
        agent.share_resource = share_resource
        agent.get_shared_resource = get_shared_resource
        agent.api_key = os.environ.get("OPENAI_API_KEY")

    # Load input files
    input_files_dir = Path(__file__).parent.parent / "input_files"
    input_files = [str(f) for f in input_files_dir.glob('*') if f.is_file()]
    if not input_files:
        print("No input files found in the 'input_files' directory.")
        return

    # Handler processes input files
    shared_resources['input_files'] = input_files
    handler.run()

    # Check if instructions were extracted
    if not shared_resources.get('instructions'):
        print("Handler did not extract any instructions.")
        return

    # Recon uses instructions and supporting documents from Handler
    recon.run()

    # Bond synthesizes instructions and research_material
    bond.run()

    # Assume Bond's process description is available
    bond_process_description = "Detailed description of the steps Bond took to complete the task."
    shared_resources['bond_process'] = bond_process_description

    # Sleeper generates replication instructions and validates citations
    sleeper.run()

    # Optional: Save outputs to files or handle as needed
    outputs_dir = Path(__file__).parent.parent / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    # Save the instructions and supporting documents
    instructions = shared_resources.get('instructions', '')
    supporting_docs = shared_resources.get('supporting_docs', '')
    with open(outputs_dir / 'instructions.txt', 'w') as f:
        f.write(instructions)
    with open(outputs_dir / 'supporting_documents.txt', 'w') as f:
        f.write(supporting_docs)

    print("Execution completed. Outputs are saved in the 'outputs' directory.")

if __name__ == "__main__":
    load_keys()
    run_swarm()