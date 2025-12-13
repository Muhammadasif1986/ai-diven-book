/**
 * SelectionHandler component for handling text selection and providing a floating button to query the AI
 */
import React, { useState, useEffect, useRef } from 'react';

interface SelectionHandlerProps {
  onQuerySubmit: (query: string) => void;
  isLoading: boolean;
}

const SelectionHandler: React.FC<SelectionHandlerProps> = ({ onQuerySubmit, isLoading }) => {
  const [selection, setSelection] = useState<{
    text: string;
    rect: DOMRect;
  } | null>(null);
  const [isVisible, setIsVisible] = useState(false);
  const selectionTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Handle text selection
  useEffect(() => {
    const handleSelection = () => {
      const selectedText = window.getSelection()?.toString().trim();

      if (selectedText) {
        const selectionRange = window.getSelection()?.getRangeAt(0);
        if (selectionRange) {
          const rect = selectionRange.getBoundingClientRect();
          setSelection({
            text: selectedText,
            rect: rect
          });
          setIsVisible(true);
        }
      } else {
        // Hide the button after a short delay to prevent flickering
        if (selectionTimeoutRef.current) {
          clearTimeout(selectionTimeoutRef.current);
        }
        selectionTimeoutRef.current = setTimeout(() => {
          setIsVisible(false);
          setSelection(null);
        }, 150);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('selectionchange', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('selectionchange', handleSelection);

      if (selectionTimeoutRef.current) {
        clearTimeout(selectionTimeoutRef.current);
      }
    };
  }, []);

  const handleAskClick = () => {
    if (selection?.text) {
      onQuerySubmit(selection.text);
      setIsVisible(false);
      setSelection(null);
      // Clear the selection
      window.getSelection()?.empty?.();
      document.getSelection()?.removeAllRanges?.();
    }
  };

  if (!isVisible || !selection || isLoading) {
    return null;
  }

  return (
    <div
      className="selection-handler-overlay"
      style={{
        position: 'fixed',
        top: selection.rect.top + window.scrollY - 50,
        left: selection.rect.left + window.scrollX + selection.rect.width / 2,
        transform: 'translateX(-50%)',
        zIndex: 9999,
        cursor: 'pointer',
      }}
      onClick={handleAskClick}
    >
      <div
        className="selection-handler-button"
        style={{
          backgroundColor: '#3b82f6', // blue-500
          color: 'white',
          borderRadius: '50%',
          width: '40px',
          height: '40px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          border: '2px solid white',
        }}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      </div>
    </div>
  );
};

export default SelectionHandler;