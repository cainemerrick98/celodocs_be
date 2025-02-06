from bs4 import Tag
import regex as re

def extract_page_content(tags:list[Tag]):
    page_content = ''
    for tag in tags:
        page_content += tag_to_content(tag)
        page_content += '\n\n'
    return page_content

def tag_to_content(tag:Tag):
    identifiers_and_extractors = [
        (is_text_element, extract_text),
        (is_list_element, extract_list),
        (is_pql_example, extract_pql_example), #special case of PQL examples
        (is_table_element, extract_table),
    ]

    for identifier, extractor in identifiers_and_extractors:
        if identifier(tag):
            return extractor(tag)
    
    raise ValueError(f'{Tag} has no identifier function')

def is_text_element(tag:Tag):
    return tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'code', 'pre']

def is_list_element(tag:Tag):
    return tag.name in ['ul', 'ol']

def is_table_element(tag:Tag):
    return tag.name == 'table'

def is_pql_example(tag:Tag):
    if tag.name == 'table':
        if tag.find_next('table') is not None:
            return tag.find_next('table').find_next('th').get_text(strip=True) == 'Query'
    return False

def extract_text(tag:Tag):
    text = re.sub(r'\s([^\w\s])', r'\1', tag.get_text(separator=' ', strip=True))
    text = text.replace('\n', '')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_list(tag:Tag):
    items = map(lambda x: extract_text(x), tag.find_all('li'))
    return ','.join(items)

def extract_table(tag:Tag):
    rows = [[extract_text(value) for value in row] for row in tag.find_all('tr')]
    rows = [[value for value in row if value != ""] for row in rows]
    csv_table = [','.join(row) for row in rows]
    csv_table = '\n'.join(csv_table)
    return csv_table

def extract_pql_example(tag:Tag):
    description = extract_text(tag.find_all('p')[1])
    queries = list(map(lambda x: extract_text(x), tag.find_all('pre')))
    
    sub_tables = tag.find_all('table')
    input_tables = list(map(extract_table, sub_tables[2:-2]))
    output_table = extract_table(sub_tables[-1])
    
    pql_example = (
        "PQL Example"
        f"{description}\n\n"
        "Queries:\n" + ",\n".join(queries) + "\n\n"
        "Input tables:\n" + "\n\n".join(input_tables) + "\n\n"
        f"Output:\n{output_table}"
    )  

    return pql_example



