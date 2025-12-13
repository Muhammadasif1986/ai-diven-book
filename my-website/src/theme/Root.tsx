import React, { useEffect, useState } from 'react';
import Chatbot from '../components/Chatbot';

// Define the Root component props
interface Props {
  children: React.ReactNode;
}

// Root component that wraps the entire Docusaurus app
const Root: React.FC<Props> = ({ children }) => {
  useEffect(() => {
    // Initialize any global functionality when the app loads
    console.log('Docusaurus app with integrated chatbot loaded');
  }, []);

  // Conditionally render the Chatbot only on the client side
  const [showChatbot, setShowChatbot] = useState(false);

  React.useEffect(() => {
    // This will only run on the client side
    setShowChatbot(true);
  }, []);

  return (
    <>
      {/* Render the normal Docusaurus content */}
      {children}

      {/* Add the chatbot to all pages only on client side */}
      {showChatbot && <Chatbot />}
    </>
  );
};

export default Root;