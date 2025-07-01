import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div style={{ 
      minHeight: '100vh', 
      padding: '20px', 
      fontFamily: 'Arial, sans-serif',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white'
    }}>
      {/* Header */}
      <header style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '10px' }}>🤖 AI Brand Audit Tool</h1>
        <p style={{ fontSize: '1.2rem', opacity: 0.9 }}>
          Comprehensive brand analysis powered by AI
        </p>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
          gap: '20px',
          marginBottom: '40px'
        }}>
          <div style={{ 
            background: 'rgba(255,255,255,0.1)', 
            padding: '30px', 
            borderRadius: '15px',
            textAlign: 'center',
            backdropFilter: 'blur(10px)'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🔍</div>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>Brand Search</h3>
            <p>Search and analyze any brand's digital presence</p>
          </div>
          
          <div style={{ 
            background: 'rgba(255,255,255,0.1)', 
            padding: '30px', 
            borderRadius: '15px',
            textAlign: 'center',
            backdropFilter: 'blur(10px)'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '15px' }}>📤</div>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>Asset Analysis</h3>
            <p>Upload and analyze brand assets and logos</p>
          </div>
          
          <div style={{ 
            background: 'rgba(255,255,255,0.1)', 
            padding: '30px', 
            borderRadius: '15px',
            textAlign: 'center',
            backdropFilter: 'blur(10px)'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '15px' }}>📊</div>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>AI Insights</h3>
            <p>Get AI-powered recommendations and insights</p>
          </div>
        </div>

        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <button 
            onClick={() => setCount(count + 1)}
            style={{
              background: '#ff6b6b',
              color: 'white',
              border: 'none',
              padding: '15px 30px',
              fontSize: '1.1rem',
              borderRadius: '25px',
              cursor: 'pointer',
              marginRight: '15px',
              boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
            }}
          >
            Start Analysis (Clicked {count} times)
          </button>
          
          <button 
            style={{
              background: 'rgba(255,255,255,0.2)',
              color: 'white',
              border: '2px solid white',
              padding: '15px 30px',
              fontSize: '1.1rem',
              borderRadius: '25px',
              cursor: 'pointer',
              boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
            }}
          >
            View Demo
          </button>
        </div>

        <div style={{ 
          background: 'rgba(255,255,255,0.1)', 
          padding: '30px', 
          borderRadius: '15px',
          textAlign: 'center',
          backdropFilter: 'blur(10px)'
        }}>
          <h2 style={{ marginBottom: '15px' }}>✅ React App Successfully Deployed!</h2>
          <p style={{ marginBottom: '15px' }}>
            Your AI Brand Audit Tool is now live on Railway. The frontend is working perfectly!
          </p>
          <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>
            Status: Frontend ✅ | Backend: Next to implement
          </div>
        </div>
      </main>
    </div>
  )
}

export default App