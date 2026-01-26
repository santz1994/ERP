import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DailyProductionForm } from '../components/DailyProductionForm';
import * as productionService from '../services/productionService';

jest.mock('../services/productionService');

describe('DailyProductionForm Component', () => {

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders form with all required fields', () => {
    render(<DailyProductionForm />);

    expect(screen.getByLabelText(/line/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/article/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/quantity/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/date/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit|record/i })).toBeInTheDocument();
  });

  test('records daily production with valid data', async () => {
    const mockRecord = jest.fn().mockResolvedValue({ id: 1, quantity: 100 });
    productionService.recordProduction.mockImplementation(mockRecord);

    render(<DailyProductionForm />);

    const lineSelect = screen.getByLabelText(/line/i);
    const articleSelect = screen.getByLabelText(/article/i);
    const quantityInput = screen.getByLabelText(/quantity/i);
    const submitButton = screen.getByRole('button', { name: /submit|record/i });

    await userEvent.selectOption(lineSelect, 'LINE001');
    await userEvent.selectOption(articleSelect, 'ARTICLE001');
    await userEvent.type(quantityInput, '100');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockRecord).toHaveBeenCalledWith(
        expect.objectContaining({
          lineId: 'LINE001',
          articleId: 'ARTICLE001',
          quantity: 100
        })
      );
    });
  });

  test('validates positive quantity', async () => {
    render(<DailyProductionForm />);

    const quantityInput = screen.getByLabelText(/quantity/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /submit|record/i });

    await userEvent.type(quantityInput, '-50');
    await userEvent.click(submitButton);

    expect(screen.getByText(/quantity must be positive/i)).toBeInTheDocument();
  });

  test('validates reasonable quantity limit', async () => {
    render(<DailyProductionForm />);

    const quantityInput = screen.getByLabelText(/quantity/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /submit|record/i });

    await userEvent.type(quantityInput, '50000');
    await userEvent.click(submitButton);

    expect(screen.getByText(/quantity exceeds maximum/i)).toBeInTheDocument();
  });

  test('validates required fields', async () => {
    render(<DailyProductionForm />);

    const submitButton = screen.getByRole('button', { name: /submit|record/i });
    await userEvent.click(submitButton);

    expect(screen.getByText(/line is required/i)).toBeInTheDocument();
    expect(screen.getByText(/article is required/i)).toBeInTheDocument();
    expect(screen.getByText(/quantity is required/i)).toBeInTheDocument();
  });

  test('shows success message on record submission', async () => {
    productionService.recordProduction.mockResolvedValue({ id: 1 });

    render(<DailyProductionForm />);

    const lineSelect = screen.getByLabelText(/line/i);
    const articleSelect = screen.getByLabelText(/article/i);
    const quantityInput = screen.getByLabelText(/quantity/i);
    const submitButton = screen.getByRole('button', { name: /submit|record/i });

    await userEvent.selectOption(lineSelect, 'LINE001');
    await userEvent.selectOption(articleSelect, 'ARTICLE001');
    await userEvent.type(quantityInput, '100');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/production recorded successfully/i)).toBeInTheDocument();
    });
  });

  test('shows error message on submission failure', async () => {
    const errorMessage = 'Recording failed';
    productionService.recordProduction.mockRejectedValue(new Error(errorMessage));

    render(<DailyProductionForm />);

    const lineSelect = screen.getByLabelText(/line/i);
    const articleSelect = screen.getByLabelText(/article/i);
    const quantityInput = screen.getByLabelText(/quantity/i);
    const submitButton = screen.getByRole('button', { name: /submit|record/i });

    await userEvent.selectOption(lineSelect, 'LINE001');
    await userEvent.selectOption(articleSelect, 'ARTICLE001');
    await userEvent.type(quantityInput, '100');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  test('prevents double submission', async () => {
    const mockRecord = jest.fn().mockResolvedValue({ id: 1 });
    productionService.recordProduction.mockImplementation(mockRecord);

    render(<DailyProductionForm />);

    const submitButton = screen.getByRole('button', { name: /submit|record/i });

    await userEvent.click(submitButton);
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockRecord).toHaveBeenCalledTimes(1);
    });
  });

  test('disables submit button during submission', async () => {
    productionService.recordProduction.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ id: 1 }), 100))
    );

    render(<DailyProductionForm />);

    const submitButton = screen.getByRole('button', { name: /submit|record/i });
    await userEvent.click(submitButton);

    expect(submitButton).toBeDisabled();
  });

  test('shows loading indicator during submission', async () => {
    productionService.recordProduction.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ id: 1 }), 100))
    );

    render(<DailyProductionForm />);

    const submitButton = screen.getByRole('button', { name: /submit|record/i });
    await userEvent.click(submitButton);

    expect(screen.getByText(/recording/i)).toBeInTheDocument();
  });

  test('clears form after successful submission', async () => {
    productionService.recordProduction.mockResolvedValue({ id: 1 });

    render(<DailyProductionForm />);

    const lineSelect = screen.getByLabelText(/line/i) as HTMLSelectElement;
    const articleSelect = screen.getByLabelText(/article/i) as HTMLSelectElement;
    const quantityInput = screen.getByLabelText(/quantity/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /submit|record/i });

    await userEvent.selectOption(lineSelect, 'LINE001');
    await userEvent.selectOption(articleSelect, 'ARTICLE001');
    await userEvent.type(quantityInput, '100');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(lineSelect.value).toBe('');
      expect(articleSelect.value).toBe('');
      expect(quantityInput.value).toBe('');
    });
  });

  test('sets today as default date', () => {
    render(<DailyProductionForm />);

    const dateInput = screen.getByLabelText(/date/i) as HTMLInputElement;
    const today = new Date().toISOString().split('T')[0];

    expect(dateInput.value).toBe(today);
  });

  test('handles quick record buttons', async () => {
    productionService.recordProduction.mockResolvedValue({ id: 1 });

    render(<DailyProductionForm />);

    const quick100Button = screen.getByRole('button', { name: /100/i });
    await userEvent.click(quick100Button);

    const quantityInput = screen.getByLabelText(/quantity/i) as HTMLInputElement;
    expect(quantityInput.value).toBe('100');
  });

  test('calculates running total', async () => {
    const dailyProductions = [
      { quantity: 100 },
      { quantity: 150 },
      { quantity: 200 }
    ];

    render(<DailyProductionForm productions={dailyProductions} />);

    const total = dailyProductions.reduce((sum, p) => sum + p.quantity, 0);
    expect(screen.getByText(`Total: ${total}`)).toBeInTheDocument();
  });
});
