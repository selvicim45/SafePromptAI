
import React from 'react';
import './App.css';  // Keep this if you want to style your app
import PromptComponent from './Components/PromptComponent';  // Correct the import path to reflect the location of PromptComponent

function App() {
  return (
    <div className="App">
      <PromptComponent />  {/* Render the PromptComponent */}
    </div>
  );
}

export default App;

