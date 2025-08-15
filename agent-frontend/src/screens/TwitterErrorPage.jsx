import React from 'react';
import { Link } from 'react-router-dom';
import { FaTwitter } from 'react-icons/fa';

const TwitterErrorPage = () => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      backgroundColor: '#f0f2f5',
      color: '#333',
      textAlign: 'center',
      padding: '20px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <FaTwitter size={80} color="#1DA1F2" />
      <h1 style={{ fontSize: '3em', margin: '20px 0' }}>Oops! Our Tweets Flew Away!</h1>
      <p style={{ fontSize: '1.2em', maxWidth: '600px' }}>
        It seems our Twitter link decided to take a spontaneous vacation. We're terribly sorry for the inconvenience!
        While we try to coax it back, feel free to explore other parts of our amazing application.
      </p>
      <p style={{ fontSize: '1.2em', maxWidth: '600px' }}>
        Perhaps it's for the best, who needs the bird app anyway? 😉
      </p>
      <Link to="/" style={{
        marginTop: '30px',
        padding: '10px 20px',
        backgroundColor: '#007bff',
        color: 'white',
        textDecoration: 'none',
        borderRadius: '5px',
        fontSize: '1em'
      }}>
        Go Back Home
      </Link>
    </div>
  );
};

export default TwitterErrorPage;
