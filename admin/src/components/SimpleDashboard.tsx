export function SimpleDashboard() {
  return (
    <div>
      <h2>Dashboard</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
        <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
          <h3>Total Licenses</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold' }}>0</p>
        </div>
        <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
          <h3>Total Models</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold' }}>0</p>
        </div>
        <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
          <h3>Active Engines</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold' }}>2</p>
        </div>
        <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
          <h3>System Status</h3>
          <p style={{ color: 'green' }}>✓ Healthy</p>
        </div>
      </div>
    </div>
  )
}