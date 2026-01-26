import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  TextInput,
} from 'react-native';
import { apiClient } from '../api/client';

interface LineStatus {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'idle';
  currentQuantity: number;
  targetQuantity: number;
  timeElapsed: number;
  operator: string;
}

export const OperatorScreen: React.FC = () => {
  const [selectedLine, setSelectedLine] = useState<LineStatus | null>(null);
  const [lines, setLines] = useState<LineStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [operatingLoading, setOperatingLoading] = useState(false);
  const [quantity, setQuantity] = useState('0');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    loadLines();
    const interval = setInterval(loadLines, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadLines = async () => {
    try {
      const [cuttingLines, sewingLines, finishingLines] = await Promise.all([
        apiClient.getCuttingLines(),
        apiClient.getSewingLines(),
        apiClient.getFinishingLines(),
      ]);
      setLines([...cuttingLines, ...sewingLines, ...finishingLines]);
    } catch (error) {
      console.error('Error loading lines:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartLine = async () => {
    if (!selectedLine) return;

    setOperatingLoading(true);
    try {
      const module = selectedLine.id.split('-')[0].toLowerCase();
      if (module === 'cutting') {
        await apiClient.startCuttingLine(selectedLine.id);
      } else if (module === 'sewing') {
        await apiClient.startSewingLine(selectedLine.id);
      } else if (module === 'finishing') {
        await apiClient.startFinishingLine(selectedLine.id);
      }
      Alert.alert('Success', `Line ${selectedLine.name} started`);
      await loadLines();
    } catch (error: any) {
      Alert.alert('Error', error.message);
    } finally {
      setOperatingLoading(false);
    }
  };

  const handleStopLine = async () => {
    if (!selectedLine) return;

    setOperatingLoading(true);
    try {
      const module = selectedLine.id.split('-')[0].toLowerCase();
      if (module === 'cutting') {
        await apiClient.stopCuttingLine(selectedLine.id);
      } else if (module === 'sewing') {
        await apiClient.stopSewingLine(selectedLine.id);
      } else if (module === 'finishing') {
        await apiClient.stopFinishingLine(selectedLine.id);
      }
      Alert.alert('Success', `Line ${selectedLine.name} stopped`);
      await loadLines();
    } catch (error: any) {
      Alert.alert('Error', error.message);
    } finally {
      setOperatingLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return '#4CAF50';
      case 'stopped':
        return '#f44336';
      case 'idle':
        return '#FFC107';
      default:
        return '#999';
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Operator Control</Text>
      </View>

      {/* Line Selection */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Select Production Line</Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.linesList}
        >
          {lines.map((line) => (
            <TouchableOpacity
              key={line.id}
              style={[
                styles.lineButton,
                selectedLine?.id === line.id && styles.lineButtonActive,
              ]}
              onPress={() => setSelectedLine(line)}
            >
              <View
                style={[
                  styles.statusIndicator,
                  { backgroundColor: getStatusColor(line.status) },
                ]}
              />
              <Text style={styles.lineButtonText}>{line.name}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Selected Line Details */}
      {selectedLine && (
        <>
          <View style={styles.section}>
            <View style={styles.detailCard}>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Line Name</Text>
                <Text style={styles.detailValue}>{selectedLine.name}</Text>
              </View>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Status</Text>
                <View style={styles.statusBadge}>
                  <View
                    style={[
                      styles.statusDot,
                      { backgroundColor: getStatusColor(selectedLine.status) },
                    ]}
                  />
                  <Text style={styles.statusText}>{selectedLine.status.toUpperCase()}</Text>
                </View>
              </View>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Operator</Text>
                <Text style={styles.detailValue}>{selectedLine.operator}</Text>
              </View>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Current Quantity</Text>
                <Text style={styles.detailValue}>{selectedLine.currentQuantity}</Text>
              </View>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Target Quantity</Text>
                <Text style={styles.detailValue}>{selectedLine.targetQuantity}</Text>
              </View>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Progress</Text>
                <Text style={styles.detailValue}>
                  {(
                    (selectedLine.currentQuantity / selectedLine.targetQuantity) *
                    100
                  ).toFixed(1)}%
                </Text>
              </View>
            </View>
          </View>

          {/* Quantity & Notes */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Update Production</Text>
            <TextInput
              style={styles.input}
              placeholder="Quantity Produced"
              placeholderTextColor="#999"
              value={quantity}
              onChangeText={setQuantity}
              keyboardType="number-pad"
            />
            <TextInput
              style={[styles.input, styles.notesInput]}
              placeholder="Add notes (optional)"
              placeholderTextColor="#999"
              value={notes}
              onChangeText={setNotes}
              multiline
            />
          </View>

          {/* Control Buttons */}
          <View style={styles.section}>
            <TouchableOpacity
              style={[
                styles.controlButton,
                styles.startButton,
                operatingLoading && styles.buttonDisabled,
              ]}
              onPress={handleStartLine}
              disabled={operatingLoading || selectedLine.status === 'running'}
            >
              {operatingLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.controlButtonText}>START</Text>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.controlButton,
                styles.stopButton,
                operatingLoading && styles.buttonDisabled,
              ]}
              onPress={handleStopLine}
              disabled={operatingLoading || selectedLine.status === 'stopped'}
            >
              {operatingLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.controlButtonText}>STOP</Text>
              )}
            </TouchableOpacity>
          </View>
        </>
      )}

      {!selectedLine && (
        <View style={styles.emptyState}>
          <Text style={styles.emptyStateText}>Select a production line to begin</Text>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    backgroundColor: '#2196F3',
    padding: 20,
    paddingTop: 30,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  section: {
    padding: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  linesList: {
    marginBottom: 10,
  },
  lineButton: {
    backgroundColor: '#fff',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 15,
    marginRight: 10,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  lineButtonActive: {
    borderColor: '#2196F3',
    backgroundColor: '#E3F2FD',
  },
  statusIndicator: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 8,
  },
  lineButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  detailCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  detailLabel: {
    fontSize: 14,
    color: '#666',
  },
  detailValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
  },
  input: {
    backgroundColor: '#fff',
    borderColor: '#ddd',
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    fontSize: 14,
  },
  notesInput: {
    height: 100,
    textAlignVertical: 'top',
  },
  controlButton: {
    height: 50,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  startButton: {
    backgroundColor: '#4CAF50',
  },
  stopButton: {
    backgroundColor: '#f44336',
  },
  controlButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 50,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#999',
  },
});
