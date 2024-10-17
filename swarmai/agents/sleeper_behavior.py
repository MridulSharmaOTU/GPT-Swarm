# agents/sleeper_behavior.py
from AgentBase import BaseAgent
import re

class SleeperAgent(BaseAgent):
    def run(self):
        bond_process = self.get_shared_resource('bond_process')
        research_material = self.get_shared_resource('research_material')
        self.generate_replication_instructions(bond_process)
        self.validate_citations(research_material)
        self.log_info("Sleeper has generated replication instructions and validated citations.")

    def generate_replication_instructions(self, bond_process):
        prompt = (
            "Based on the following description of the process, provide detailed, step-by-step instructions "
            "for a user to replicate the task. The instructions should be clear and easy to follow.\n\n"
            + bond_process
        )
        steps = self.call_large_language_model(prompt)
        with open('replication_instructions.txt', 'w') as f:
            f.write(steps)
        self.log_info("Sleeper saved replication instructions to replication_instructions.txt.")

    def validate_citations(self, research_material):
        incorrect_citations = []
        for item in research_material:
            citation = item['citation']
            if not self.check_apa_format(citation):
                incorrect_citations.append(citation)
        if incorrect_citations:
            self.log_error("The following citations are not in correct APA format:")
            for citation in incorrect_citations:
                self.log_error(citation)
        else:
            self.log_info("All citations are correctly formatted in APA style.")

    def check_apa_format(self, citation):
        # Simple regex pattern to check APA citation format
        pattern = r"^[A-Za-z ,.&']+ \(\d{4}\)\. .+\.$"
        return bool(re.match(pattern, citation))