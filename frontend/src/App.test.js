import { render, screen } from '@testing-library/react';
import App from './App';

test('renders vision assistant heading', () => {
  render(<App />);
  const headingElement = screen.getByText(/YOLO Vision Assistant/i);
  expect(headingElement).toBeInTheDocument();
});
