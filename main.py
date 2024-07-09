import os
import re

from bs4 import BeautifulSoup, Tag


def extract_values(file_path: str):
    with open(f"data/{file_path}", "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, 'html.parser')
        text = soup.get_text()

        match = re.search(r'F\(X\)\s*=\s*([\d\+\-\*x\s]+)', text)
        if match:
            function_str = match.group(1)
            coefficients = re.findall(r'(\d+)\s*x(\d+)', function_str)
            return {f'x{var}': int(coeff) for coeff, var in coefficients}


def extract_tables_from_html(file_path: str):
    with open(f"data/{file_path}", "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, 'html.parser')
        tables = soup.find_all("table", class_="table table-bordered table-center")
        filtered_tables = []

        if tables:
            for table in tables:
                if table.find("td", bgcolor="FFA0A0"):
                    filtered_tables.append(table)

            if tables[-1] not in filtered_tables:
                filtered_tables.append(tables[-1])

        return filtered_tables


def transform_table(table, target_values):
    # Добавляем строку сверху
    num_columns = len(table.find_all('tr')[0].find_all(['td', 'th']))
    header_row = Tag(name='tr')

    c_cell = Tag(name='td')
    c_cell.string = 'C'
    header_row.append(c_cell)

    dash_cell = Tag(name='td')
    dash_cell.string = '-'
    header_row.append(dash_cell)

    for i in range(num_columns - 2):
        cell = Tag(name='td')
        cell.string = str(target_values.get(f'x{i + 1}', 0))
        header_row.append(cell)

    table.insert(0, header_row)

    # Добавляем столбец слева
    rows_len = len(table.find_all('tr'))
    for i, row in enumerate(table.find_all('tr')):
        first_cell = Tag(name='td')
        if i == 0 or i == 1 or i == rows_len - 1:
            first_cell.string = ''
        else:
            variable_name = row.find_all('td')[0].get_text().strip()
            first_cell.string = str(target_values.get(variable_name, 0))
        row.insert(0, first_cell)

    return table


def parse():
    html_files = ["data1.html", "data2.html", "data3.html"]
    output_dir = "extracted_tables"

    for html_file in html_files:
        target_values = extract_values(html_file)
        tables = extract_tables_from_html(html_file)
        for i, table in enumerate(tables):
            transformed_table = transform_table(table, target_values)
            output_file_path = os.path.join(output_dir, f'{os.path.basename(html_file)}_table_{i + 1}.html')
            with open(output_file_path, "w", encoding="utf-8") as file:
                file.write(transformed_table.prettify())


if __name__ == '__main__':
    parse()
