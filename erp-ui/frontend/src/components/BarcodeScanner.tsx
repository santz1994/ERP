import React, { useState, useRef, useEffect } from 'react';
import { Html5QrcodeScanner, Html5Qrcode } from 'html5-qrcode';
import apiClient from '../api/client';

interface BarcodeScannerProps {
  onScan: (barcode: string) => void;
  operation: 'receive' | 'pick';
  location: 'warehouse' | 'finishgoods';
}

const BarcodeScanner: React.FC<BarcodeScannerProps> = ({ onScan, operation, location }) => {
  const [scanning, setScanning] = useState(false);
  const [manualInput, setManualInput] = useState('');
  const [cameraAvailable, setCameraAvailable] = useState(true);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const scannerRef = useRef<Html5QrcodeScanner | null>(null);
  const readerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check camera availability
    Html5Qrcode.getCameras().then(devices => {
      setCameraAvailable(devices && devices.length > 0);
    }).catch(err => {
      console.warn('Camera not available:', err);
      setCameraAvailable(false);
    });

    return () => {
      stopScanning();
    };
  }, []);

  const startScanning = () => {
    if (!readerRef.current || scanning) return;

    const scanner = new Html5QrcodeScanner(
      'barcode-reader',
      {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0
      },
      false
    );

    scanner.render(
      async (decodedText) => {
        console.log('Barcode scanned:', decodedText);
        await handleScan(decodedText);
        scanner.clear();
        setScanning(false);
      },
      (errorMessage) => {
        // Handle scan error (can be noisy, so we ignore most)
      }
    );

    scannerRef.current = scanner;
    setScanning(true);
  };

  const stopScanning = () => {
    if (scannerRef.current) {
      scannerRef.current.clear();
      scannerRef.current = null;
    }
    setScanning(false);
  };

  const handleScan = async (barcode: string) => {
    try {
      setError('');
      setValidationResult(null);

      // Validate barcode
      const response = await apiClient.post('/barcode/validate', {
        barcode,
        operation,
        location
      });

      if (response.data.valid) {
        setValidationResult(response.data);
        onScan(barcode);
      } else {
        setError(response.data.message);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to validate barcode');
    }
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (manualInput.trim()) {
      handleScan(manualInput.trim());
      setManualInput('');
    }
  };

  return (
    <div className="barcode-scanner bg-white rounded-lg shadow p-6">
      <h3 className="text-xl font-bold mb-4">
        Barcode Scanner - {operation === 'receive' ? 'Receiving' : 'Picking'} ({location})
      </h3>

      {/* Camera Scanner */}
      {cameraAvailable && (
        <div className="mb-6">
          <div id="barcode-reader" ref={readerRef} className="mb-4"></div>
          
          {!scanning ? (
            <button
              onClick={startScanning}
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Start Camera Scanner
            </button>
          ) : (
            <button
              onClick={stopScanning}
              className="w-full bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition"
            >
              Stop Scanner
            </button>
          )}
        </div>
      )}

      {/* Manual Input */}
      <div className="mb-6">
        <h4 className="font-semibold mb-2">Manual Barcode Entry</h4>
        <form onSubmit={handleManualSubmit} className="flex gap-2">
          <input
            type="text"
            value={manualInput}
            onChange={(e) => setManualInput(e.target.value)}
            placeholder="Enter barcode manually..."
            className="flex-1 border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="submit"
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition"
          >
            Submit
          </button>
        </form>
        <p className="text-sm text-gray-500 mt-2">
          Can't use camera? Type or paste the barcode here.
        </p>
      </div>

      {/* Validation Result */}
      {validationResult && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
          <div className="flex items-start gap-3">
            <svg className="w-6 h-6 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <h4 className="font-semibold text-green-800 mb-2">✓ Barcode Valid</h4>
              <div className="text-sm space-y-1">
                <p><strong>Product:</strong> {validationResult.product_name}</p>
                <p><strong>Code:</strong> {validationResult.product_code}</p>
                <p><strong>Current Stock:</strong> {validationResult.current_qty}</p>
                {validationResult.lot_number && (
                  <p><strong>Latest Lot:</strong> {validationResult.lot_number}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg className="w-6 h-6 text-red-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <h4 className="font-semibold text-red-800 mb-1">Scan Error</h4>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
        <h4 className="font-semibold text-blue-800 mb-2">📱 How to Use</h4>
        <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
          <li>Click "Start Camera Scanner" and point camera at barcode</li>
          <li>Or enter barcode manually in the text field</li>
          <li>Product information will appear after successful scan</li>
          <li>Then proceed to enter quantity and complete the transaction</li>
        </ul>
      </div>
    </div>
  );
};

export default BarcodeScanner;
