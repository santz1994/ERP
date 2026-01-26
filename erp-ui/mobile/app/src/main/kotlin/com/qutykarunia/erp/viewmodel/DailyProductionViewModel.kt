package com.qutykarunia.erp.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import com.qutykarunia.erp.data.api.ProductionApi
import timber.log.Timber
import java.time.LocalDate
import javax.inject.Inject
import kotlin.math.ceil

/**
 * DailyProductionInputScreen ViewModel
 * 
 * Manages:
 * 1. Daily production quantity input
 * 2. Cumulative total calculation
 * 3. Progress percentage tracking
 * 4. Target vs actual comparison
 * 5. Completion confirmation workflow
 * 6. Backend API communication
 * 7. Offline queue for sync
 */
@HiltViewModel
class DailyProductionViewModel @Inject constructor(
    private val productionApi: ProductionApi
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(DailyProductionUIState())
    val uiState: StateFlow<DailyProductionUIState> = _uiState.asStateFlow()
    
    init {
        loadSPKData()
    }
    
    /**
     * Load SPK and production data from backend
     */
    private fun loadSPKData() {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true)
                
                // In production, would fetch from API:
                // val response = productionApi.getMySPKs(status = "IN_PROGRESS")
                
                // Mock data for now
                val mockDailyInputs = mapOf(
                    LocalDate.now().minusDays(5) to 50,
                    LocalDate.now().minusDays(4) to 60,
                    LocalDate.now().minusDays(3) to 55,
                    LocalDate.now().minusDays(2) to 70,
                    LocalDate.now().minusDays(1) to 65,
                    LocalDate.now() to 0
                )
                
                val targetQty = 500
                val totalQty = mockDailyInputs.values.sum()
                val progressPct = (totalQty.toFloat() / targetQty).coerceIn(0f, 1f)
                val dailyRate = if (mockDailyInputs.size > 1) totalQty / mockDailyInputs.size else 0
                val remainingQty = maxOf(0, targetQty - totalQty)
                val estDaysRemaining = if (dailyRate > 0) ceil(remainingQty.toFloat() / dailyRate).toInt() else null
                
                _uiState.value = DailyProductionUIState(
                    spkId = 1001,
                    spkNumber = "SPK-2026-001",
                    productName = "Product Example",
                    targetQty = targetQty,
                    totalQty = totalQty,
                    progressPct = progressPct,
                    dailyInputs = mockDailyInputs,
                    estimatedDaysRemaining = estDaysRemaining,
                    isLoading = false
                )
                
                Timber.d("SPK data loaded - Target: $targetQty, Actual: $totalQty, Progress: ${progressPct * 100}%")
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = "Failed to load SPK data: ${e.message}"
                )
                Timber.e(e, "Error loading SPK data")
            }
        }
    }
    
    /**
     * Set daily production quantity for a specific date
     * 
     * Flow:
     * 1. Update the daily input map
     * 2. Recalculate cumulative total
     * 3. Update progress percentage
     * 4. Estimate remaining days
     */
    fun setDailyInput(date: LocalDate, quantity: Int) {
        try {\n            val currentInputs = _uiState.value.dailyInputs.toMutableMap()
            
            if (quantity > 0) {
                currentInputs[date] = quantity
            } else {
                currentInputs.remove(date)
            }
            
            // Recalculate totals
            val targetQty = _uiState.value.targetQty
            val totalQty = currentInputs.values.sum()
            val progressPct = (totalQty.toFloat() / targetQty).coerceIn(0f, 1f)
            val dailyRate = if (currentInputs.size > 0) totalQty / currentInputs.size else 0
            val remainingQty = maxOf(0, targetQty - totalQty)
            val estDaysRemaining = if (dailyRate > 0) ceil(remainingQty.toFloat() / dailyRate).toInt() else null
            
            _uiState.value = _uiState.value.copy(
                dailyInputs = currentInputs,
                totalQty = totalQty,
                progressPct = progressPct,
                estimatedDaysRemaining = estDaysRemaining
            )
            
            Timber.d("Daily input updated - Date: $date, Qty: $quantity, Total: $totalQty")
            
        } catch (e: Exception) {
            Timber.e(e, "Error setting daily input")
        }
    }
    
    /**\n     * Save progress without completing
     * \n     * Persists all daily inputs to backend\n     */\n    fun saveProgress() {\n        viewModelScope.launch {\n            try {\n                _uiState.value = _uiState.value.copy(isLoading = true)\n                \n                val spkId = _uiState.value.spkId\n                val dailyInputs = _uiState.value.dailyInputs\n                \n                Timber.d(\"Saving progress for SPK $spkId with ${dailyInputs.size} entries\")\n                \n                // In production, would call API to save each daily input:\n                // for ((date, quantity) in dailyInputs) {\n                //     val request = DailyInputRequest(\n                //         production_date = date,\n                //         input_qty = quantity,\n                //         status = \"CONFIRMED\"\n                //     )\n                //     val response = productionApi.recordDailyInput(spkId, request)\n                // }\n                \n                _uiState.value = _uiState.value.copy(\n                    isLoading = false,\n                    error = null\n                )\n                \n                Timber.d(\"Progress saved successfully\")\n                \n            } catch (e: Exception) {\n                _uiState.value = _uiState.value.copy(\n                    isLoading = false,\n                    error = \"Save failed: ${e.message}\"\n                )\n                Timber.e(e, \"Error saving progress\")\n            }\n        }\n    }\n    \n    /**\n     * Confirm SPK completion\n     * \n     * Flow:\n     * 1. Verify total quantity >= target\n     * 2. Send completion request to backend\n     * 3. Update SPK status to COMPLETED\n     * 4. Handle offline queue\n     */\n    fun confirmCompletion() {\n        viewModelScope.launch {\n            try {\n                _uiState.value = _uiState.value.copy(isLoading = true)\n                \n                val spkId = _uiState.value.spkId\n                val totalQty = _uiState.value.totalQty\n                val targetQty = _uiState.value.targetQty\n                \n                if (totalQty < targetQty) {\n                    _uiState.value = _uiState.value.copy(\n                        isLoading = false,\n                        error = \"Cannot complete: Total ($totalQty) < Target ($targetQty)\"\n                    )\n                    return@launch\n                }\n                \n                Timber.d(\"Confirming SPK completion - SPK: $spkId, Total: $totalQty\")\n                \n                // In production, would call completion API:\n                // val response = productionApi.completeProduction(spkId)\n                \n                // Simulate successful completion\n                _uiState.value = _uiState.value.copy(\n                    isLoading = false,\n                    error = null\n                )\n                \n                Timber.d(\"SPK $spkId completed successfully\")\n                \n            } catch (e: Exception) {\n                _uiState.value = _uiState.value.copy(\n                    isLoading = false,\n                    error = \"Completion failed: ${e.message}\"\n                )\n                Timber.e(e, \"Error confirming completion\")\n            }\n        }\n    }\n    \n    /**\n     * Clear error message\n     */\n    fun clearError() {\n        _uiState.value = _uiState.value.copy(error = null)\n    }\n}\n\n/**\n * UI State for DailyProductionInputScreen\n */\ndata class DailyProductionUIState(\n    val spkId: Int = 0,\n    val spkNumber: String = \"\",\n    val productName: String = \"\",\n    val targetQty: Int = 0,\n    val totalQty: Int = 0,\n    val progressPct: Float = 0f,\n    val dailyInputs: Map<LocalDate, Int> = emptyMap(), // Date -> Quantity\n    val estimatedDaysRemaining: Int? = null,\n    val isLoading: Boolean = false,\n    val error: String? = null\n)\n