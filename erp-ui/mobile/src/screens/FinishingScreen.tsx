import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ScrollView,
  ActivityIndicator,
  TextInput,
  Modal,
} from 'react-native';
import { Camera } from 'expo-camera';
import * as Haptics from 'expo-haptics';
import { apiClient } from '../api/client';
import { useAuth } from '../contexts/AuthContext';

interface ScannedProduct {
  id: string;
  productName: string;
  sku: string;
  batchId: string;
  size: string;
  quantity: number;
  stage: string;
  lastUpdated: string;
}

interface FinishingCheckpoint {
  trimmed: boolean;
  pressed: boolean;
  labeled: boolean;
  measured: boolean;
  functionality: boolean;
  qualityApproved: boolean;
  notes: string;
}

const FinishingScreen: React.FC = () => {
  const { user } = useAuth();
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [cameraType, setCameraType] = useState('back');
  const [scannedData, setScannedData] = useState<string>('');
  const [scannedProduct, setScannedProduct] = useState<ScannedProduct | null>(null);
  const [loading, setLoading] = useState(false);
  const [checkpoints, setCheckpoints] = useState<FinishingCheckpoint>({
    trimmed: false,
    pressed: false,
    labeled: false,
    measured: false,
    functionality: false,
    qualityApproved: false,
    notes: '',
  });
  const [showScanner, setShowScanner] = useState(true);
  const [showManualEntry, setShowManualEntry] = useState(false);
  const [manualSKU, setManualSKU] = useState('');
  const [defectNotes, setDefectNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const cameraRef = useRef<Camera>(null);

  // Request camera permission
  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'Camera access is required for barcode scanning');
      }
    })();
  }, []);

  // Handle barcode scan (using camera text recognition)
  const handleBarcodeScan = async (barcode: string) => {
    if (!barcode || barcode.length < 3) return;

    setScannedData(barcode);
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);

    // Stop camera
    setShowScanner(false);

    // Fetch product details
    fetchProductDetails(barcode);
  };

  // Fetch product details from API
  const fetchProductDetails = async (sku: string) => {
    setLoading(true);
    try {
      const response = await apiClient.get(`/finishing/products/${sku}`);
      const product = response.data;

      setScannedProduct({
        id: product.id,
        productName: product.productName,
        sku: product.sku,
        batchId: product.batchId,
        size: product.size,
        quantity: product.quantity,
        stage: product.stage,
        lastUpdated: new Date(product.lastUpdated).toLocaleString(),
      });

      // Reset checkpoints for new product
      setCheckpoints({
        trimmed: false,
        pressed: false,
        labeled: false,
        measured: false,
        functionality: false,
        qualityApproved: false,
        notes: '',
      });
      setDefectNotes('');
    } catch (error) {
      Alert.alert('Error', `Product not found: ${sku}`);
      setShowScanner(true);
    } finally {
      setLoading(false);
    }
  };

  // Update checkpoint status
  const toggleCheckpoint = (key: keyof FinishingCheckpoint) => {
    if (key !== 'notes') {
      setCheckpoints({
        ...checkpoints,
        [key]: !checkpoints[key as keyof Omit<FinishingCheckpoint, 'notes'>],
      });
    }
  };

  // Submit finishing data
  const handleSubmitFinishing = async () => {
    if (!scannedProduct) {
      Alert.alert('Error', 'No product scanned');
      return;
    }

    // Validate all checkpoints are completed
    const allCheckpointsComplete =
      checkpoints.trimmed &&
      checkpoints.pressed &&
      checkpoints.labeled &&
      checkpoints.measured &&
      checkpoints.functionality &&
      checkpoints.qualityApproved;

    if (!allCheckpointsComplete) {
      Alert.alert('Incomplete', 'All quality checkpoints must be completed');
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        productId: scannedProduct.id,
        sku: scannedProduct.sku,
        batchId: scannedProduct.batchId,
        finishingCheckpoints: checkpoints,
        operator: user?.username,
        timestamp: new Date().toISOString(),
      };

      const response = await apiClient.post('/finishing/complete', payload);

      if (response.status === 200 || response.status === 201) {
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        Alert.alert('Success', `Product ${scannedProduct.sku} marked as finished`);

        // Reset for next product
        setScannedProduct(null);
        setScannedData('');
        setShowScanner(true);
        setDefectNotes('');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to submit finishing data');
      console.error(error);
    } finally {
      setSubmitting(false);
    }
  };

  // Reject/Mark defect
  const handleRejectProduct = async () => {
    if (!scannedProduct) return;

    Alert.alert('Confirm Rejection', 'Mark this product as defective?', [
      { text: 'Cancel', onPress: () => {} },
      {
        text: 'Confirm',
        onPress: async () => {
          setSubmitting(true);
          try {
            const payload = {
              productId: scannedProduct.id,
              sku: scannedProduct.sku,
              batchId: scannedProduct.batchId,
              status: 'DEFECTIVE',
              defectReason: defectNotes || 'Quality issue detected',
              operator: user?.username,
              timestamp: new Date().toISOString(),
            };

            await apiClient.post('/finishing/reject', payload);
            await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
            Alert.alert('Marked', 'Product marked as defective for rework');

            // Reset
            setScannedProduct(null);
            setShowScanner(true);
            setDefectNotes('');
          } catch (error) {
            Alert.alert('Error', 'Failed to mark product as defective');
          } finally {
            setSubmitting(false);
          }
        },
      },
    ]);
  };

  // Manual SKU entry
  const handleManualEntry = () => {
    if (!manualSKU.trim()) {
      Alert.alert('Error', 'Please enter SKU');
      return;
    }
    fetchProductDetails(manualSKU);
    setShowManualEntry(false);
    setManualSKU('');
  };

  if (hasPermission === null) {
    return (
      <View style={styles.container}>
        <Text>Requesting camera permission...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Camera permission denied</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Camera Scanner */}
      {showScanner && !scannedProduct ? (
        <View style={styles.cameraContainer}>
          <Camera
            ref={cameraRef}
            style={styles.camera}
            type={cameraType as any}
            onCameraReady={async () => {
              // Camera is ready - set up barcode detection
              // Note: Expo Camera doesn't have built-in barcode scanning
              // For production, use react-native-vision-camera with VisionCamera Barcode plugin
            }}
          />
          <View style={styles.cameraOverlay}>
            <View style={styles.scanBox} />
            <Text style={styles.scanText}>Align barcode within frame</Text>
          </View>

          {/* Manual Entry Button */}
          <TouchableOpacity
            style={styles.manualEntryBtn}
            onPress={() => setShowManualEntry(true)}
          >
            <Text style={styles.btnText}>📝 Manual Entry</Text>
          </TouchableOpacity>
        </View>
      ) : null}

      {/* Manual Entry Modal */}
      <Modal visible={showManualEntry} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Enter SKU/Barcode</Text>
            <TextInput
              style={styles.input}
              placeholder="Scan or type SKU"
              value={manualSKU}
              onChangeText={setManualSKU}
              autoFocus
            />
            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.button, styles.cancelBtn]}
                onPress={() => setShowManualEntry(false)}
              >
                <Text style={styles.btnText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.button, styles.submitBtn]}
                onPress={handleManualEntry}
              >
                <Text style={styles.btnText}>Search</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Product Details & Checkpoints */}
      {scannedProduct && (
        <ScrollView style={styles.detailsContainer}>
          <View style={styles.productHeader}>
            <Text style={styles.productName}>{scannedProduct.productName}</Text>
            <Text style={styles.sku}>SKU: {scannedProduct.sku}</Text>
            <Text style={styles.batchId}>Batch: {scannedProduct.batchId}</Text>
            <Text style={styles.size}>Size: {scannedProduct.size}</Text>
            <Text style={styles.quantity}>Qty: {scannedProduct.quantity} units</Text>
          </View>

          {/* Quality Checkpoints */}
          <View style={styles.checkpointsContainer}>
            <Text style={styles.sectionTitle}>Finishing Checkpoints</Text>

            {/* Trim Loose Threads */}
            <TouchableOpacity
              style={[
                styles.checkpoint,
                checkpoints.trimmed && styles.checkpointComplete,
              ]}
              onPress={() => toggleCheckpoint('trimmed')}
            >
              <Text style={styles.checkpointIcon}>
                {checkpoints.trimmed ? '✅' : '⭕'}
              </Text>
              <Text style={styles.checkpointText}>Trim loose threads</Text>
              <Text style={styles.checkpointDesc}>Check for any loose threads</Text>
            </TouchableOpacity>

            {/* Press */}
            <TouchableOpacity
              style={[
                styles.checkpoint,
                checkpoints.pressed && styles.checkpointComplete,
              ]}
              onPress={() => toggleCheckpoint('pressed')}
            >
              <Text style={styles.checkpointIcon}>
                {checkpoints.pressed ? '✅' : '⭕'}
              </Text>
              <Text style={styles.checkpointText}>Press with steam (180°C)</Text>
              <Text style={styles.checkpointDesc}>2-3 seconds per piece</Text>
            </TouchableOpacity>

            {/* Attach Labels */}
            <TouchableOpacity
              style={[
                styles.checkpoint,
                checkpoints.labeled && styles.checkpointComplete,
              ]}
              onPress={() => toggleCheckpoint('labeled')}
            >
              <Text style={styles.checkpointIcon}>
                {checkpoints.labeled ? '✅' : '⭕'}
              </Text>
              <Text style={styles.checkpointText}>Attach labels</Text>
              <Text style={styles.checkpointDesc}>
                Main label, care label, barcode
              </Text>
            </TouchableOpacity>

            {/* Measurement Check */}
            <TouchableOpacity
              style={[
                styles.checkpoint,
                checkpoints.measured && styles.checkpointComplete,
              ]}
              onPress={() => toggleCheckpoint('measured')}
            >
              <Text style={styles.checkpointIcon}>
                {checkpoints.measured ? '✅' : '⭕'}
              </Text>
              <Text style={styles.checkpointText}>Measurement check</Text>
              <Text style={styles.checkpointDesc}>Length/width ±2cm, sleeves ±1cm</Text>
            </TouchableOpacity>

            {/* Functionality Test */}
            <TouchableOpacity
              style={[
                styles.checkpoint,
                checkpoints.functionality && styles.checkpointComplete,
              ]}
              onPress={() => toggleCheckpoint('functionality')}
            >
              <Text style={styles.checkpointIcon}>
                {checkpoints.functionality ? '✅' : '⭕'}
              </Text>
              <Text style={styles.checkpointText}>Functionality test</Text>
              <Text style={styles.checkpointDesc}>
                Zippers, buttons, elastic - all working
              </Text>
            </TouchableOpacity>

            {/* Quality Approval */}
            <TouchableOpacity
              style={[
                styles.checkpoint,
                checkpoints.qualityApproved && styles.checkpointComplete,
              ]}
              onPress={() => toggleCheckpoint('qualityApproved')}
            >
              <Text style={styles.checkpointIcon}>
                {checkpoints.qualityApproved ? '✅' : '⭕'}
              </Text>
              <Text style={styles.checkpointText}>Quality approval</Text>
              <Text style={styles.checkpointDesc}>All checks passed, ready for pack</Text>
            </TouchableOpacity>
          </View>

          {/* Defect Notes */}
          <View style={styles.notesContainer}>
            <Text style={styles.sectionTitle}>Notes / Issues</Text>
            <TextInput
              style={styles.notesInput}
              placeholder="Any defects or issues found..."
              multiline
              numberOfLines={3}
              value={defectNotes}
              onChangeText={setDefectNotes}
            />
          </View>

          {/* Action Buttons */}
          <View style={styles.actionButtons}>
            <TouchableOpacity
              style={[styles.button, styles.scanAgainBtn]}
              onPress={() => {
                setScannedProduct(null);
                setShowScanner(true);
              }}
              disabled={submitting}
            >
              <Text style={styles.btnText}>🔄 Scan Next</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.rejectBtn]}
              onPress={handleRejectProduct}
              disabled={submitting}
            >
              <Text style={styles.btnText}>❌ Reject</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.submitBtn]}
              onPress={handleSubmitFinishing}
              disabled={submitting}
            >
              {submitting ? (
                <ActivityIndicator color="white" />
              ) : (
                <Text style={styles.btnText}>✅ Mark Finished</Text>
              )}
            </TouchableOpacity>
          </View>

          <View style={styles.spacer} />
        </ScrollView>
      )}

      {/* Loading Indicator */}
      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="white" />
          <Text style={styles.loadingText}>Fetching product details...</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  cameraContainer: {
    flex: 1,
    position: 'relative',
  },
  camera: {
    flex: 1,
  },
  cameraOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scanBox: {
    width: 250,
    height: 250,
    borderWidth: 3,
    borderColor: '#00ff00',
    borderRadius: 10,
    backgroundColor: 'transparent',
  },
  scanText: {
    color: '#fff',
    fontSize: 16,
    marginTop: 20,
    textAlign: 'center',
  },
  manualEntryBtn: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    backgroundColor: '#2196F3',
    padding: 12,
    borderRadius: 8,
  },
  detailsContainer: {
    flex: 1,
    padding: 16,
  },
  productHeader: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  productName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  sku: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  batchId: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  size: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  quantity: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2196F3',
  },
  checkpointsContainer: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  checkpoint: {
    backgroundColor: '#fff',
    padding: 12,
    marginBottom: 8,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    borderLeftWidth: 4,
    borderLeftColor: '#ddd',
  },
  checkpointComplete: {
    borderLeftColor: '#4CAF50',
    backgroundColor: '#f1f8f6',
  },
  checkpointIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  checkpointText: {
    flex: 1,
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  checkpointDesc: {
    fontSize: 12,
    color: '#999',
    position: 'absolute',
    bottom: 4,
    left: 48,
  },
  notesContainer: {
    marginBottom: 16,
  },
  notesInput: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    minHeight: 80,
    color: '#333',
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 20,
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  scanAgainBtn: {
    backgroundColor: '#2196F3',
  },
  rejectBtn: {
    backgroundColor: '#ff9800',
  },
  submitBtn: {
    backgroundColor: '#4CAF50',
  },
  cancelBtn: {
    backgroundColor: '#999',
  },
  btnText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#fff',
    marginTop: 16,
    fontSize: 14,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    padding: 16,
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
  },
  modalTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    fontSize: 14,
  },
  modalButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  spacer: {
    height: 20,
  },
});

export default FinishingScreen;
