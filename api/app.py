from flask import Flask, request

from sys import stderr
import ast
import string
import re
from datetime import date

from flask_cors import CORS


# our own python scripts
from database_query_helper import *
from generate_predicate_varies_values import *
from sqlparser import *
from generator import Generator
from query_visualizer_explainer import *
from custom_errors import *


# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Load Flask config
app = Flask(__name__)
CORS(app)
app.config.from_object("config.Config")
app.run(debug=True)

var_prefix_to_table = {
    "r": "region",
    "n": "nation",
    "s": "supplier",
    "c": "customer",
    "p": "part",
    "ps": "partsupp",
    "o": "orders",
    "l": "lineitem",
}

''' PSQL '''
equality_comparators = {"!=", "="}
range_comparators = {"<=", ">=", ">", "<"}
operators = {"<", "=", ">", "!"}

@app.route("/")
def hello():
    return "Hey, you're not supposed to come here! But if you find this, please give us extra marks, thanks! (:"


#used to generate a query plan based on the provided query
@app.route("/generate", methods=["POST"])
def get_plans():
    try:
        # Gets the request data from the frontend
        request_data = request.json
        sql_query = request_data["query"]

        # Gets the query execution plan (qep) recommended by postgres for this query and also the graph and explanation
        qep_sql_string = create_qep_sql(sql_query)
        original_qep, original_graph, original_explanation = execute_plan(
            qep_sql_string
        )

        # Get the values and selectivity of various attributes for the original query
        original_predicate_selectivity_data = list()

        for predicate_data in get_selectivities(sql_query, request_data["predicates"]):
            attribute = predicate_data["attribute"]

            original_predicate_selectivity_data = [
            {
                "attribute": attribute,
                "operator": operator,
                "queried_value": predicate_data["conditions"][operator]["histogram_bounds"][predicate_data["conditions"][operator]["queried_selectivity"]],
                "new_value": None,
                "queried_selectivity": predicate_data["conditions"][operator]["queried_selectivity"],
                "new_selectivity": None,
            }
            for operator in predicate_data["conditions"]]

        # Add the original query and its details into the dictionary that will contain all queries
        all_generated_plans = {
            0: {
                "qep": original_qep,
                "graph": original_graph,
                "explanation": original_explanation,
                "predicate_selectivity_data": original_predicate_selectivity_data,
                "estimated_cost_per_row": calculate_estimated_cost_per_row(original_qep),
            }
        }

        # Get the selectivity variation of this qep.
        if len(original_predicate_selectivity_data) != 0:

            new_selectivities = get_selectivities(sql_query, request_data["predicates"])

            # array of (new_queries, predicate_selectivity_data)
            new_plans = Generator().generate_plans(new_selectivities, sql_query)

            # loop through every potential new plan and fire off a query, then get the result and save to our result dictionary
            for index, (new_query, predicate_selectivity_data) in enumerate(new_plans):
                predicate_selectivity_combination = list()

                for data in predicate_selectivity_data:
                    predicate_selectivity = {
                        "attribute": data[0],
                        "operator": data[1],
                        "queried_value": data[2],
                        "new_value": data[3],
                        "queried_selectivity": data[4],
                        "new_selectivity": data[5],
                    }
                    predicate_selectivity_combination.append(predicate_selectivity)
                        


                qep_sql_string = create_qep_sql(new_query)
                qep, graph, explanation = execute_plan(qep_sql_string)
                all_generated_plans[index + 1] = {
                    "qep": qep,
                    "graph": graph,
                    "explanation": explanation,
                    "predicate_selectivity_data": predicate_selectivity_combination,
                    "estimated_cost_per_row": calculate_estimated_cost_per_row(qep),
                }

        # get the best plan out of all the generated plans
        best_plan_id = get_best_plan_id(all_generated_plans)

        # clean out the date objects for json serializability
        data = {
            "data": all_generated_plans,
            "best_plan_id": best_plan_id,
            "status": "Successfully executed query.",
            "error": False,
        }
        # clean_json(data)

        return data
    except CustomError as e:
        return {"status": str(e), "error": True}
    except Exception as e:
        print(str(e), file=stderr)
        return {
            "status": "Error in get_plans() - Unable to get plans for the query.",
            "error": True,
        }


#used to get the qep, graph and explanation for a given query string
def execute_plan(qep_sql_string):
    try:
        query_execution_plan = query(qep_sql_string, explain=True)
        query_execution_plan = json.dumps(ast.literal_eval(str(query_execution_plan)))
        query_execution_graph, query_execution_explanation = visualize_explain_query(query_execution_plan)
        query_execution_plan = json.loads(query_execution_plan)
        return query_execution_plan, query_execution_graph, query_execution_explanation
    except CustomError as e:
        raise CustomError(str(e))
    except:
        error_message = f"Error in execute_plan() - Unable to get QEP, graph, explanation. {str(e)}"
        raise CustomError(error_message)

def create_qep_sql(sql_query):
    try:
        # Prepare an SQL query for explaining query execution
        explained_sql_query = f"EXPLAIN (COSTS, VERBOSE, BUFFERS, FORMAT JSON) {sql_query}"
        return explained_sql_query
    except Exception as e:
        # Handle any exceptions and raise a custom error
        error_message = f"Error in create_qep_sql(): {str(e)}"
        raise CustomError(error_message)


#Calculates the specific selectivities of each predicate in the query.
def get_selectivities(sql_string, predicates):
    try:
        sqlparser = SQLParser()
        sqlparser.parse_query(sql_string)
        predicate_selectivities = list()
        for predicate in predicates:
            relation = var_prefix_to_table[predicate.split("_")[0]]
            conditions = sqlparser.comparison[predicate]
            if conditions and conditions[0][0] not in equality_comparators:
                histogram_data = get_histogram(relation, predicate, conditions)
                res = dict()
                for condition_key, condition_value in histogram_data["conditions"].items():  # k is like ('<', 5)
                    if len(condition_key) == 2:
                        operator = condition_key[0]
                        new_v = {key: value for key, value in condition_value.items()}
                        cur_selectivity = new_v["queried_selectivity"]
                        if histogram_data["datatype"] != "date":
                            new_v["histogram_bounds"][cur_selectivity] = condition_key[1]
                        else:
                            new_v["histogram_bounds"][cur_selectivity] = date.fromisoformat(condition_key[1][1:-1])

                        res[operator] = new_v
                histogram_data["conditions"] = dict(sorted(res.items()))  # make sure that < always comes first

                # histogram_data returns the histogram bounds for a single predicate
                predicate_selectivities.append(histogram_data)
        return predicate_selectivities
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in get_selectivities() - Unable to get the different selectivities for predicates."
        )



def get_selective_qep(sql_string, selectivities, predicates):
    try:
        # Find the place in query to add additional clauses for selectivity
        index = sql_string.find("where")

        # If there is a where statement, just add selectivity clause in where statement
        if index != -1:
            # Go to start of where statement
            index += 6
            for i in range(0, len(predicates)):
                predicate ,selectivity= str(predicates[i]),str(selectivities[i])
                sql_string = ( sql_string[:index] + f" {predicate} < {selectivity} and " + sql_string[index:])
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in get_selective_qep() - Unable to parse the sql_string for 'WHERE' clause."
        )


#get the best plan id in terms of cost, and the plan must be different from original plan
def get_best_plan_id(all_generated_plans):
    try:
        best_plan_id_cost = all_generated_plans[0]["estimated_cost_per_row"]
        best_plan_id = 0

        for plan_id in all_generated_plans:

            # ignore the original plan
            if plan_id != 0 and all_generated_plans[plan_id]["estimated_cost_per_row"] < best_plan_id_cost and all_generated_plans[plan_id]["explanation"]!= all_generated_plans[0]["explanation"]:
                best_plan_id_cost = all_generated_plans[plan_id]["estimated_cost_per_row"]
                best_plan_id = plan_id

        return best_plan_id
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in get_best_plan_id() - Unable to get the lowest cost plan."
        )
    

def calculate_estimated_cost_per_row(qep):
    try:
        total_cost = qep["Plan"]["Startup Cost"] + qep["Plan"]["Total Cost"]
        plan_rows = qep["Plan"]["Plan Rows"]
        if plan_rows!=0:
            estimated_cost_per_row = total_cost / plan_rows
            return estimated_cost_per_row
        else:
            return total_cost
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in calculate_estimated_cost_per_row() - Unable to calculate estimated costs."
        )