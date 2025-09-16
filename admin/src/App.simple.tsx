function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>BudConnect Admin Panel</h1>
      <p>Testing: If you see this, React is working!</p>
      <div style={{ marginTop: '20px' }}>
        <h2>Quick Links:</h2>
        <ul>
          <li><a href="/licenses">Licenses</a></li>
          <li><a href="/models">Models</a></li>
          <li><a href="/providers">Providers</a></li>
        </ul>
      </div>
    </div>
  )
}

export default App