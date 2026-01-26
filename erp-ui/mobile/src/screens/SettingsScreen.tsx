import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import { useAuth } from '../context/AuthContext';

export const SettingsScreen: React.FC = () => {
  const { user, logout } = useAuth();
  const [language, setLanguage] = useState('en');
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  const handleLogout = async () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', onPress: () => {} },
        {
          text: 'Logout',
          onPress: async () => {
            try {
              await logout();
            } catch (error) {
              Alert.alert('Error', 'Failed to logout');
            }
          },
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Settings</Text>
      </View>

      {/* User Profile Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Profile</Text>
        <View style={styles.profileCard}>
          <View style={styles.profileHeader}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>{user?.username?.[0]?.toUpperCase()}</Text>
            </View>
            <View style={styles.userInfo}>
              <Text style={styles.userName}>{user?.username}</Text>
              <Text style={styles.userRole}>{user?.role || 'Operator'}</Text>
              <Text style={styles.userDepartment}>{user?.department || 'Production'}</Text>
            </View>
          </View>
        </View>
      </View>

      {/* Preferences Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Preferences</Text>

        <View style={styles.preferenceCard}>
          <View style={styles.preferenceRow}>
            <View>
              <Text style={styles.preferenceName}>Language</Text>
              <Text style={styles.preferenceDescription}>App language</Text>
            </View>
            <View style={styles.languageSelector}>
              <TouchableOpacity
                style={[styles.languageButton, language === 'en' && styles.activeLanguage]}
                onPress={() => setLanguage('en')}
              >
                <Text
                  style={[
                    styles.languageButtonText,
                    language === 'en' && styles.activeLanguageText,
                  ]}
                >
                  EN
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.languageButton, language === 'id' && styles.activeLanguage]}
                onPress={() => setLanguage('id')}
              >
                <Text
                  style={[
                    styles.languageButtonText,
                    language === 'id' && styles.activeLanguageText,
                  ]}
                >
                  ID
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.divider} />

          <View style={styles.preferenceRow}>
            <View>
              <Text style={styles.preferenceName}>Notifications</Text>
              <Text style={styles.preferenceDescription}>Receive production alerts</Text>
            </View>
            <Switch
              value={notifications}
              onValueChange={setNotifications}
              trackColor={{ false: '#ccc', true: '#81C784' }}
              thumbColor={notifications ? '#4CAF50' : '#999'}
            />
          </View>

          <View style={styles.divider} />

          <View style={styles.preferenceRow}>
            <View>
              <Text style={styles.preferenceName}>Dark Mode</Text>
              <Text style={styles.preferenceDescription}>Easier on the eyes</Text>
            </View>
            <Switch
              value={darkMode}
              onValueChange={setDarkMode}
              trackColor={{ false: '#ccc', true: '#81C784' }}
              thumbColor={darkMode ? '#4CAF50' : '#999'}
            />
          </View>
        </View>
      </View>

      {/* Application Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Application</Text>

        <View style={styles.appCard}>
          <View style={styles.appRow}>
            <Text style={styles.appLabel}>Version</Text>
            <Text style={styles.appValue}>1.0.0</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.appRow}>
            <Text style={styles.appLabel}>Build</Text>
            <Text style={styles.appValue}>20260126</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.appRow}>
            <Text style={styles.appLabel}>API Server</Text>
            <Text style={styles.appValue}>Connected</Text>
          </View>
        </View>
      </View>

      {/* About Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>

        <View style={styles.aboutCard}>
          <Text style={styles.aboutText}>
            ERP Production Control System{'\n'}
            Version 1.0.0{'\n'}
            {'\n'}
            © 2026 All rights reserved.
          </Text>
        </View>
      </View>

      {/* Logout Button */}
      <View style={styles.section}>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>LOGOUT</Text>
        </TouchableOpacity>
      </View>

      <View style={{ height: 20 }} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
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
  profileCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#2196F3',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  avatarText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  userRole: {
    fontSize: 14,
    color: '#666',
    marginTop: 3,
  },
  userDepartment: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  preferenceCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  preferenceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 15,
  },
  preferenceName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#333',
  },
  preferenceDescription: {
    fontSize: 12,
    color: '#999',
    marginTop: 3,
  },
  languageSelector: {
    flexDirection: 'row',
    gap: 5,
  },
  languageButton: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 4,
    backgroundColor: '#f0f0f0',
  },
  activeLanguage: {
    backgroundColor: '#2196F3',
  },
  languageButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
  },
  activeLanguageText: {
    color: '#fff',
  },
  divider: {
    height: 1,
    backgroundColor: '#eee',
  },
  appCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  appRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 12,
  },
  appLabel: {
    fontSize: 14,
    color: '#666',
  },
  appValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  aboutCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  aboutText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
    textAlign: 'center',
  },
  logoutButton: {
    backgroundColor: '#f44336',
    borderRadius: 8,
    paddingVertical: 15,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
