# agents/recon_behavior.py
from GooglerAgent import GooglerAgent

class ReconAgent(GooglerAgent):
    def run(self):
        instructions = self.get_shared_resource('instructions')
        supporting_docs = self.get_shared_resource('supporting_docs')
        research_material = self.gather_research(instructions, supporting_docs)
        self.share_resource('research_material', research_material)
        self.log_info("Recon has gathered research materials.")

    def gather_research(self, instructions, supporting_docs):
        # Combine instructions and supporting_docs for better context
        combined_text = instructions + '\n' + supporting_docs
        search_queries = self.extract_keywords(combined_text)
        materials = []
        for query in search_queries:
            results = self.perform_search(query)
            for i, result in enumerate(results):
                if i >= 2:  # Limit to top 2 results per query
                    break
                summary = self.summarize_article(result['snippet'])
                citation = self.format_apa_citation(result)
                materials.append({'summary': summary, 'citation': citation})
        return materials

    def extract_keywords(self, text):
        # Use a language model to extract keywords
        prompt = f"Extract a list of key topics and keywords from the following text:\n\n{text}\n\nProvide the keywords as a comma-separated list."
        response = self.call_large_language_model(prompt)
        keywords = [kw.strip() for kw in response.split(',')]
        return keywords

    def perform_search(self, query):
        # Use the GooglerAgent's search capability
        search_results = self.search(query + ' scholarly articles')
        return search_results

    def summarize_article(self, text):
        # Summarize the text using the language model
        prompt = (
            "Summarize the following text using direct quotations where appropriate, "
            "and paraphrase the rest. Ensure all information is accurate:\n\n" + text
        )
        summary = self.call_large_language_model(prompt)
        return summary.strip()

    def format_apa_citation(self, result):
        # Format the citation in APA style using the search result data
        title = result.get('title', '')
        link = result.get('link', '')
        snippet = result.get('snippet', '')
        source = result.get('source', '')
        authors = result.get('authors', 'Author(s)')
        year = result.get('year', 'n.d.')
        citation = f"{authors} ({year}). {title}. Retrieved from {link}"
        return citation