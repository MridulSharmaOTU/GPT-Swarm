# agents/bond_behavior.py
from AgentBase import BaseAgent
import os

class BondAgent(BaseAgent):
    def run(self):
        instructions = self.get_shared_resource('instructions')
        research_material = self.get_shared_resource('research_material')
        outputs = self.execute_task(instructions, research_material)
        self.share_resource('outputs', outputs)
        self.log_info("Bond has completed the assigned task and produced outputs.")

    def execute_task(self, instructions, research_material):
        # Create a detailed prompt for the language model
        prompt = self.create_prompt(instructions, research_material)
        response = self.call_large_language_model(prompt)
        output_files = self.generate_output_files(response, instructions)
        return output_files

    def create_prompt(self, instructions, research_material):
        # Prepare research materials for inclusion in the prompt
        research_text = ''
        for item in research_material:
            research_text += f"{item['summary']}\nCitations: {item['citation']}\n\n"
        prompt = (
            f"{instructions}\n\n"
            "Using the research materials provided, complete the assigned task. "
            "Ensure all outputs are of professional quality and adhere to formatting standards.\n\n"
            "Research Materials:\n" + research_text
        )
        return prompt

    def generate_output_files(self, response, instructions):
        # Determine the types of outputs needed from the instructions
        required_formats = self.determine_required_formats(instructions)
        output_files = []
        for fmt in required_formats:
            filename = f"output.{fmt}"
            with open(filename, 'w') as f:
                f.write(response)
            output_files.append(filename)
            self.log_info(f"Bond generated {filename}.")
            # Additional processing if needed (e.g., converting .tex to PDF)
            if fmt == 'tex':
                self.compile_latex(filename)
        return output_files

    def determine_required_formats(self, instructions):
        # Logic to determine required output formats from the instructions
        formats = []
        instructions_lower = instructions.lower()
        if '.tex' in instructions_lower or 'latex' in instructions_lower:
            formats.append('tex')
        if '.pdf' in instructions_lower or 'pdf' in instructions_lower:
            formats.append('pdf')
        if '.py' in instructions_lower or 'python code' in instructions_lower:
            formats.append('py')
        if '.pptx' in instructions_lower or 'powerpoint' in instructions_lower:
            formats.append('pptx')
        if '.docx' in instructions_lower or 'word document' in instructions_lower:
            formats.append('docx')
        # Add other formats as needed
        return formats

    def compile_latex(self, tex_file):
        # Compile .tex file to PDF using pdflatex or similar
        compile_command = f"pdflatex -interaction=nonstopmode {tex_file}"
        os.system(compile_command)
        self.log_info(f"Bond compiled {tex_file} to PDF.")