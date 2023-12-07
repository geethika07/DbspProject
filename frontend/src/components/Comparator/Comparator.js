import { Fragment } from 'react';
import Table from 'react-bootstrap/Table';
import styles from "./Comparator.module.css";

const PlanComparison = ({ output, planId }) => {
  const isDataAvailable = () => output["data"].hasOwnProperty(planId);

  const renderSelectivityData = () => {
    if (output["error"] === false && isDataAvailable()) {
      const planData = output["data"][planId];
      return planData["predicate_selectivity_data"].map((predicate, index) => renderPredicateRow(predicate, index));
    }
    return null;
  };

  const renderPredicateRow = (predicate, index) => {
    const { attribute, operator, new_selectivity, queried_selectivity, queried_value, new_value } = predicate;
    const selectivity = parseFloat(new_selectivity ?? queried_selectivity).toFixed(3);
    const value = new_value ?? queried_value;

    return (
      <Fragment key={index}>
        <tr className={styles.planAttributeCell}>
          <td colSpan="2"><b>{attribute}</b></td>
        </tr>
        <tr>
          <td><b>Value</b></td>
          <td>{`${operator} ${value}`}</td>
        </tr>
        <tr>
          <td><b>Selectivity</b></td>
          <td>{selectivity}</td>
        </tr>
      </Fragment>
    );
  };

  const renderComparisonTable = () => {
    const planData = output["data"][planId];
    return (
      <Table bordered hover responsive className={styles.planComparisonTable}>
        <tbody>
          <tr>
            <td><b>Estimated cost per row</b></td>
            <td>{parseFloat(planData["estimated_cost_per_row"]).toFixed(3)}</td>
          </tr>
          {renderSelectivityData()}
        </tbody>
      </Table>
    );
  };

  return (
    <div>
      {isDataAvailable() ? renderComparisonTable() : <div className={styles.planComparisonLoading}><span>No data to show</span></div>}
    </div>
  );
}

export default PlanComparison;
