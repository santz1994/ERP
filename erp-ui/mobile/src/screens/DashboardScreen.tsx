import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { apiClient } from '../api/client';

interface DashboardStats {
  totalProduction: number;
  completedToday: number;
  inProgress: number;
  quality: {
    passRate: number;
    defectRate: number;
  };
  lines: {
    cutting: { running: number; idle: number; stopped: number };
    sewing: { running: number; idle: number; stopped: number };
    finishing: { running: number; idle: number; stopped: number };
  };
}

export const DashboardScreen: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadStats();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  if (!stats) {
    return (
      <View style={styles.centerContainer}>
        <Text>Failed to load dashboard</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Production Dashboard</Text>
      </View>

      {/* Key Metrics */}
      <View style={styles.metricsContainer}>
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>Total Production</Text>
          <Text style={styles.metricValue}>{stats.totalProduction}</Text>
          <Text style={styles.metricUnit}>units</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>Completed Today</Text>
          <Text style={styles.metricValue}>{stats.completedToday}</Text>
          <Text style={styles.metricUnit}>units</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>In Progress</Text>
          <Text style={styles.metricValue}>{stats.inProgress}</Text>
          <Text style={styles.metricUnit}>units</Text>
        </View>
      </View>

      {/* Quality Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quality Metrics</Text>
        <View style={styles.qualityCard}>
          <View style={styles.qualityRow}>
            <Text style={styles.qualityLabel}>Pass Rate</Text>
            <Text style={[styles.qualityValue, { color: '#4CAF50' }]}>
              {stats.quality.passRate.toFixed(1)}%
            </Text>
          </View>
          <View style={styles.qualityRow}>
            <Text style={styles.qualityLabel}>Defect Rate</Text>
            <Text style={[styles.qualityValue, { color: '#f44336' }]}>
              {stats.quality.defectRate.toFixed(1)}%
            </Text>
          </View>
        </View>
      </View>

      {/* Line Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Production Lines</Text>

        <View style={styles.lineCard}>
          <Text style={styles.lineTitle}>Cutting</Text>
          <View style={styles.lineStatus}>
            <View style={styles.statusItem}>
              <View style={[styles.statusDot, { backgroundColor: '#4CAF50' }]} />
              <Text style={styles.statusLabel}>Running: {stats.lines.cutting.running}</Text>
            </View>
            <View style={styles.statusItem}>
              <View style={[styles.statusDot, { backgroundColor: '#FFC107' }]} />
              <Text style={styles.statusLabel}>Idle: {stats.lines.cutting.idle}</Text>
            </View>
            <View style={styles.statusItem}>
              <View style={[styles.statusDot, { backgroundColor: '#f44336' }]} />
              <Text style={styles.statusLabel}>Stopped: {stats.lines.cutting.stopped}</Text>
            </View>
          </View>
        </View>

        <View style={styles.lineCard}>
          <Text style={styles.lineTitle}>Sewing</Text>
          <View style={styles.lineStatus}>
            <View style={styles.statusItem}>
              <View style={[styles.statusDot, { backgroundColor: '#4CAF50' }]} />
              <Text style={styles.statusLabel}>Running: {stats.lines.sewing.running}</Text>
            </View>
            <View style={styles.statusItem}>
              <View style={[styles.statusDot, { backgroundColor: '#FFC107' }]} />
              <Text style={styles.statusLabel}>Idle: {stats.lines.sewing.idle}</Text>
            </View>
            <View style={styles.statusItem}>
              <View style={[styles.statusDot, { backgroundColor: '#f44336' }]} />
              <Text style={styles.statusLabel}>Stopped: {stats.lines.sewing.stopped}</Text>
            </View>
          </View>
        </View>

        <View style={styles.lineCard}>
          <Text style={styles.lineTitle}>Finishing</Text>
          <View style={styles.lineStatus}>
            <View style={styles.statusItem}>
              <View style={[styles.statusDot, { backgroundColor: '#4CAF50' }]} />
              <Text style={styles.statusLabel}>Running: {stats.lines.finishing.running}</Text>
            </View>
            <View style={styles.statusItem}>
              <View style={[styles.statusDot, { backgroundColor: '#FFC107' }]} />
              <Text style={styles.statusLabel}>Idle: {stats.lines.finishing.idle}</Text>
            </View>
            <View style={styles.statusItem}>
              <View style={[styles.statusDot, { backgroundColor: '#f44336' }]} />
              <Text style={styles.statusLabel}>Stopped: {stats.lines.finishing.stopped}</Text>
            </View>
          </View>
        </View>
      </View>
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
  metricsContainer: {
    flexDirection: 'row',
    padding: 10,
    justifyContent: 'space-between',
  },
  metricCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginHorizontal: 5,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  metricUnit: {
    fontSize: 11,
    color: '#999',
    marginTop: 3,
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
  qualityCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  qualityRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  qualityLabel: {
    fontSize: 14,
    color: '#666',
  },
  qualityValue: {
    fontSize: 18,
    fontWeight: '600',
  },
  lineCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  lineTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  lineStatus: {
    gap: 8,
  },
  statusItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 8,
  },
  statusLabel: {
    fontSize: 14,
    color: '#666',
  },
});
