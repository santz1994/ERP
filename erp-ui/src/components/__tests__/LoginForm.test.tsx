import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from '../components/LoginForm';
import * as authService from '../services/authService';

jest.mock('../services/authService');

describe('LoginForm Component', () => {
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login form with username and password fields', () => {
    render(<LoginForm />);
    
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('submits form with valid credentials', async () => {
    const mockLogin = jest.fn().mockResolvedValue({ token: 'abc123' });
    authService.login.mockImplementation(mockLogin);

    render(<LoginForm />);

    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    await userEvent.type(usernameInput, 'user123');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('user123', 'password123');
    });
  });

  test('shows error message on failed login', async () => {
    const errorMessage = 'Invalid credentials';
    authService.login.mockRejectedValue(new Error(errorMessage));

    render(<LoginForm />);

    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    await userEvent.type(usernameInput, 'wrong');
    await userEvent.type(passwordInput, 'wrong');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  test('validates empty username', async () => {
    render(<LoginForm />);

    const submitButton = screen.getByRole('button', { name: /login/i });
    await userEvent.click(submitButton);

    expect(screen.getByText(/username is required/i)).toBeInTheDocument();
  });

  test('validates empty password', async () => {
    render(<LoginForm />);

    const usernameInput = screen.getByLabelText(/username/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    await userEvent.type(usernameInput, 'user123');
    await userEvent.click(submitButton);

    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
  });

  test('shows loading state during login', async () => {
    authService.login.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ token: 'abc123' }), 100))
    );

    render(<LoginForm />);

    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    await userEvent.type(usernameInput, 'user123');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);

    expect(screen.getByText(/logging in/i)).toBeInTheDocument();
  });

  test('handles remember me checkbox', async () => {
    render(<LoginForm />);

    const rememberCheckbox = screen.getByRole('checkbox', { name: /remember me/i });
    await userEvent.click(rememberCheckbox);

    expect(rememberCheckbox).toBeChecked();
  });

  test('disables submit button during submission', async () => {
    authService.login.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ token: 'abc123' }), 100))
    );

    render(<LoginForm />);

    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    await userEvent.type(usernameInput, 'user123');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);

    expect(submitButton).toBeDisabled();
  });

  test('focuses on username field on mount', () => {
    render(<LoginForm />);

    const usernameInput = screen.getByLabelText(/username/i) as HTMLInputElement;
    expect(usernameInput).toHaveFocus();
  });

  test('handles password reset link', async () => {
    render(<LoginForm />);

    const resetLink = screen.getByText(/forgot password/i);
    expect(resetLink).toBeInTheDocument();
  });

  test('clears form on successful login', async () => {
    authService.login.mockResolvedValue({ token: 'abc123' });

    render(<LoginForm onLoginSuccess={() => {}} />);

    const usernameInput = screen.getByLabelText(/username/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /login/i });

    await userEvent.type(usernameInput, 'user123');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(usernameInput.value).toBe('');
      expect(passwordInput.value).toBe('');
    });
  });
});
