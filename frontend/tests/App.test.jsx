import { render, screen } from '@testing-library/react'
import App from '../src/App'

describe('App', () => {
  it('should render the main application component', () => {
    render(<App />)
    // Assuming your App component renders some text like "Brand Audit Tool"
    expect(screen.getByText(/Brand Audit Tool/i)).toBeInTheDocument()
  })
})
