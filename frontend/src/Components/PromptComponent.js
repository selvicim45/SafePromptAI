/******************************************************************************************
______________________________________SafePromptAI_________________________________________
   Microsoft Hackathon March 2025
   Programmars: Arulselvi Amirrthalingam(Selvi) and Selvamani Ramasamy
   Challenge: Auto Correct and Prompt Validation Before AI Execution
   Frontend:React, AXIOS, CSS for UI Styling)
#******************************************************************************************/
import React, { useState } from 'react';
import axios from 'axios';

const PromptComponent = () => {
  const [userInput, setUserInput] = useState('');
  const [containsPii, setContainsPii] = useState(false);
  const [piiCategories, setPiiCategories] = useState([]);  // This will hold the categories of detected PII
  const [clarifiedInput, setClarifiedInput] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [proceeded, setProceed] = useState(false);  // Track if user has clicked "Proceed"
  const [isAudioReady, setIsAudioReady] = useState(false); // Track if audio is ready

  // Handle user input change
  const handleInputChange = (e) => {
    setUserInput(e.target.value);
    // Reset necessary states when user changes the input
    setContainsPii(false);
    setPiiCategories([]);
    setClarifiedInput('');
    setAiResponse('');
    setErrorMessage('');
    setProceed(false);  // Reset the proceeded state when new input is entered
    setIsAudioReady(false); // Reset audio readiness when new input is entered
  };

  // Function to submit input for PII check
  const handleSubmit = async () => {
    if (!userInput.trim()) {
      alert("Please enter some text.");
      return;
    }

    setIsLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:5000/check_pii', {
        input: userInput
      });

      // Check if PII was found in the input
      if (response.data.contains_pii) {
        setContainsPii(true);
        setPiiCategories(response.data.pii_categories);  // Set the detected categories
      } else {
        // If no PII is detected, proceed with processing
        await processInput(userInput);
      }
    } catch (error) {
      console.error("Error occurred:", error);
      setErrorMessage("An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // Function to handle user decision to proceed or revise input
  const handleUserApproval = async (approved) => {
    if (approved) {
      // User clicked "Proceed", set proceeded to true and continue processing
      setProceed(true);
      await processInput(userInput);
    } else {
      // User declined, clear the input to allow revision
      setUserInput('');
      setContainsPii(false);
      setPiiCategories([]);
      setClarifiedInput('');
      setAiResponse('');
      setProceed(false);
    }
  };

  // Function to process the input (AI response generation or other processing)
  const processInput = async (input) => {
    setIsLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:5000/process', {
        input: input
      });

      if (response.data.error) {
        setErrorMessage(response.data.error);
        return;
      }

      setClarifiedInput(response.data.clarified_input);
      setAiResponse(response.data.ai_response);
      setErrorMessage('');

      // Set audio URL to null initially (audio generation only happens later)
      setIsAudioReady(true); // Enable the play audio button after AI response is processed
    } catch (error) {
      console.error("Error occurred:", error);
      setErrorMessage("An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // Play audio for the clarified input and AI response
  const playAudio = async () => {
    if (!clarifiedInput || !aiResponse) {
      alert("Please submit a prompt first.");
      return;
    }

    try {
      // Send the audio request to the backend
      const response = await axios.post('http://127.0.0.1:5000/generate_audio', {
        first_text: clarifiedInput,
        second_text: aiResponse
      });

      // Check if the backend returned an audio URL
      if (response.data.audio_url) {
        const audioUrl = response.data.audio_url;
        const audioPlayer = new Audio(audioUrl);

        // Set up event listener for successful completion of the audio playback
        audioPlayer.addEventListener('ended', () => {
          console.log("Audio finished playing successfully.");
        });

        // Set up error handling
        audioPlayer.addEventListener('error', (error) => {
          console.error("Error playing audio:", error);
        });

        // Play the audio
        audioPlayer.play().catch((error) => {
          console.error("Error playing audio:", error);
        });
      } else {
        alert("Audio not available yet. Please try again.");
      }
    } catch (error) {
      console.error("Error generating audio:", error);
      alert("Failed to generate audio.");
    }
  };

  return (
    <div className="App" style={{ backgroundColor: '#FFFFE0', minHeight: '100vh', padding: '20px' }}>
      <h1>SafePromptAI</h1>
      <h2>Empathy in Technology: Clean Safe Prompt</h2>

      {/* User input */}
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="user_input">Enter your message:</label>
        <textarea
          id="user_input"
          rows="4"
          cols="50"
          value={userInput}
          onChange={handleInputChange}
          placeholder="Enter your prompt..."
          style={{ width: '100%', padding: '10px', borderRadius: '5px', marginBottom: '10px' }}
        />
        <br />
        <button onClick={handleSubmit} disabled={isLoading} style={{ padding: '10px 20px', fontSize: '16px' }}>
          {isLoading ? 'Processing...' : 'Send to AI'}
        </button>
      </div>

      {/* Error handling */}
      {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}

      {/* Clarified message */}
      <div style={{ marginTop: '20px' }}>
        <h3>Clarified Input:</h3>
        <textarea
          rows="4"
          cols="50"
          value={clarifiedInput}
          placeholder="Clarified message will appear here..."
          style={{ width: '100%', padding: '10px', borderRadius: '5px', marginBottom: '10px' }}
          readOnly
        />
      </div>

      {/* AI Response */}
      <div style={{ marginTop: '20px', backgroundColor: '#f8f8f8', padding: '10px', borderRadius: '5px' }}>
          <h3>AI Response:</h3>
          <p style={{ fontSize: '16px', lineHeight: '1.5' }}>
          {aiResponse || <i style={{ color: 'gray' }}>AI response will appear here...</i>}
       </p>
       </div>


      {/* PII Approval Modal */}
      {containsPii && !proceeded && (
        <div style={{ marginTop: '20px' }}>
          <p>Your input contains potentially sensitive information. The following categories were detected:</p>
          <div style={{ color: 'red', fontWeight: 'bold', marginBottom: '10px' }}>
            {piiCategories.map((category, index) => (
              <span key={index}>
                {category}
                {index !== piiCategories.length - 1 && ', '}
              </span>
            ))}
          </div>

          <p style={{ color: 'red' }}>Are you sure you want to share this information?</p>

          <button onClick={() => handleUserApproval(true)} style={{ padding: '10px 20px', fontSize: '16px', marginRight: '10px' }}>
            Yes, Proceed
          </button>
          <button onClick={() => handleUserApproval(false)} style={{ padding: '10px 20px', fontSize: '16px' }}>
            No, Revise
          </button>
        </div>
      )}

      {/* Audio section */}
      {isAudioReady && (
        <div id="audio_section" style={{ marginTop: '20px' }}>
          <button onClick={playAudio} style={{ padding: '10px 20px', fontSize: '16px' }}>
            Play Audio
          </button>
        </div>
      )}
    </div>
  );
};

export default PromptComponent;
