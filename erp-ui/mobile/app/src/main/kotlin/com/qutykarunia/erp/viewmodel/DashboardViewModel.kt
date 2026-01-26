package com.qutykarunia.erp.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import android.content.Context
import dagger.hilt.android.qualifiers.ApplicationContext
import com.qutykarunia.erp.data.api.ProductionApi
import com.qutykarunia.erp.data.api.TokenManager
import com.qutykarunia.erp.data.models.SPKData
import timber.log.Timber
import javax.inject.Inject

/**
 * DashboardScreen ViewModel
 * 
 * Manages:
 * 1. Loading SPKs assigned to user
 * 2. Production summary statistics
 * 3. On-track vs at-risk tracking
 * 4. User session management
 * 5. Logout functionality
 */
@HiltViewModel
class DashboardViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val productionApi: ProductionApi
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(DashboardUIState())
    val uiState: StateFlow<DashboardUIState> = _uiState.asStateFlow()
    
    init {
        loadDashboardData()
    }
    
    /**
     * Load production data for dashboard
     * 
     * Flow:
     * 1. Fetch user's assigned SPKs
     * 2. Calculate summary statistics
     * 3. Determine on-track vs at-risk
     * 4. Update UI state
     */
    private fun loadDashboardData() {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true)
                
                Timber.d("Loading dashboard data")
                
                // In production, would call:
                // val response = productionApi.getMySPKs()
                
                // Mock data for now
                val mockSPKs = listOf(
                    SPKData(
                        id = 1001,
                        spk_number = "SPK-2026-001",
                        product_name = "Product A",
                        product_id = 1,
                        target_quantity = 500,
                        actual_quantity = 350,
                        status = "IN_PROGRESS",
                        created_date = java.time.LocalDate.now(),
                        completion_pct = 0.7f,
                        assigned_to = "User01"
                    ),
                    SPKData(
                        id = 1002,
                        spk_number = "SPK-2026-002",
                        product_name = "Product B",
                        product_id = 2,
                        target_quantity = 300,
                        actual_quantity = 300,
                        status = "COMPLETED",
                        created_date = java.time.LocalDate.now(),
                        completion_pct = 1.0f,
                        assigned_to = "User01"
                    ),
                    SPKData(
                        id = 1003,
                        spk_number = "SPK-2026-003",
                        product_name = "Product C",
                        product_id = 3,
                        target_quantity = 200,
                        actual_quantity = 80,
                        status = "IN_PROGRESS",
                        created_date = java.time.LocalDate.now(),
                        completion_pct = 0.4f,
                        assigned_to = "User01"
                    )
                )
                
                // Calculate statistics
                val totalSPKs = mockSPKs.size
                val inProgress = mockSPKs.count { it.status == "IN_PROGRESS" }
                val completed = mockSPKs.count { it.status == "COMPLETED" }
                
                // Determine on-track vs at-risk
                // On-track: completion % >= days passed
                val onTrack = mockSPKs.count { it.completion_pct >= 0.5f }
                val atRisk = mockSPKs.count { it.completion_pct < 0.5f }
                
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    totalSPKs = totalSPKs,
                    inProgress = inProgress,
                    completed = completed,
                    onTrack = onTrack,
                    atRisk = atRisk,
                    spks = mockSPKs,
                    userName = "Operator 01",
                    error = null
                )
                
                Timber.d("Dashboard loaded - Total: $totalSPKs, In Progress: $inProgress, Completed: $completed")
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = "Failed to load dashboard: ${e.message}"
                )
                Timber.e(e, "Dashboard loading error")
            }
        }
    }
    
    /**
     * Refresh dashboard data
     */
    fun refreshDashboard() {
        loadDashboardData()
    }
    
    /**
     * Logout user
     * 
     * Flow:
     * 1. Clear JWT tokens
     * 2. Clear cached data
     * 3. Mark logout successful
     * 4. Navigate to login screen
     */
    fun logout() {
        viewModelScope.launch {
            try {
                Timber.d("Logging out user")
                
                // Clear tokens
                TokenManager.clearTokens(context)
                
                // Clear cached data
                _uiState.value = DashboardUIState(logoutSuccess = true)
                
                Timber.d("User logged out successfully")
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    error = "Logout failed: ${e.message}"
                )
                Timber.e(e, "Logout error")
            }
        }
    }
    
    /**
     * Clear error message
     */
    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}

/**
 * UI State for DashboardScreen
 */
data class DashboardUIState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val logoutSuccess: Boolean = false,
    val totalSPKs: Int = 0,
    val inProgress: Int = 0,
    val completed: Int = 0,
    val onTrack: Int = 0,
    val atRisk: Int = 0,
    val spks: List<SPKData> = emptyList(),
    val userName: String = "Operator",
    val userRole: String = "Production Staff"
)
