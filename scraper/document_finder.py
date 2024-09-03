from .base_scraper import BaseScraper
import re

class DocumentFinder(BaseScraper):
    def __init__(self, base_url, headers, search_criteria, tse_list, use_id_list):
        super().__init__(base_url, headers)
        self.search_criteria = search_criteria
        self.tse_list = tse_list
        self.use_id_list = use_id_list #boolean determining if we are using the id list
        

    def find_documents(self):
        """Finds and returns a list of document links and their metadata."""

        html = self.get_html(self.base_url, method='POST', data=self.search_criteria)
        if html:
            self.save_html(html)
            soup = self.parse_html(html)
            document_info = []
            for row in soup.find_all('tr', class_='even'):
                title_td = row.find('td', class_='title')
                if title_td:
                    a_tag = title_td.find('a', href=True)
                    if a_tag and a_tag['href'].endswith('.pdf'):
                        document_metadata = {
                            "company_name": row.find('td', class_='companyname').text.strip(),
                            "company_code": row.find('td', class_='code').text.strip()[:4],
                            "file_timestamp": row.find('td', class_='time').text.strip(),
                            "document_name": a_tag.text.strip()
                        }
                        if not self.use_id_list:
                            document_info.append((a_tag['href'], document_metadata))
                        else:
                            if document_metadata["company_code"] in self.tse_list:
                                document_info.append((a_tag['href'], document_metadata))
                            
                            else:
                                print(f"Company code {document_metadata['company_code']} not in TSE list.")
            for row in soup.find_all('tr', class_='odd'):
                title_td = row.find('td', class_='title')
                if title_td:
                    a_tag = title_td.find('a', href=True)
                    if a_tag and a_tag['href'].endswith('.pdf'):
                        document_metadata = {
                            "company_name": row.find('td', class_='companyname').text.strip(),
                            "company_code": row.find('td', class_='code').text.strip()[:4],
                            "file_timestamp": row.find('td', class_='time').text.strip(),
                            "document_name": a_tag.text.strip()
                        }
                        if not self.use_id_list:
                            document_info.append((a_tag['href'], document_metadata))
                        else:
                            if document_metadata["company_code"] in self.tse_list:
                                document_info.append((a_tag['href'], document_metadata))
                            
                            else:
                                print(f"Company code {document_metadata['company_code']} not in TSE list.")
            return document_info
        return []

    def _matches_logic(self, document_name, filter_query):
        """Evaluate AND/OR logic based on filter_query."""
        if not filter_query:
            return True

        def evaluate(match):
            return str(self._evaluate_expression(match.group(1), document_name)).lower()

        while '(' in filter_query:
            filter_query = re.sub(r'\(([^()]+)\)', evaluate, filter_query)

        return self._evaluate_expression(filter_query, document_name)

    def _evaluate_expression(self, expression, document_name):
        expression = expression.strip()
        if "+" in expression:
            return all(self._evaluate_expression(term, document_name) for term in expression.split("+"))
        elif "," in expression:
            return any(self._evaluate_expression(term, document_name) for term in expression.split(","))
        else:
            return expression in document_name

    def apply_filters(self, documents, filter_query):
        filtered_documents = []
        for link, metadata in documents:
            if self._matches_logic(metadata["document_name"].lower(), filter_query.lower()):
                filtered_documents.append((link, metadata))
        return filtered_documents

    def save_html(self, html):
        with open("output.html", "w", encoding="utf-8") as f:
            f.write(html)
