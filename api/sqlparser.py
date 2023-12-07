import sqlparse
import collections 
import re
from operator import mul, add, sub, truediv
from custom_errors import *

FROM = "FROM"
SELECT = "SELECT"
GROUP_BY = "GROUP BY"
ORDER_BY = "ORDER BY"
range_comparators = {"<=", ">=", ">", "<"}
operators = {"<", "=", ">", "!"}

class SQLParser:
    def __init__(self):
        self.comparison = collections.defaultdict(list)
        self.parenthesis = list()
        self.select_attributes = list()
        self.tables = list()
        self.orderby_attributes = list()
        self.groupby_attributes = list()

    def parse_query(self, sql):
        try:
            nested_sql_ = self.nested_query(sql)
            nested_sql = nested_sql_.replace('  ', '')
            formatted_sql = self.sql_formatter(nested_sql)
            parsed = sqlparse.parse(formatted_sql)
            stmt = parsed[0]
            from_seen, select_seen, where_seen, groupby_seen, orderby_seen = (
                False,
                False,
                False,
                False,
                False,
            )


            def append_identifiers_if_seen(self, token, attribute_list):
                if isinstance(token, sqlparse.sql.IdentifierList):
                    attribute_list.extend(token.get_identifiers())
                elif isinstance(token, sqlparse.sql.Identifier):
                    attribute_list.append(token)

            for token in stmt.tokens:
                # Append identifiers to respective lists based on seen flags
                if select_seen:
                    append_identifiers_if_seen(self, token, self.select_attributes)
                if from_seen:
                    append_identifiers_if_seen(self, token, self.tables)
                if orderby_seen:
                    append_identifiers_if_seen(self, token, self.orderby_attributes)
                if groupby_seen:
                     append_identifiers_if_seen(self, token, self.groupby_attributes)

                if isinstance(token, sqlparse.sql.Where):
                    select_seen, from_seen, where_seen, groupby_seen, orderby_seen = False, False, True, False, False
                    for tokens in token:
                        if isinstance(tokens, sqlparse.sql.Comparison):
                            comparison_string = f"{tokens}\n"
                            comparison_key, comparison_operator, comparison_value = map(str.strip, comparison_string.split(" "))
                            self.comparison[comparison_key].append((comparison_operator, comparison_value))
                        # Check if it's a parenthesis expression
                        elif isinstance(tokens, sqlparse.sql.Parenthesis):
                            parenthesis_string = f"{tokens}\n"
                            self.parenthesis.append(parenthesis_string)

            keyword_mappings = {
                GROUP_BY: (False, False, False, True, False),
                ORDER_BY: (False, False, False, False, True),
                FROM: (False, True, False, False, False),
                SELECT: (True, False, False, False, False)
            }

            # Check if the token is a keyword and update seen flags accordingly
            if token.ttype is sqlparse.tokens.Keyword:
                keyword_upper = token.value.upper()
                select_seen, from_seen, where_seen, groupby_seen, orderby_seen = keyword_mappings.get(keyword_upper, (False, False, False, False, False))

        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError("Error in parse_query() - Unable to parse the SQL query.")

    def query_index(self, inside, whole):
        if(whole.find(inside)>=0):
            return whole.find(inside);
        return -1;

    def calculate(self, s):
        try:
            OP = {"*": mul, "+": add, "-": sub, "/": truediv}
            cur_op = ""
            cur_num, prev_num = "", ""
            num_chars = [char for char in s if char != ""]
            for char in num_chars:
                if char in OP.keys():
                    cur_op, prev_num, cur_num = char, cur_num, ""
                elif char != " ":
                    cur_num += char
            return OP[cur_op](float(prev_num), float(cur_num))
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError(
                "Error in calculate() - Unable to calculate attribute value."
            )

    def sql_formatter(self, sql):
        try:
            # Define the set of operators
            operators_set = set(['=', '<', '>', '!', '+', '-', '*', '/', '%', '^', '&', '|', '~'])
            
            # Use regular expression to add spaces around the operators
            formatted_sql = re.sub(f"([{re.escape(''.join(operators_set))}])", r" \1 ", sql)

            # Replace multiple spaces with a single space
            formatted_sql = re.sub(r'\s+', ' ', formatted_sql).strip()

            return formatted_sql
        except CustomError as e:
            raise CustomError(str(e))
        except Exception as e:
            raise CustomError(f"Error in sql_formatter() - {e}")
        

    def nested_query(self, sql): 
        try:
            select_index = list()
            splitted_word_sql = sql.split(" ")
            
            for i, word in enumerate(splitted_word_sql): 
                if word in ['select\n', 'SELECT\n']:
                    select_index.append(i)
            if len(select_index) == 2: 
                start_index = end_index = int(select_index[1])
                while not splitted_word_sql[start_index].startswith('('):
                    start_index -= 1  
                flag = False
                for i in range(start_index, start_index-3, -1): 
                    if splitted_word_sql[i] in range_comparators:
                        flag = True
                        break;
                if flag:
                    if len(splitted_word_sql[start_index]) > 1:
                        start_part = splitted_word_sql[start_index][2:]
                    else:
                        start_part = splitted_word_sql[start_index]

                    while not splitted_word_sql[end_index].startswith(')'): 
                        end_index += 1
                    if len(splitted_word_sql[end_index]) > 1:
                        end_part = splitted_word_sql[end_index][1:]
                    else:
                        end_part = splitted_word_sql[end_index]
                    
                    before_start_index = " ".join(splitted_word_sql[:start_index])
                    after_end_index = " ".join(splitted_word_sql[end_index + 1:])

                    final_string = before_start_index + " " + start_part + " 100 " + end_part + " " + after_end_index

                    return final_string.strip()

            return sql
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError("Error in nested_query() - Unable to parse the nested query. Have mercy and give us something less nested please.")