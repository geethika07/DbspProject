import React from 'react';
import Container from 'react-bootstrap/Container';
import FormInput from '../Input/Input';
import styles from "./App.module.css";
import iconImage from "../../db logo.jpeg";
import { useState, useEffect } from 'react';
// Constants for URLs
const TPC_H_DATASET_URL = "http://www.tpc.org/tpch/";

const Header = () => {
  const [colorChange, setColorChange] = useState(false);

  const changeColor = () => {
    if(window.scrollY >= 80){
      setColorChange(true);
    } else {
      setColorChange(false);
    }
  };

  useEffect(() => {
    window.addEventListener('scroll', changeColor);
    return () => window.removeEventListener('scroll', changeColor);
  }, []);

  return (
  <div className={styles.uniqueHeaderWrapper}>
    <div className={styles.uniqueHeaderContent}>
      <img src={iconImage} alt="Icon" className={styles.uniqueHeaderIcon} />
      <h1 className={styles.headerTitle}>Explore SQL Performance</h1>
    </div>
    <p className={styles.leadText}>Optimize your SQL queries in a snap!</p>
    <HeaderText />
  </div>
  );
};


const HeaderText = () => (
  <>
    <p className={styles.uniqueHeaderText}>
      Welcome to our SQL Query Optimizer! Here, you can experiment with different SQL queries and uncover the most efficient execution strategies. Just input an SQL query based on the <a href={TPC_H_DATASET_URL} target="_blank" rel="noopener noreferrer" style={{color:'#333'}}>TPC-H dataset</a> and let the magic happen.
    </p>
    <p className={styles.uniqueHeaderText}>
      Make sure your database is set up as per the guidelines. Feel free to tweak various predicates on the fly; our optimizer will adapt and compare different execution plans for you. Remember, only certain predicates are allowed for modification, specifically those related to numeric and date attributes, and they must be supported by histograms in your database.
    </p>
    <p className={styles.uniqueHeaderText}>
      Dive in and start optimizing your SQL queries. Who knew database performance tuning could be this easy and fun?
    </p>
  </>
);

const App = () => {
  return (
    <Container fluid="md" className={styles.customContainer}>
      <Header />
      <hr />
      <div className={styles.formInputArea}> 
        <FormInput />
      </div>
    </Container>
  );
}

export default App;
