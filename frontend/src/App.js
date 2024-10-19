import logo from './logo.svg';
import './App.css';
import React, { useState, useEffect } from 'react';


function App() {
  const [optionData, setOptionData] = useState({});

  useEffect(() => {
    const fetchData = () => {
      fetch('/api/option_data')
        .then(response => response.json())
        .then(data => setOptionData(data));
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // 每5秒获取一次数据

    return () => clearInterval(interval); // 清除定时器
  }, []);

  return (
    <div>
      <h1>期权详情</h1>
      <p><strong>行权价:</strong> {optionData.strike_price}</p>
      <p><strong>时间戳:</strong> {optionData.timestamp}</p>
      <p><strong>买一价:</strong> {optionData.bid_price}</p>
      <p><strong>买一量:</strong> {optionData.bid_volume}</p>
      <p><strong>卖一价:</strong> {optionData.ask_price}</p>
      <p><strong>卖一量:</strong> {optionData.ask_volume}</p>
    </div>
  );
}

export default App;
