import { useState } from 'react';
import axios from "axios";

import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Accordion from 'react-bootstrap/Accordion'
import Card from 'react-bootstrap/Card'
import Toast from 'react-bootstrap/Toast'
import Spinner from 'react-bootstrap/Spinner'
import Modal from 'react-bootstrap/Modal';
import FormOutput from "../Output/Output";

import styles from "./Input.module.css";

const FormInput = () => {
  const [queryInput, setQueryInput] = useState({
    "query": "",
    "predicates": []
  });
  const [queryOutput, setQueryOutput] = useState({
    "data": {},
    "bestPlanId": 1,
    "status": "",
    "error": false
  });

  const [showPredicateLimitWarning, setShowPredicateLimitWarning] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isError, setIsError] = useState(false);
  const [predicateModalShow, setPredicateModalShow] = useState(false);
  const [outputModalShow, setOutputModalShow] = useState(false);
  const handlePredicateModalOpen = () => setPredicateModalShow(true);
  const handlePredicateModalClose = () => setPredicateModalShow(false);
  const handleSubmit = (event) => {
    event.preventDefault();
    setIsLoading(true);
    setQueryOutput({ ...queryOutput, status: "Generating output...", error: false });
    
    if (queryInput.query !== "") {
      axios.post("http://127.0.0.1:5000/generate", queryInput)
        .then(response => {
          setIsLoading(false);
          if (response.data.error) {
            setQueryOutput({ ...queryOutput, status: response.data.status, error: true });
            setIsError(true);
          } else {
            setQueryOutput({ ...queryOutput, data: response.data.data, bestPlanId: response.data.best_plan_id, status: response.data.status, error: false });
            setIsSuccess(true);
            setOutputModalShow(true);
          }
        })
        .catch(error => {
          setIsLoading(false);
          setQueryOutput({ ...queryOutput, status: "Error generating output. Please check your query's formatting and/or validity.", error: true });
          setIsError(true);
        });
    } else {
      setIsLoading(false);
      setQueryOutput({ ...queryOutput, status: "Error generating output. Please input an SQL query.", error: true });
      setIsError(true);
    }
  };
  const handlePredicateLimit = (event) => {
    event.target.checked = false;
    setShowPredicateLimitWarning(true);
  }

  const handlePredicateSelection = (event) => {
    setQueryInput(oldState => {
      const index = oldState.predicates.indexOf(event.target.id);

      if (event.target.checked) {
        if (index <= -1) {
          if (oldState.predicates.length >= 4) {
            handlePredicateLimit(event);
            return (oldState);
          }
          oldState.predicates.push(event.target.id)
        }
      }
      else {
        if (index > -1) {
          oldState.predicates.splice(index, 1);
        }
      }

      return ({ ...oldState, "predicates": oldState.predicates });
    });
  }

  // Resets the form's state.
  const resetForm = () => {
    setQueryInput({
      "query": "",
      "predicates": []
    });
    setQueryOutput({
      "data": {},
      "bestPlanId": 1,
      "status": "",
      "error": false
    });
  };

  const ToastMessage = ({ show, onClose, type, header, body }) => (
    <div className={styles.toastContainer}>
      <Toast className={styles[type]} show={show} onClose={onClose} delay={3000} autohide animation>
        <Toast.Header>{header}</Toast.Header>
        <Toast.Body>{body}</Toast.Body>
      </Toast>
    </div>
  );

  return (
    <>

          {/* Toast messages for success, loading, and error */}
      <ToastMessage 
        show={isLoading} 
        onClose={() => setIsLoading(false)} 
        type="toastLoading" 
        header="Loading data..." 
        body={<Spinner animation="border" role="status" />} 
      />
      <ToastMessage 
        show={isSuccess} 
        onClose={() => setIsSuccess(false)} 
        type="toastSuccess" 
        header="Success!" 
        body="Data loaded. Please see the output for the results." 
      />
      <ToastMessage 
        show={isError} 
        onClose={() => setIsError(false)} 
        type="toastError" 
        header="Error!" 
        body={queryOutput.status} 
      />

      <Form onSubmit={handleSubmit} className="mb-4" style={{ marginBottom: '2rem' }}>

        <Form.Row>
          <Form.Group as={Row} controlId="formPredicates">
            <Button variant="primary" onClick={handlePredicateModalOpen} className={styles.button}>
              Select Predicates
            </Button>
            <br />
            <Form.Text className={styles.text} style={{ marginTop: '1rem' }}>
              Choose a maximum of four predicates subject to a range restriction within the WHERE segment of the query (no conditions of equality).
            </Form.Text>
            <Form.Text className={styles.text} style={{ marginTop: '-1rem' }}>
              Example: <b> WHERE l_extendedprice &gt; 100</b> select <b>l_extendedprice</b> as the predicate.
            </Form.Text>

            <Modal show={predicateModalShow} onHide={handlePredicateModalClose}>
              <Modal.Header closeButton>
                <Modal.Title>Predicate Selection</Modal.Title>
              </Modal.Header>
              <Modal.Body>
              <ToastMessage 
            show={showPredicateLimitWarning} 
            onClose={() => setShowPredicateLimitWarning(false)} 
            type="errorToast" 
            header="Too many predicates!" 
            body="You may not select more than 4 predicates." 
          />
                <Accordion style={{ marginTop: '1.25rem' }}>
                  <Card>
                    <Accordion.Toggle as={Card.Header} variant="link" eventKey="0">
                      Region
                    </Accordion.Toggle>
                    <Accordion.Collapse eventKey="0">
                      <Card.Body>
                        {["r_regionkey"].map((type) => (
                          <Form.Check
                            type="checkbox" key={type} id={type} label={type} onClick={handlePredicateSelection}
                            checked={queryInput.predicates.includes(type)} />
                        ))}
                      </Card.Body>
                    </Accordion.Collapse>
                  </Card>
                  <Card>
                    <Accordion.Toggle as={Card.Header} variant="link" eventKey="1">
                      Nation
                    </Accordion.Toggle>
                    <Accordion.Collapse eventKey="1">
                      <Card.Body>
                        {["n_nationkey"].map((type) => (
                          <Form.Check
                            type="checkbox" key={type} id={type} label={type} onClick={handlePredicateSelection}
                            checked={queryInput.predicates.includes(type)} />
                        ))}
                      </Card.Body>
                    </Accordion.Collapse>
                  </Card>
                  <Card>
                    <Accordion.Toggle as={Card.Header} variant="link" eventKey="2">
                      Supplier
                    </Accordion.Toggle>
                    <Accordion.Collapse eventKey="2">
                      <Card.Body>
                        {["s_suppkey", "s_acctbal"].map((type) => (
                          <Form.Check
                            type="checkbox" key={type} id={type} label={type} onClick={handlePredicateSelection}
                            checked={queryInput.predicates.includes(type)} />
                        ))}
                      </Card.Body>
                    </Accordion.Collapse>
                  </Card>
                  <Card>
                    <Accordion.Toggle as={Card.Header} variant="link" eventKey="3">
                      Customer
                    </Accordion.Toggle>
                    <Accordion.Collapse eventKey="3">
                      <Card.Body>
                        {["c_custkey", "c_acctbal"].map((type) => (
                          <Form.Check
                            type="checkbox" key={type} id={type} label={type} onClick={handlePredicateSelection}
                            checked={queryInput.predicates.includes(type)} />
                        ))}
                      </Card.Body>
                    </Accordion.Collapse>
                  </Card>
                  <Card>
                    <Accordion.Toggle as={Card.Header} variant="link" eventKey="4">
                      Part
                    </Accordion.Toggle>
                    <Accordion.Collapse eventKey="4">
                      <Card.Body>
                        {["p_partkey", "p_retailprice"].map((type) => (
                          <Form.Check
                            type="checkbox" key={type} id={type} label={type} onClick={handlePredicateSelection}
                            checked={queryInput.predicates.includes(type)} />
                        ))}
                      </Card.Body>
                    </Accordion.Collapse>
                  </Card>
                  <Card>
                    <Accordion.Toggle as={Card.Header} variant="link" eventKey="5">
                      PartSupp
                    </Accordion.Toggle>
                    <Accordion.Collapse eventKey="5">
                      <Card.Body>
                        {["ps_partkey", "ps_suppkey", "ps_availqty", "ps_supplycost"].map((type) => (
                          <Form.Check
                            type="checkbox" key={type} id={type} label={type} onClick={handlePredicateSelection}
                            checked={queryInput.predicates.includes(type)} />
                        ))}
                      </Card.Body>
                    </Accordion.Collapse>
                  </Card>
                  <Card>
                    <Accordion.Toggle as={Card.Header} variant="link" eventKey="6">
                      Orders
                    </Accordion.Toggle>
                    <Accordion.Collapse eventKey="6">
                      <Card.Body>
                        {["o_orderkey", "o_custkey", "o_totalprice", "o_orderdate"].map((type) => (
                          <Form.Check
                            type="checkbox" key={type} id={type} label={type} onClick={handlePredicateSelection}
                            checked={queryInput.predicates.includes(type)} />
                        ))}
                      </Card.Body>
                    </Accordion.Collapse>
                  </Card>
                  <Card>
                    <Accordion.Toggle as={Card.Header} variant="link" eventKey="7">
                      LineItem
                    </Accordion.Toggle>
                    <Accordion.Collapse eventKey="7">
                      <Card.Body>
                        {["l_orderkey", "l_partkey", "l_suppkey", "l_extendedprice", "l_shipdate", "l_commitdate", "l_receiptdate"].map((type) => (
                          <Form.Check
                            type="checkbox" key={type} id={type} label={type} onClick={handlePredicateSelection}
                            checked={queryInput.predicates.includes(type)} />
                        ))}
                      </Card.Body>
                    </Accordion.Collapse>
                  </Card>
                </Accordion>
              </Modal.Body>
              <Modal.Footer>
                <Button variant="secondary" onClick={handlePredicateModalClose}>
                  Close
                </Button>
              </Modal.Footer>
            </Modal>
          </Form.Group>

          <Form.Group as={Row} controlId="formInput">
            <Form.Group controlId="formQuery">
              <Form.Label className={styles.formLabel}><b>SQL Query</b></Form.Label>
              <Form.Text className={styles.formText}>
                Enter your SQL query here. Make sure that the query is correctly structured and constitutes a legitimate SQL command. You may utilize the 'Enter' key to format your query over several lines. Currently, we do not accommodate highly nested queries, although single-level nesting is acceptable.
              </Form.Text>
              {/* <br /> */}
              <Form.Control as="textarea" rows="19" placeholder="Input SQL query..." onChange={event => setQueryInput({ ...queryInput, "query": event.target.value })} value={queryInput.query} style={{ height: '405px', backgroundColor: '#f7f7f7' }} />
              <Row>
                <Col>
                  <Button onClick={resetForm} variant="secondary" type="reset" className="w-100 mt-3 ">
                    Reset
                  </Button>
                </Col>
                <Col>
                  <Button variant="primary" type="submit" className="w-100 mt-3" style={{ backgroundColor: '#333', borderColor: '#333' }}>
                    Generate
                  </Button>
                </Col>
              </Row>
            </Form.Group>
          </Form.Group>
        </Form.Row>
      </Form>

      <Modal className={styles.custom} show={outputModalShow} onHide={() => setOutputModalShow(false)} >
        <Modal.Dialog style={{ "minWidth": "1000px", "position": "absolute", "left": "-250px" }}> {/* Apply the custom class here */}
          <Modal.Header closeButton style={{ "backgroundColor": "#f4f4f8", "color": "#333", "padding": "1rem", "borderBottom": "1px solid #ddd", "fontSize": "1.2rem" }}>
            <Modal.Title>Results</Modal.Title>
          </Modal.Header>
          <Modal.Body style={{ "padding": "1rem", "backgroundColor": "#fff", "color": "#333" }}>
            <FormOutput output={queryOutput} />
          </Modal.Body>
          <Modal.Footer style={{ "padding": "0.5rem", "backgroundColor": "#f4f4f8", "borderTop": "1px solid #ddd", "textAlign": "right" }}>
            <Button className={styles.outputModalCloseBtn} onClick={() => setOutputModalShow(false)}>
              Close
            </Button>
          </Modal.Footer>
        </Modal.Dialog>
      </Modal>


    </>
  )
}

export default FormInput;