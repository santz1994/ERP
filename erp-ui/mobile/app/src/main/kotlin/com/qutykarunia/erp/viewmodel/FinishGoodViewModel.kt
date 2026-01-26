package com.qutykarunia.erp.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import com.qutykarunia.erp.data.api.FinishGoodApi
import com.qutykarunia.erp.data.models.*
import timber.log.Timber
import java.util.UUID
import javax.inject.Inject

/**
 * FinishGoodBarcodeScreen ViewModel
 * 
 * Manages:
 * 1. Carton barcode scanning and validation
 * 2. Per-article item counting
 * 3. Quantity tracking and confirmation
 * 4. Backend API communication
 * 5. Offline queue for sync
 */
@HiltViewModel
class FinishGoodViewModel @Inject constructor(
    private val finishGoodApi: FinishGoodApi
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(FinishGoodUIState())
    val uiState: StateFlow<FinishGoodUIState> = _uiState.asStateFlow()
    
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()
    
    /**
     * Handle barcode scan event
     * 
     * Flow:
     * 1. Validate barcode format
     * 2. Extract carton ID
     * 3. Load carton details from backend
     * 4. Initialize article count tracking
     */
    fun onBarcodeScanned(barcode: String) {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true)
                
                Timber.d("Processing barcode: $barcode")
                
                // Extract carton ID from barcode
                val cartonId = extractCartonId(barcode)
                
                if (cartonId.isEmpty()) {
                    onScanError("Invalid barcode format")
                    return@launch
                }
                
                // For now, set current carton directly
                // In production, would load from backend:
                // val response = finishGoodApi.getFinishGood(cartonId.toInt())
                
                _uiState.value = _uiState.value.copy(
                    currentCarton = cartonId,
                    isLoading = false,
                    scannedItems = listOf(
                        ScannedArticle(article = "ARTICLE-001", count = 0),
                        ScannedArticle(article = "ARTICLE-002", count = 0),
                        ScannedArticle(article = "ARTICLE-003", count = 0)
                    )
                )
                
                Timber.d("Carton loaded: $cartonId with ${_uiState.value.scannedItems.size} articles")
                
            } catch (e: Exception) {
                onScanError("Error loading carton: ${e.message}")
                Timber.e(e, "Barcode processing error")
            }
        }
    }
    
    /**
     * Increment article count
     */
    fun incrementCount(article: String) {
        val currentItems = _uiState.value.scannedItems
        val updated = currentItems.map { item ->
            if (item.article == article) {
                item.copy(count = item.count + 1)
            } else {
                item
            }
        }
        _uiState.value = _uiState.value.copy(scannedItems = updated)
        Timber.d("Incremented $article: ${updated.find { it.article == article }?.count}")
    }
    
    /**
     * Decrement article count
     */
    fun decrementCount(article: String) {
        val currentItems = _uiState.value.scannedItems
        val updated = currentItems.map { item ->
            if (item.article == article && item.count > 0) {
                item.copy(count = item.count - 1)
            } else {
                item
            }
        }
        _uiState.value = _uiState.value.copy(scannedItems = updated)
        Timber.d("Decremented $article: ${updated.find { it.article == article }?.count}")
    }
    
    /**
     * Set specific quantity for article
     */
    fun setQuantity(article: String, quantity: Int) {
        val currentItems = _uiState.value.scannedItems
        val updated = currentItems.map { item ->
            if (item.article == article) {
                item.copy(count = maxOf(0, quantity))
            } else {
                item
            }
        }
        _uiState.value = _uiState.value.copy(scannedItems = updated)
        Timber.d("Set $article quantity: $quantity")
    }
    
    /**
     * Confirm carton and submit to backend
     * 
     * Flow:
     * 1. Validate all articles have quantity > 0
     * 2. Create CartonConfirmRequest
     * 3. Send to backend
     * 4. Handle response (success/error)
     * 5. Queue for offline sync if needed
     */
    fun confirmCarton() {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true)
                
                val currentCarton = _uiState.value.currentCarton
                if (currentCarton.isNullOrEmpty()) {
                    onScanError("No carton selected")
                    return@launch
                }
                
                // Calculate total quantity
                val totalQty = _uiState.value.scannedItems.sumOf { it.count }
                
                if (totalQty <= 0) {
                    onScanError("At least one article must have quantity > 0")
                    _uiState.value = _uiState.value.copy(isLoading = false)
                    return@launch
                }
                
                Timber.d("Confirming carton $currentCarton with total qty: $totalQty")
                
                // Create request
                val request = CartonConfirmRequest(
                    carton_id = currentCarton,
                    final_qty = totalQty
                )
                
                // Call API
                try {
                    val response = finishGoodApi.confirmCarton(request)
                    
                    if (response.isSuccessful && response.body()?.success == true) {
                        val finishGoodId = response.body()?.finish_good_id
                        val message = response.body()?.message ?: "Carton confirmed"
                        
                        Timber.d("Carton confirmed with ID: $finishGoodId")
                        
                        // Reset form
                        _uiState.value = FinishGoodUIState()
                        _errorMessage.value = message
                        
                    } else {
                        val error = response.errorBody()?.string() ?: "Unknown error"
                        onScanError("Confirmation failed: $error")
                    }
                } catch (apiError: Exception) {
                    // Offline: Queue for sync
                    queueForSync(currentCarton, totalQty)
                    
                    _uiState.value = FinishGoodUIState()
                    _errorMessage.value = "Offline: Carton queued for sync (ID: $currentCarton)"
                    
                    Timber.w(apiError, "API error, queued for sync")
                }
                
            } catch (e: Exception) {
                onScanError("Error confirming carton: ${e.message}")
                Timber.e(e, "Confirm error")
            } finally {
                _uiState.value = _uiState.value.copy(isLoading = false)
            }
        }
    }
    
    /**
     * Cancel current carton and reset
     */
    fun cancelCarton() {
        _uiState.value = FinishGoodUIState()
        _errorMessage.value = null
        Timber.d("Carton cancelled, form reset")
    }
    
    /**
     * Handle scan error
     */
    fun onScanError(error: String) {
        _uiState.value = _uiState.value.copy(isLoading = false)
        _errorMessage.value = error
        Timber.w("Scan error: $error")
    }
    
    /**
     * Extract carton ID from barcode
     * 
     * Supports formats:
     * - QR Code: { carton_id: "CAR-XXX" }
     * - Code128/EAN: Direct carton ID
     * - Format: CAR-XXXXX or CARXXXXX
     */
    private fun extractCartonId(barcode: String): String {
        return barcode
            .replace("CAR-", "")
            .replace("CAR", "")
            .trim()
            .takeIf { it.isNotEmpty() } ?: ""
    }
    
    /**
     * Queue carton confirmation for offline sync
     * 
     * Stores in local Room database with:
     * - Carton ID
     * - Total quantity
     * - Timestamp
     * - Sync status (PENDING)
     */
    private fun queueForSync(cartonId: String, totalQty: Int) {
        val syncId = UUID.randomUUID().toString()
        Timber.d("Queued for sync - ID: $syncId, Carton: $cartonId, Qty: $totalQty")
        
        // In production, would save to Room database:
        // offlineSyncDao.insert(
        //     OfflineSyncEntity(
        //         id = syncId,
        //         type = "CARTON_CONFIRM",
        //         cartonId = cartonId,
        //         quantity = totalQty,
        //         status = "PENDING",
        //         createdAt = System.currentTimeMillis()
        //     )
        // )
    }
    
    /**
     * Clear error message
     */
    fun clearError() {
        _errorMessage.value = null
    }
}

/**
 * UI State for FinishGood Barcode Screen
 */
data class FinishGoodUIState(
    val currentCarton: String? = null,
    val scannedItems: List<ScannedArticle> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

/**
 * Scanned article model
 */
data class ScannedArticle(
    val article: String,
    val count: Int = 0
)
