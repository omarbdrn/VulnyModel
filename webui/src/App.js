import React, { useState, useEffect, useRef  } from 'react';
import './App.css';

const App = () => {
  const [reward, setReward] = useState(0);
  const [modelData, setModelData] = useState({});
  const [filename, setFilename] = useState('');
  const [fileCode, setFileCode] = useState('');
  const [predictionLabel, setPredictionLabel] = useState('');
  const [predictionProbabilities, setPredictionProbabilities] = useState('');
  const isMountedRef = useRef(false); // Track initial mount state

  useEffect(() => {
    if (isMountedRef.current) {
      return; // Skip fetching data on subsequent renders
    }
    
    fetchModelData();
    fetchData();
    isMountedRef.current = true;
  }, []);

  const fetchModelData = async () => {
    try {
      const response = await fetch('http://localhost:6969/api/model/data'); // Replace with your API endpoint
      const data = await response.json();
      setModelData(data);
    } catch (error) {
      console.log('Error fetching model data:', error);
    }
  };

  const fetchData = async () => {
    try {
      const response = await fetch('http://localhost:6969/api/model/snippet'); // Replace with your API endpoint
      const data = await response.json();
      setFilename(data.filename);
      setFileCode(data.file_code);
      setPredictionLabel(data.prediction_label);
      setPredictionProbabilities(data.prediction_probabilities);
    } catch (error) {
      console.log('Error fetching data:', error);
    }
  };

  const handleSetReward = async (value) => {
    setReward(value);
    saveRewardToCSV(value);
  };

  const saveRewardToCSV = async (value) => {
    try {
      const requestBody = {
        filename,
        reward: value,
      };
      return await fetch('http://localhost:6969/api/model/insert-csv', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
        mode:'cors',
      }).then(() => {
        fetchData();
      });
    } catch (error) {
      console.log('Error saving reward:', error);
    }
  };

  return (
    <div className="container">
      <div className="sidebar">
        <div className="sidebar-heading">
          <h2>Manual-RLAgent</h2>
        </div>
        <div className="sideList">
          <ul>
            <li>Model Name: {modelData.model_name}</li>
            <li>Model Accuracy: {modelData.model_accuracy}</li>
            <li>Model Size: {modelData.model_size}</li>
          </ul>
        </div>
      </div>
      <div className="content">
        <pre className="textWhite">Filename: {filename}</pre>
        <div className="codeblock">
          <code>{fileCode}</code>
        </div>
        <pre className="textWhite">
          Prediction: {predictionLabel}, Probabilities: {predictionProbabilities}
        </pre>
        <div className="buttons">
          <button onClick={() => handleSetReward(1, filename, predictionLabel)}>
            <span>Correct</span>
            <i></i>
          </button>
          <button onClick={() => handleSetReward(-1)}>
            <span>Incorrect</span>
            <i></i>
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;