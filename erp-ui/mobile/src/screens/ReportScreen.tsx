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

interface DailyReport {
  date: string;
  totalProduced: number;
  totalTarget: number;
  efficiency: number;
  defectRate: number;
  qualityGrade: string;
  byLine: Array<{
    name: string;
    produced: number;
    target: number;
    efficiency: number;
  }>;
}

export const ReportScreen: React.FC = () => {
  const [report, setReport] = useState<DailyReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadReport();
  }, []);

  const loadReport = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getDailyReport();
      setReport(data);
    } catch (error) {
      console.error('Error loading report:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadReport();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  if (!report) {
    return (
      <View style={styles.centerContainer}>
        <Text>Failed to load report</Text>
      </View>
    );
  }

  const getQualityColor = (grade: string) => {
    switch (grade) {
      case 'A':
        return '#4CAF50';
      case 'B':
        return '#FFC107';
      case 'C':
        return '#f44336';
      default:
        return '#999';
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Daily Report</Text>
        <Text style={styles.headerDate}>{report.date}</Text>
      </View>

      {/* Summary Cards */}
      <View style={styles.summaryContainer}>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryLabel}>Total Produced</Text>
          <Text style={styles.summaryValue}>{report.totalProduced}</Text>
          <Text style={styles.summarySubtext}>Target: {report.totalTarget}</Text>
        </View>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryLabel}>Efficiency</Text>
          <Text style={styles.summaryValue}>{report.efficiency.toFixed(1)}%</Text>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                { width: `${Math.min(report.efficiency, 100)}%` },
              ]}
            />
          </View>
        </View>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryLabel}>Quality Grade</Text>
          <View
            style={[
              styles.gradeBadge,
              { backgroundColor: getQualityColor(report.qualityGrade) },
            ]}
          >
            <Text style={styles.gradeText}>{report.qualityGrade}</Text>
          </View>
          <Text style={styles.summarySubtext}>Defect: {report.defectRate.toFixed(2)}%</Text>
        </View>
      </View>

      {/* Detailed Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Detailed Metrics</Text>
        <View style={styles.metricsCard}>
          <View style={styles.metricRow}>
            <Text style={styles.metricLabel}>Production Target</Text>
            <Text style={styles.metricValue}>{report.totalTarget} units</Text>
          </View>
          <View style={styles.metricRow}>
            <Text style={styles.metricLabel}>Actual Production</Text>
            <Text style={styles.metricValue}>{report.totalProduced} units</Text>
          </View>
          <View style={styles.metricRow}>
            <Text style={styles.metricLabel}>Achievement Rate</Text>
            <Text style={styles.metricValue}>
              {((report.totalProduced / report.totalTarget) * 100).toFixed(1)}%
            </Text>
          </View>
          <View style={styles.metricRow}>
            <Text style={styles.metricLabel}>Line Efficiency</Text>
            <Text style={styles.metricValue}>{report.efficiency.toFixed(1)}%</Text>
          </View>
          <View style={styles.metricRow}>
            <Text style={styles.metricLabel}>Defect Rate</Text>
            <Text style={[styles.metricValue, { color: '#f44336' }]}>
              {report.defectRate.toFixed(2)}%
            </Text>
          </View>
        </View>
      </View>

      {/* By Line Breakdown */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Production by Line</Text>
        {report.byLine.map((line, index) => (
          <View key={index} style={styles.lineCard}>
            <View style={styles.lineHeader}>
              <Text style={styles.lineName}>{line.name}</Text>
              <Text style={styles.lineEfficiency}>{line.efficiency.toFixed(1)}%</Text>
            </View>
            <View style={styles.lineProgress}>
              <View style={styles.progressBar}>
                <View
                  style={[
                    styles.progressFill,
                    { width: `${Math.min(line.efficiency, 100)}%` },
                  ]}
                />
              </View>
            </View>
            <View style={styles.lineStats}>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>Produced</Text>
                <Text style={styles.statValue}>{line.produced}</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>Target</Text>
                <Text style={styles.statValue}>{line.target}</Text>
              </View>
            </View>
          </View>
        ))}
      </View>

      {/* Footer Spacer */}
      <View style={{ height: 20 }} />
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
  headerDate: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 5,
  },
  summaryContainer: {
    flexDirection: 'row',
    padding: 10,
    justifyContent: 'space-between',
  },
  summaryCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    marginHorizontal: 5,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  summaryLabel: {
    fontSize: 11,
    color: '#666',
    marginBottom: 5,
    textAlign: 'center',
  },
  summaryValue: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  summarySubtext: {
    fontSize: 10,
    color: '#999',
    textAlign: 'center',
  },
  progressBar: {
    width: '100%',
    height: 4,
    backgroundColor: '#eee',
    borderRadius: 2,
    marginTop: 5,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
  },
  gradeBadge: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 5,
  },
  gradeText: {
    fontSize: 18,
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
  metricsCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  metricLabel: {
    fontSize: 14,
    color: '#666',
  },
  metricValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
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
  lineHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  lineName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  lineEfficiency: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  lineProgress: {
    marginBottom: 10,
  },
  lineStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 3,
  },
  statValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
});
