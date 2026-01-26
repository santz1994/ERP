/**
 * FinishGood Mobile Screen
 * Barcode scanning for finished goods warehouse management
 * 
 * Features:
 * - Scan barcode per box (IKEA-style article)
 * - Receive goods from packing department
 * - Count and confirm per-box packing
 * - Track shipment preparation
 * - Real-time inventory updates
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  FlatList,
  SafeAreaView,
  Modal,
} from 'react-native';
import { Camera } from 'expo-camera';
import { BarCodeScanner } from 'expo-barcode-scanner';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useNavigation } from '@react-navigation/native';
import axios from 'axios';

// ==================== TYPES ====================

interface FinishGoodItem {
  id: string;
  barcode: string;
  productCode: string;
  productName: string;
  articleIKEA: string;
  moId: number;
  quantity: number;
  unitPerBox: number;
  boxCount: number;
  location: string;
  receivedDate: string;
  packingDate: string;
  destination?: string;
  status: 'scanned' | 'received' | 'prepared_for_shipment';
  scanHistory: ScanRecord[];
}

interface ScanRecord {
  timestamp: string;
  barcode: string;
  action: 'scan' | 'verify' | 'confirm';
  userId: number;
  quantity: number;
}

interface ShipmentBoxData {
  boxNumber: number;
  barcode: string;
  productCode: string;
  quantity: number;
  scannedCount: number;
  expectedCount: number;
  isComplete: boolean;
}

interface TransferData {
  transferId: number;
  moId: number;
  productCode: string;
  productName: string;
  totalQuantity: number;
  boxesCount: number;
  unitPerBox: number;
  status: 'pending' | 'received' | 'confirmed';
}

// ==================== API SERVICES ====================

class FinishGoodService {
  private apiClient: axios.AxiosInstance;
  private baseURL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

  constructor() {
    this.apiClient = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
    });

    // Add auth token interceptor
    this.setupInterceptors();
  }

  private async setupInterceptors() {
    const token = await AsyncStorage.getItem('jwt_token');
    if (token) {
      this.apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }

  /**
   * Get all pending transfers from Packing department
   */
  async getPendingTransfers(): Promise<TransferData[]> {
    try {
      const response = await this.apiClient.get('/finishgoods/pending-transfers');
      return response.data;
    } catch (error) {
      console.error('Error fetching pending transfers:', error);
      throw new Error('Failed to fetch pending transfers');
    }
  }

  /**
   * Validate barcode format and get product info
   */
  async validateBarcode(barcode: string): Promise<FinishGoodItem> {
    try {
      const response = await this.apiClient.get(`/finishgoods/barcode/${barcode}`);
      return response.data;
    } catch (error) {
      console.error('Error validating barcode:', error);
      throw new Error('Invalid barcode or product not found');
    }
  }

  /**
   * Scan box - record barcode for goods receiving
   */
  async scanBox(
    barcode: string,
    moId: number,
    boxNumber: number,
    quantity: number
  ): Promise<ScanRecord> {
    try {
      const response = await this.apiClient.post('/finishgoods/scan-box', {
        barcode,
        mo_id: moId,
        box_number: boxNumber,
        quantity,
        scanned_at: new Date().toISOString(),
      });
      return response.data;
    } catch (error) {
      console.error('Error scanning box:', error);
      throw new Error('Failed to record box scan');
    }
  }

  /**
   * Confirm receipt of finished goods from packing
   */
  async confirmReceipt(
    transferId: number,
    scannedBoxes: ShipmentBoxData[]
  ): Promise<any> {
    try {
      const response = await this.apiClient.post('/finishgoods/receive-from-packing', {
        transfer_id: transferId,
        scanned_boxes: scannedBoxes,
        received_at: new Date().toISOString(),
        received_by_user_id: await this.getCurrentUserId(),
      });
      return response.data;
    } catch (error) {
      console.error('Error confirming receipt:', error);
      throw new Error('Failed to confirm goods receipt');
    }
  }

  /**
   * Prepare shipment - transition goods to prepared state
   */
  async prepareShipment(
    moId: number,
    destination: string
  ): Promise<any> {
    try {
      const response = await this.apiClient.post('/finishgoods/prepare-shipment', {
        mo_id: moId,
        destination,
        prepared_at: new Date().toISOString(),
        prepared_by_user_id: await this.getCurrentUserId(),
      });
      return response.data;
    } catch (error) {
      console.error('Error preparing shipment:', error);
      throw new Error('Failed to prepare shipment');
    }
  }

  /**
   * Get inventory by product code
   */
  async getInventoryByProduct(productCode: string): Promise<any> {
    try {
      const response = await this.apiClient.get('/finishgoods/inventory', {
        params: { product_code: productCode },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching inventory:', error);
      throw new Error('Failed to fetch inventory');
    }
  }

  private async getCurrentUserId(): Promise<number> {
    const userJson = await AsyncStorage.getItem('user');
    if (!userJson) throw new Error('User not authenticated');
    return JSON.parse(userJson).id;
  }
}

// ==================== MAIN COMPONENT ====================

export const FinishGoodScreen: React.FC = () => {
  const navigation = useNavigation();
  const [currentMode, setCurrentMode] = useState<'pending' | 'scan' | 'confirm'>('pending');
  
  // Camera & Barcode states
  const [cameraVisible, setCameraVisible] = useState(false);
  const [cameraPermission, setCameraPermission] = useState<boolean | null>(null);
  const cameraRef = useRef<any>(null);

  // Data states
  const [pendingTransfers, setPendingTransfers] = useState<TransferData[]>([]);
  const [selectedTransfer, setSelectedTransfer] = useState<TransferData | null>(null);
  const [scannedBoxes, setScannedBoxes] = useState<ShipmentBoxData[]>([]);
  const [finishGoodItems, setFinishGoodItems] = useState<FinishGoodItem[]>([]);

  // UI states
  const [loading, setLoading] = useState(false);
  const [manualBarcode, setManualBarcode] = useState('');
  const [currentBoxNumber, setCurrentBoxNumber] = useState(1);
  const [confirmationModal, setConfirmationModal] = useState(false);
  const [shippingDestination, setShippingDestination] = useState('');

  const service = useRef(new FinishGoodService()).current;

  // ==================== LIFECYCLE ====================

  useEffect(() => {
    initializeScreen();
  }, []);

  useEffect(() => {
    requestCameraPermission();
  }, []);

  // ==================== INITIALIZATION ====================

  const initializeScreen = async () => {
    try {
      setLoading(true);
      const transfers = await service.getPendingTransfers();
      setPendingTransfers(transfers);
    } catch (error) {
      Alert.alert('Error', 'Failed to load pending transfers');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const requestCameraPermission = async () => {
    const { status } = await Camera.requestCameraPermissionsAsync();
    setCameraPermission(status === 'granted');
  };

  // ==================== BARCODE SCANNING ====================

  const handleBarCodeScanned = ({ type, data }: { type: string; data: string }) => {
    // Prevent duplicate scans
    setCameraVisible(false);
    
    processBarcodeScan(data);
  };

  const processBarcodeScan = async (barcode: string) => {
    if (!selectedTransfer) {
      Alert.alert('Error', 'Please select a transfer first');
      return;
    }

    try {
      setLoading(true);

      // Validate barcode
      const productInfo = await service.validateBarcode(barcode);

      // Create box data
      const newBox: ShipmentBoxData = {
        boxNumber: currentBoxNumber,
        barcode,
        productCode: productInfo.productCode,
        quantity: productInfo.quantity,
        scannedCount: productInfo.quantity,
        expectedCount: selectedTransfer.unitPerBox,
        isComplete: productInfo.quantity === selectedTransfer.unitPerBox,
      };

      // Record scan
      await service.scanBox(
        barcode,
        selectedTransfer.moId,
        currentBoxNumber,
        productInfo.quantity
      );

      // Add to scanned boxes
      setScannedBoxes([...scannedBoxes, newBox]);
      setFinishGoodItems([...finishGoodItems, productInfo]);

      // Increment box counter
      setCurrentBoxNumber(currentBoxNumber + 1);

      // Show feedback
      Alert.alert(
        'Success',
        `Box #${currentBoxNumber} scanned successfully\n${productInfo.productCode} - ${productInfo.quantity} units`,
        [{ text: 'Continue', onPress: () => setCameraVisible(true) }]
      );
    } catch (error) {
      Alert.alert('Error', error instanceof Error ? error.message : 'Failed to process barcode');
    } finally {
      setLoading(false);
    }
  };

  const handleManualBarcodeEntry = () => {
    if (!manualBarcode.trim()) {
      Alert.alert('Error', 'Please enter a barcode');
      return;
    }

    processBarcodeScan(manualBarcode);
    setManualBarcode('');
  };

  // ==================== RECEIPT CONFIRMATION ====================

  const handleConfirmReceipt = async () => {
    if (!selectedTransfer || scannedBoxes.length === 0) {
      Alert.alert('Error', 'No boxes scanned yet');
      return;
    }

    try {
      setLoading(true);

      await service.confirmReceipt(selectedTransfer.transferId, scannedBoxes);

      Alert.alert(
        'Success',
        `Received ${scannedBoxes.length} boxes\nTotal: ${scannedBoxes.reduce((sum, b) => sum + b.quantity, 0)} units`,
        [
          {
            text: 'OK',
            onPress: () => {
              resetScanSession();
              setCurrentMode('pending');
            },
          },
        ]
      );
    } catch (error) {
      Alert.alert('Error', error instanceof Error ? error.message : 'Failed to confirm receipt');
    } finally {
      setLoading(false);
    }
  };

  // ==================== SHIPMENT PREPARATION ====================

  const handlePrepareShipment = async () => {
    if (!selectedTransfer || !shippingDestination.trim()) {
      Alert.alert('Error', 'Please select destination and confirm receipt first');
      return;
    }

    try {
      setLoading(true);

      await service.prepareShipment(selectedTransfer.moId, shippingDestination);

      Alert.alert(
        'Success',
        `Shipment prepared for ${shippingDestination}`,
        [
          {
            text: 'OK',
            onPress: () => {
              resetScanSession();
              setConfirmationModal(false);
              setCurrentMode('pending');
            },
          },
        ]
      );
    } catch (error) {
      Alert.alert('Error', error instanceof Error ? error.message : 'Failed to prepare shipment');
    } finally {
      setLoading(false);
    }
  };

  // ==================== UTILITIES ====================

  const resetScanSession = () => {
    setSelectedTransfer(null);
    setScannedBoxes([]);
    setFinishGoodItems([]);
    setCurrentBoxNumber(1);
    setShippingDestination('');
  };

  const calculateStats = () => {
    return {
      totalBoxes: scannedBoxes.length,
      totalUnits: scannedBoxes.reduce((sum, b) => sum + b.quantity, 0),
      completeBoxes: scannedBoxes.filter(b => b.isComplete).length,
      incompleteBoxes: scannedBoxes.filter(b => !b.isComplete).length,
    };
  };

  const validateAllBoxesComplete = () => {
    return scannedBoxes.every(b => b.isComplete);
  };

  // ==================== RENDER METHODS ====================

  const renderPendingTransfers = () => (
    <View style={styles.container}>
      <Text style={styles.title}>📦 Pending Transfers</Text>

      {pendingTransfers.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>No pending transfers</Text>
        </View>
      ) : (
        <FlatList
          scrollEnabled={false}
          data={pendingTransfers}
          keyExtractor={(item) => item.moId.toString()}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[
                styles.transferCard,
                selectedTransfer?.moId === item.moId && styles.transferCardSelected,
              ]}
              onPress={() => {
                setSelectedTransfer(item);
                setCurrentMode('scan');
              }}
            >
              <View style={styles.transferCardContent}>
                <Text style={styles.transferCardTitle}>{item.productCode}</Text>
                <Text style={styles.transferCardSubtitle}>{item.productName}</Text>
                <View style={styles.transferCardDetails}>
                  <Text style={styles.detailText}>
                    📊 {item.totalQuantity} units / {item.boxesCount} boxes
                  </Text>
                  <Text style={styles.detailText}>
                    📦 {item.unitPerBox} units per box
                  </Text>
                  <Text style={styles.statusBadge}>{item.status.toUpperCase()}</Text>
                </View>
              </View>
            </TouchableOpacity>
          )}
        />
      )}
    </View>
  );

  const renderScanMode = () => {
    const stats = calculateStats();

    return (
      <SafeAreaView style={styles.container}>
        <ScrollView style={styles.scrollView}>
          {/* Header */}
          <View style={styles.scanHeader}>
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => {
                resetScanSession();
                setCurrentMode('pending');
              }}
            >
              <Text style={styles.backButtonText}>← Back</Text>
            </TouchableOpacity>
            <Text style={styles.scanTitle}>Scan Finished Goods</Text>
          </View>

          {/* Transfer Info */}
          {selectedTransfer && (
            <View style={styles.transferInfo}>
              <Text style={styles.transferInfoTitle}>{selectedTransfer.productCode}</Text>
              <Text style={styles.transferInfoSubtitle}>{selectedTransfer.productName}</Text>
              <View style={styles.transferInfoDetails}>
                <View style={styles.infoBadge}>
                  <Text style={styles.infoBadgeLabel}>MO ID</Text>
                  <Text style={styles.infoBadgeValue}>{selectedTransfer.moId}</Text>
                </View>
                <View style={styles.infoBadge}>
                  <Text style={styles.infoBadgeLabel}>Total Units</Text>
                  <Text style={styles.infoBadgeValue}>{selectedTransfer.totalQuantity}</Text>
                </View>
                <View style={styles.infoBadge}>
                  <Text style={styles.infoBadgeLabel}>Expected Boxes</Text>
                  <Text style={styles.infoBadgeValue}>{selectedTransfer.boxesCount}</Text>
                </View>
              </View>
            </View>
          )}

          {/* Camera Button */}
          <TouchableOpacity
            style={styles.cameraButton}
            onPress={() => setCameraVisible(true)}
            disabled={loading}
          >
            <Text style={styles.cameraButtonText}>📱 Tap to Scan Barcode</Text>
          </TouchableOpacity>

          {/* Manual Entry */}
          <View style={styles.manualEntrySection}>
            <Text style={styles.sectionLabel}>Or Enter Barcode Manually</Text>
            <View style={styles.manualEntryGroup}>
              <TextInput
                style={styles.manualBarcodeInput}
                placeholder="Scan or type barcode..."
                value={manualBarcode}
                onChangeText={setManualBarcode}
                onSubmitEditing={handleManualBarcodeEntry}
                placeholderTextColor="#999"
                editable={!loading}
              />
              <TouchableOpacity
                style={styles.manualEntryButton}
                onPress={handleManualBarcodeEntry}
                disabled={loading || !manualBarcode.trim()}
              >
                <Text style={styles.manualEntryButtonText}>Enter</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Statistics */}
          <View style={styles.statsContainer}>
            <View style={styles.statCard}>
              <Text style={styles.statLabel}>Boxes Scanned</Text>
              <Text style={styles.statValue}>{stats.totalBoxes}</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statLabel}>Total Units</Text>
              <Text style={styles.statValue}>{stats.totalUnits}</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statLabel}>Complete</Text>
              <Text style={[styles.statValue, { color: '#4CAF50' }]}>
                {stats.completeBoxes}
              </Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statLabel}>Incomplete</Text>
              <Text style={[styles.statValue, { color: stats.incompleteBoxes > 0 ? '#FF9800' : '#4CAF50' }]}>
                {stats.incompleteBoxes}
              </Text>
            </View>
          </View>

          {/* Scanned Boxes List */}
          {scannedBoxes.length > 0 && (
            <View style={styles.scannedBoxesSection}>
              <Text style={styles.sectionLabel}>📋 Scanned Boxes</Text>
              {scannedBoxes.map((box, index) => (
                <View
                  key={index}
                  style={[
                    styles.boxItem,
                    box.isComplete ? styles.boxItemComplete : styles.boxItemIncomplete,
                  ]}
                >
                  <View style={styles.boxItemHeader}>
                    <Text style={styles.boxNumber}>Box #{box.boxNumber}</Text>
                    <Text style={styles.boxStatus}>
                      {box.isComplete ? '✅ Complete' : '⚠️ Incomplete'}
                    </Text>
                  </View>
                  <Text style={styles.boxBarcode}>{box.barcode}</Text>
                  <View style={styles.boxDetails}>
                    <Text style={styles.boxDetailText}>{box.productCode}</Text>
                    <Text style={styles.boxDetailText}>
                      {box.scannedCount}/{box.expectedCount} units
                    </Text>
                  </View>
                </View>
              ))}
            </View>
          )}

          {/* Confirm Button */}
          {scannedBoxes.length > 0 && (
            <TouchableOpacity
              style={[
                styles.confirmButton,
                !validateAllBoxesComplete() && styles.confirmButtonDisabled,
              ]}
              onPress={() => {
                if (validateAllBoxesComplete()) {
                  handleConfirmReceipt();
                } else {
                  Alert.alert(
                    'Warning',
                    'Some boxes are incomplete. Continue anyway?',
                    [
                      { text: 'Cancel', onPress: () => {} },
                      { text: 'Continue', onPress: handleConfirmReceipt },
                    ]
                  );
                }
              }}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.confirmButtonText}>✓ Confirm Receipt</Text>
              )}
            </TouchableOpacity>
          )}
        </ScrollView>

        {/* Camera Modal */}
        {cameraVisible && cameraPermission && (
          <Modal transparent animationType="fade">
            <View style={styles.cameraModalContainer}>
              <BarCodeScanner
                onBarCodeScanned={handleBarCodeScanned}
                style={styles.barcodeScannerContainer}
              />
              <TouchableOpacity
                style={styles.closeCameraButton}
                onPress={() => setCameraVisible(false)}
              >
                <Text style={styles.closeCameraButtonText}>✕ Close</Text>
              </TouchableOpacity>
            </View>
          </Modal>
        )}

        {/* Loading Indicator */}
        {loading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color="#007AFF" />
          </View>
        )}
      </SafeAreaView>
    );
  };

  const renderConfirmMode = () => {
    const stats = calculateStats();

    return (
      <SafeAreaView style={styles.container}>
        <ScrollView style={styles.scrollView}>
          <Text style={styles.title}>✓ Confirm & Prepare Shipment</Text>

          {/* Summary */}
          <View style={styles.summaryCard}>
            <Text style={styles.summaryTitle}>Receipt Summary</Text>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Transfer ID:</Text>
              <Text style={styles.summaryValue}>
                {selectedTransfer?.transferId}
              </Text>
            </View>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Product:</Text>
              <Text style={styles.summaryValue}>
                {selectedTransfer?.productCode}
              </Text>
            </View>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Boxes Received:</Text>
              <Text style={styles.summaryValue}>{stats.totalBoxes}</Text>
            </View>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Total Units:</Text>
              <Text style={styles.summaryValue}>{stats.totalUnits}</Text>
            </View>
          </View>

          {/* Destination Input */}
          <View style={styles.destinationSection}>
            <Text style={styles.sectionLabel}>Shipping Destination</Text>
            <TextInput
              style={styles.destinationInput}
              placeholder="Enter destination (e.g., Jakarta, Surabaya)"
              value={shippingDestination}
              onChangeText={setShippingDestination}
              placeholderTextColor="#999"
            />
          </View>

          {/* Action Buttons */}
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={() => setConfirmationModal(true)}
            disabled={loading || !shippingDestination.trim()}
          >
            <Text style={styles.primaryButtonText}>
              🚚 Prepare Shipment
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => {
              resetScanSession();
              setCurrentMode('pending');
            }}
          >
            <Text style={styles.secondaryButtonText}>← Back to Transfers</Text>
          </TouchableOpacity>
        </ScrollView>

        {/* Confirmation Modal */}
        <Modal visible={confirmationModal} transparent animationType="fade">
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>Confirm Shipment Preparation?</Text>
              <Text style={styles.modalMessage}>
                Destination: {shippingDestination}
                {'\n'}Boxes: {stats.totalBoxes}
                {'\n'}Units: {stats.totalUnits}
              </Text>
              <View style={styles.modalButtons}>
                <TouchableOpacity
                  style={styles.modalButtonCancel}
                  onPress={() => setConfirmationModal(false)}
                >
                  <Text style={styles.modalButtonText}>Cancel</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={styles.modalButtonConfirm}
                  onPress={handlePrepareShipment}
                  disabled={loading}
                >
                  {loading ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <Text style={styles.modalButtonText}>Confirm</Text>
                  )}
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>

        {/* Loading Indicator */}
        {loading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color="#007AFF" />
          </View>
        )}
      </SafeAreaView>
    );
  };

  // ==================== MAIN RENDER ====================

  if (loading && pendingTransfers.length === 0) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading transfers...</Text>
      </View>
    );
  }

  if (currentMode === 'pending') {
    return renderPendingTransfers();
  }

  if (currentMode === 'scan' && selectedTransfer) {
    return renderScanMode();
  }

  if (currentMode === 'confirm' && selectedTransfer) {
    return renderConfirmMode();
  }

  return (
    <View style={styles.centerContainer}>
      <Text style={styles.errorText}>Invalid state</Text>
    </View>
  );
};

// ==================== STYLES ====================

const styles = StyleSheet.create({
  // Container styles
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    padding: 16,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },

  // Typography
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333',
  },
  scanTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  sectionLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    color: '#333',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 18,
    color: '#d32f2f',
  },

  // Empty state
  emptyState: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 18,
    color: '#999',
  },

  // Transfer cards
  transferCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#e0e0e0',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  transferCardSelected: {
    borderColor: '#007AFF',
    backgroundColor: '#f0f8ff',
  },
  transferCardContent: {
    gap: 8,
  },
  transferCardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  transferCardSubtitle: {
    fontSize: 14,
    color: '#666',
  },
  transferCardDetails: {
    marginTop: 8,
    gap: 6,
  },
  detailText: {
    fontSize: 13,
    color: '#555',
  },
  statusBadge: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#fff',
    backgroundColor: '#4CAF50',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    alignSelf: 'flex-start',
    overflow: 'hidden',
  },

  // Scan header
  scanHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    gap: 12,
  },
  backButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
  },
  backButtonText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '600',
  },

  // Transfer info
  transferInfo: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  transferInfoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  transferInfoSubtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  transferInfoDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 8,
  },
  infoBadge: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    padding: 10,
    alignItems: 'center',
  },
  infoBadgeLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  infoBadgeValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },

  // Camera button
  cameraButton: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
  cameraButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },

  // Camera modal
  cameraModalContainer: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'flex-end',
  },
  barcodeScannerContainer: {
    flex: 1,
  },
  closeCameraButton: {
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    paddingVertical: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeCameraButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },

  // Manual entry
  manualEntrySection: {
    marginBottom: 20,
  },
  manualEntryGroup: {
    flexDirection: 'row',
    gap: 8,
  },
  manualBarcodeInput: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: '#ddd',
    fontSize: 14,
  },
  manualEntryButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingHorizontal: 16,
    justifyContent: 'center',
  },
  manualEntryButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
  },

  // Statistics
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 20,
  },
  statCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 12,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 6,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
  },

  // Scanned boxes
  scannedBoxesSection: {
    marginBottom: 20,
  },
  boxItem: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderLeftWidth: 4,
  },
  boxItemComplete: {
    borderLeftColor: '#4CAF50',
    backgroundColor: '#f1f8f4',
  },
  boxItemIncomplete: {
    borderLeftColor: '#FF9800',
    backgroundColor: '#fff8f1',
  },
  boxItemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  boxNumber: {
    fontWeight: 'bold',
    fontSize: 14,
    color: '#333',
  },
  boxStatus: {
    fontSize: 12,
    fontWeight: '600',
  },
  boxBarcode: {
    fontSize: 12,
    color: '#666',
    marginBottom: 6,
    fontFamily: 'monospace',
  },
  boxDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  boxDetailText: {
    fontSize: 12,
    color: '#555',
  },

  // Buttons
  confirmButton: {
    backgroundColor: '#4CAF50',
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 16,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    marginBottom: 20,
  },
  confirmButtonDisabled: {
    opacity: 0.5,
  },
  confirmButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  primaryButton: {
    backgroundColor: '#4CAF50',
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 16,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    marginBottom: 12,
  },
  primaryButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  secondaryButton: {
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 16,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ddd',
    marginBottom: 20,
  },
  secondaryButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#007AFF',
  },

  // Summary
  summaryCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#333',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  summaryLabel: {
    fontSize: 14,
    color: '#666',
  },
  summaryValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },

  // Destination
  destinationSection: {
    marginBottom: 20,
  },
  destinationInput: {
    backgroundColor: '#fff',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: '#ddd',
    fontSize: 14,
  },

  // Modal
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    width: '100%',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#333',
  },
  modalMessage: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
    lineHeight: 20,
  },
  modalButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  modalButtonCancel: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    paddingVertical: 12,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  modalButtonConfirm: {
    flex: 1,
    backgroundColor: '#4CAF50',
    borderRadius: 8,
    paddingVertical: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },

  // Loading
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default FinishGoodScreen;
