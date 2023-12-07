from sys import stderr
from datetime import date
from database_query_helper import *
from custom_errors import *


""" #################################################################### 
convert postgresql returned value that is dict-like to a list
#################################################################### """


def dict_like_to_list(dict_like, output_type):
    try:
        # Remove the first and last characters (presumably '{' and '}') and split by comma
        elements = dict_like[1:-1].split(",")

        # Use a dictionary to map types to the corresponding conversion functions
        type_conversion = {
            "float": float,
            "integer": int,
            "date": lambda d: date.fromisoformat(d.strip())
        }

        # Apply the conversion function to each element in the list
        if output_type in type_conversion:
            cleaned_output = [type_conversion[output_type](element) for element in elements]
        else:
            raise ValueError(f"Unknown output type: {output_type}")

        return cleaned_output
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in dict_like_to_list() - Unable to convert dictionary-like object to a list."
        )


""" #################################################################### 
used to get the datatype of the attribute 
#################################################################### """


def get_attribute_datatype(relation, attribute):
    try:
        # retrieve a histogram
        sql_string = f"SELECT data_type FROM information_schema.columns WHERE table_name = '{relation}' AND column_name = '{attribute}';"
        return query(sql_string)[0]
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in get_attribute_datatype() - Unable to get the datatype of an attribute."
        )


""" #################################################################### 
used to get the histgram for a specific attribute from a table 
#################################################################### """


def get_histogram(relation, attribute, conditions):
    try:
        operators, attribute_values, attribute_datatypes = list(),list(),list()
        predicate_datatype = ""

        datatype_conversions = {
        "integer": int,
        "numeric": float,
        "date": lambda d: date.fromisoformat(d[1:-1])
        }
        
        # recreate the data in the correct type
        for condition in conditions:
            operators.append(condition[0])
            datatype = get_attribute_datatype(relation, attribute)
            attribute_datatypes.append(datatype)

            # convert = datatype_conversions.get(datatype, lambda x: x)
            convert = datatype_conversions.get(datatype)
            attribute_values.append(convert(condition[1]))

            if datatype in ["integer", "numeric", "date"]:
                predicate_datatype = datatype
            else:
                predicate_datatype = "string"

        # fail condition
        if not operators:
            return "ERROR - Please give at least one valid predicate to explore."

        # dictionary object to store return result
        return_values = {
            "relation": relation,
            "attribute": attribute,
            "datatype": predicate_datatype,
            "conditions": {},
        }

        # do for every condition
        for i in range(len(operators)):
            operator = operators[i]
            attribute_value = attribute_values[i]
            attribute_datatype = attribute_datatypes[i]
            condition = conditions[i]

            # retrieve a histogram
            sql_string = f"SELECT histogram_bounds FROM pg_stats WHERE tablename = '{relation}' AND attname = '{attribute}';"
            result = query(sql_string)
            result = result[0]
            datatype_mapping = {
                "numeric": "float",
                "integer": "integer",
                "date": "date"
            }

            # Convert the result based on the attribute datatype
            histogram = dict_like_to_list(result, datatype_mapping.get(attribute_datatype, "string"))


            num_buckets = len(histogram) - 1

            leftbound = next((i for i in range(num_buckets) if attribute_value > histogram[i]), 0)

            selectivity = (
                leftbound
                + (attribute_value - histogram[leftbound])
                / (histogram[leftbound + 1] - histogram[leftbound])
            ) / num_buckets

            selectivity = 1 - selectivity if operator in [">=", ">"] else selectivity

            # set floor and ceiling
            selectivity = max(0, min(selectivity, 1))

            # get 20% below until 20% above, in 10% intervals
            selectivities = [i / 10 for i in range(11)]
            lower = sorted(v for v in selectivities if v <= selectivity)
            higher = sorted(v for v in selectivities if v >= selectivity)

            selectivities_required = []

            if lower:
                selectivities_required.extend( lower[max(len(lower) - 2, 0):])


            if higher:
                selectivities_required.extend( higher[min(len(higher), 2):])

            selectivities_required = sorted(set(selectivities_required))
            values_required = {}
            for i in selectivities_required:
                i = 1 - i if operator in [">=", ">"] else i

                index = int(i * num_buckets)

                if operator in ["<=", "<"]:
                    values_required[i] = histogram[index]
                elif operator in [">=", ">"]:
                    values_required[1 - i] = histogram[index]

            return_values["conditions"][condition] = {
                "queried_selectivity": selectivity,
                "histogram_bounds": values_required
            }


        return return_values
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in get_histogram() - Unable to obtain histogram for the attribute."
        )