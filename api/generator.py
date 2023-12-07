import datetime
from datetime import date
from sys import stderr
from custom_errors import *


""" #################################################################### 
used to generate the combinations of queries for the selected predicates
#################################################################### """


class Generator:
    def generate_plans(self, arr, original_sql):  
        # takes in array of selectivites per predicate, from get_selectivities
        try:
            res = list()

            def helper(index, path, predicate_selectivities):  
                # predicate_selectivities is like (predicate0 , 0.93) * (predicate1, 0.78) * 1.2...
                if index == len(arr):
                    res.append([path, predicate_selectivities])
                    return

                if len(arr[index]["conditions"]) == 1:  # only one comparator
                    for operator, value in arr[index]["conditions"].items():
                        queried_selectivity = value["queried_selectivity"]
                        old_val = value["histogram_bounds"][queried_selectivity]
                        for selectivity, val in value["histogram_bounds"].items():
                            # selectivity_as_percentage_of_base = float(selectivity / queried_selectivity)
                            selectivity_data = (
                                arr[index]["attribute"],
                                operator,
                                old_val,
                                val,
                                queried_selectivity,
                                selectivity,
                            )
                            new_path = self.find_and_replace(arr[index]["attribute"], operator, old_val, val, path)
                            updated_selectivities=predicate_selectivities + [selectivity_data]
                            helper(
                                index + 1,
                                new_path,
                               updated_selectivities,
                            )

                elif len(arr[index]["conditions"]) == 2:  # range
                    count = 0
                    lessthan_histogram_bounds, morethan_histogram_bounds = list(), list()
                    operators = list()
                    for operator, value in arr[index]["conditions"].items():
                        queried_selectivity = value["queried_selectivity"]
                        old_val = value["histogram_bounds"][queried_selectivity]
                        count += 1
                        histogram_bounds_map = {1: 'lessthan', 2: 'morethan'}

                        # Update the appropriate list based on the count
                        bounds_key = histogram_bounds_map.get(count)
                        if bounds_key:
                            histogram_bounds = [
                                (val, selectivity, queried_selectivity, old_val)
                                for selectivity, val in value["histogram_bounds"].items()
                            ]
                            if bounds_key == 'lessthan':
                                lessthan_histogram_bounds = histogram_bounds
                            elif bounds_key == 'morethan':
                                morethan_histogram_bounds = histogram_bounds
                            
                            operators.append(operator)
                    for less_than_data, more_than_data in self.generate_ranges(lessthan_histogram_bounds, morethan_histogram_bounds):
                        # Unpack the tuples for clarity
                        val_less, sel_less, queried_sel_less, old_val_less = less_than_data
                        val_more, sel_more, queried_sel_more, old_val_more = more_than_data

                        # Update path with more_than condition
                        path_with_more_than = self.find_and_replace(
                            arr[index]["attribute"], operators[1], old_val_more, val_more, path
                        )

                        # Update path with both less_than and more_than conditions
                        updated_path = self.find_and_replace(
                            arr[index]["attribute"], operators[0], old_val_less, val_less, path_with_more_than
                        )

                        # Construct selectivity data for both conditions
                        selectivity_data_less = (
                            arr[index]["attribute"], operators[0], old_val_less, val_less,
                            queried_sel_less, sel_less
                        )
                        selectivity_data_more = (
                            arr[index]["attribute"], operators[1], old_val_more, val_more,
                            queried_sel_more, sel_more
                        )
                        combined_selectivity_data = [selectivity_data_less, selectivity_data_more]

                        # Call helper function with updated path and combined selectivity data
                        helper(index + 1, updated_path, predicate_selectivities + combined_selectivity_data)

            helper(0, original_sql, [])
            return res
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError(
                "Error in generate_plans() - Unable to generate plans for required selectivity variations."
            )

    def generate_ranges(self, lessthan_histogram_bounds, morethan_histogram_bounds):  # for selectivities with more than 2 conditions (i.e. range)
        try:
            # less than should always have a greater value than the more than
            # all possible permutations
            res=list()
            for x in lessthan_histogram_bounds:
                for y in morethan_histogram_bounds:
                    if x[0] > y[0]:
                        res.append((x,y))
            return res
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError(
                "Error in generate_ranges() - Unable to generate the required histogram bounds."
            )

    def find_and_replace(self, predicate, operator, old_val, new_val, sql_query):
        try:
            if type(new_val) == datetime.date:
                new_val = f"'{date.isoformat(new_val)}'"
            if type(old_val) == datetime.date:
                old_val = f"'{date.isoformat(old_val)}'"
            old_expression = f"{predicate} {operator} {old_val}"
            new_expression = f"{predicate} {operator} {new_val}"
            new_query = sql_query.replace(old_expression, new_expression)
            return new_query
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError(
                "Error in find_and_replace() - Unable to replace the original attribute value with the new one."
            )