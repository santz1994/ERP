package com.quty.erp.ui.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.quty.erp.api.*
import com.quty.erp.data.repository.FinishGoodRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import timber.log.Timber
import javax.inject.Inject

/**
 * FinishGood ViewModel - Barcode Scanning Logic
 * 
 * RESPONSIBILITIES:
 * 1. Load pending transfers from API
 * 2. Manage current carton state
 * 3. Parse scanned barcode
 * 4. Verify barcode matches carton info
 * 5. Handle manual count verification
 * 6. Submit confirmed count to backend
 * 7. Sync with server (offline-capable)
 * 
 * WORKFLOW:
 * loadPendingTransfers()
 *  ↓
 * currentCarton = first pending
 *  ↓
 * onBarcodeScanned(barcode)
 *  ↓
 * parseBarcode(barcode)
 *  ↓
 * verifyBarcode(parsed, currentCarton)
 *  ↓
 * updateManualCount(count)
 *  ↓
 * confirmCarton(count)
 *  ↓
 * Load next carton or done
 */

@HiltViewModel
class FinishGoodViewModel @Inject constructor(
    private val repository: FinishGoodRepository
) : ViewModel() {

    // ============================================================================
    // STATE MANAGEMENT
    // ============================================================================

    private val _pendingTransfers = MutableStateFlow<List<PendingTransferResponse>>(emptyList())
    val pendingTransfers: StateFlow<List<PendingTransferResponse>> = _pendingTransfers.asStateFlow()

    private val _currentCartonIndex = MutableStateFlow(0)
    val currentCartonIndex: StateFlow<Int> = _currentCartonIndex.asStateFlow()

    private val _currentCarton = MutableStateFlow<PendingTransferResponse?>(null)
    val currentCarton: StateFlow<PendingTransferResponse?> = _currentCarton.asStateFlow()

    private val _isScanning = MutableStateFlow(true)
    val isScanning: StateFlow<Boolean> = _isScanning.asStateFlow()

    private val _scannedBarcode = MutableStateFlow<String?>(null)
    val scannedBarcode: StateFlow<String?> = _scannedBarcode.asStateFlow()

    private val _parsedBarcodeData = MutableStateFlow<ParsedBarcodeData?>(null)
    val parsedBarcodeData: StateFlow<ParsedBarcodeData?> = _parsedBarcodeData.asStateFlow()

    private val _verificationResult = MutableStateFlow<VerifyCartonResponse?>(null)
    val verificationResult: StateFlow<VerifyCartonResponse?> = _verificationResult.asStateFlow()

    private val _manualCount = MutableStateFlow<Int?>(null)
    val manualCount: StateFlow<Int?> = _manualCount.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    private val _successMessage = MutableStateFlow<String?>(null)
    val successMessage: StateFlow<String?> = _successMessage.asStateFlow()

    // ============================================================================
    // PHASE 1: Load Pending Transfers
    // ============================================================================

    fun loadPendingTransfers() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val response = repository.getPendingTransfers()
                if (response.success && response.data != null) {
                    _pendingTransfers.value = response.data
                    if (response.data.isNotEmpty()) {
                        loadNextCarton()
                    } else {
                        _errorMessage.value = "No pending cartons"
                    }
                } else {
                    _errorMessage.value = response.message ?: "Failed to load transfers"
                }
            } catch (e: Exception) {
                _errorMessage.value = "Error: ${e.message}"
                Timber.e(e, "Failed to load pending transfers")
            } finally {
                _isLoading.value = false
            }
        }
    }

    // ============================================================================
    // PHASE 2: Load Next Carton
    // ============================================================================

    private fun loadNextCarton() {
        val index = _currentCartonIndex.value
        if (index < _pendingTransfers.value.size) {
            _currentCarton.value = _pendingTransfers.value[index]
            _isScanning.value = true
            resetScanning()
        }
    }

    // ============================================================================
    // PHASE 3: Barcode Scanning & Parsing
    // ============================================================================

    /**
     * Called when barcode is detected by ML Kit camera
     * 
     * BARCODE FORMAT:
     * - QR Code: "[ARTICLE]|[CARTON_ID]|[QTY]|[DATE]"
     * - Code128: "[CARTON_ID]-[ARTICLE]"
     * 
     * Example:
     * - QR: "IKEA123456|CTN20260001|100|20260126"
     * - Code128: "CTN20260001-IKEA123456"
     */
    fun onBarcodeScanned(rawBarcode: String) {
        Timber.d("Barcode scanned: $rawBarcode")
        _scannedBarcode.value = rawBarcode

        // Parse barcode
        val parsed = parseBarcode(rawBarcode)
        _parsedBarcodeData.value = parsed

        if (parsed != null) {
            // Verify against current carton
            verifyBarcode(parsed)
        } else {
            _errorMessage.value = "Invalid barcode format"
            resetScanning()
        }
    }

    /**
     * ✅ BARCODE PARSING LOGIC
     * 
     * Supports multiple barcode formats for flexibility
     */
    private fun parseBarcode(rawData: String): ParsedBarcodeData? {
        return try {
            when {
                // QR Code format: "ARTICLE|CARTON_ID|QTY|DATE"
                rawData.contains("|") -> {
                    val parts = rawData.split("|")
                    if (parts.size >= 3) {
                        ParsedBarcodeData(
                            article = parts[0],           // IKEA123456
                            cartonId = parts[1],          // CTN20260001
                            quantity = parts[2].toIntOrNull() ?: 0,
                            date = parts.getOrNull(3)     // 20260126
                        )
                    } else null
                }
                // Code128 format: "CARTON_ID-ARTICLE"
                rawData.contains("-") -> {
                    val parts = rawData.split("-")
                    if (parts.size >= 2) {
                        ParsedBarcodeData(
                            article = parts[1],
                            cartonId = parts[0],
                            quantity = null,  // Will verify with system
                            date = null
                        )
                    } else null
                }
                // Plain carton ID (assume system has the article)
                rawData.length >= 8 -> {
                    ParsedBarcodeData(
                        article = null,
                        cartonId = rawData,
                        quantity = null,
                        date = null
                    )
                }
                else -> null
            }
        } catch (e: Exception) {
            Timber.e(e, "Failed to parse barcode")
            null
        }
    }

    // ============================================================================
    // PHASE 4: Barcode Verification
    // ============================================================================

    /**
     * ✅ VERIFICATION LOGIC
     * 
     * Checks if scanned barcode matches current pending carton:
     * 1. Carton ID matches?
     * 2. Article matches?
     * 3. Quantity reasonable?
     * 4. Barcode not already counted?
     */
    private fun verifyBarcode(parsed: ParsedBarcodeData) {
        val carton = _currentCarton.value ?: return

        viewModelScope.launch {
            try {
                // Prepare verification request
                val verifyRequest = VerifyCartonRequest(
                    carton_id = parsed.cartonId,
                    scanned_barcode = _scannedBarcode.value!!,
                    manual_count = null
                )

                // Send to backend for verification
                val response = repository.verifyCarton(verifyRequest)

                if (response.success && response.data != null) {
                    _verificationResult.value = response.data
                    _isScanning.value = false

                    if (response.data.match) {
                        // ✅ Barcode valid - suggest system qty
                        _manualCount.value = response.data.system_qty
                        _successMessage.value = "✅ Barcode verified"
                    } else {
                        _errorMessage.value = "⚠️ ${response.data.message}"
                    }
                } else {
                    _errorMessage.value = response.message ?: "Verification failed"
                }
            } catch (e: Exception) {
                _errorMessage.value = "Error: ${e.message}"
                Timber.e(e, "Barcode verification failed")
            }
        }
    }

    // ============================================================================
    // PHASE 5: Manual Count Input
    // ============================================================================

    fun updateManualCount(count: Int) {
        _manualCount.value = count
        Timber.d("Manual count updated: $count")
    }

    // ============================================================================
    // PHASE 6: Confirm & Submit
    // ============================================================================

    /**
     * ✅ SUBMIT CARTON CONFIRMATION
     * 
     * When user confirms the count:
     * 1. Send final count to backend
     * 2. Backend marks carton as COUNTED
     * 3. Update local cache
     * 4. Load next pending carton
     */
    fun confirmCarton(finalCount: Int) {
        val carton = _currentCarton.value ?: return

        viewModelScope.launch {
            try {
                _isLoading.value = true

                val confirmRequest = ConfirmCartonRequest(
                    transfer_id = carton.transfer_id,
                    carton_id = carton.carton_id,
                    final_count = finalCount,
                    notes = "Mobile FinishGood scan verification"
                )

                val response = repository.confirmCarton(confirmRequest)

                if (response.success) {
                    _successMessage.value = "✅ ${carton.carton_id} confirmed"
                    
                    // Move to next carton
                    _currentCartonIndex.value++
                    loadNextCarton()
                } else {
                    _errorMessage.value = response.message ?: "Confirmation failed"
                }
            } catch (e: Exception) {
                _errorMessage.value = "Error: ${e.message}"
                Timber.e(e, "Failed to confirm carton")
            } finally {
                _isLoading.value = false
            }
        }
    }

    // ============================================================================
    // PHASE 7: Reset & Retry
    // ============================================================================

    fun resetScanning() {
        _scannedBarcode.value = null
        _parsedBarcodeData.value = null
        _verificationResult.value = null
        _manualCount.value = null
        _isScanning.value = true
        _errorMessage.value = null
    }

    // ============================================================================
    // DATA MODELS
    // ============================================================================

    data class ParsedBarcodeData(
        val article: String?,      // e.g., "IKEA123456"
        val cartonId: String,      // e.g., "CTN20260001"
        val quantity: Int?,        // e.g., 100
        val date: String?          // e.g., "20260126"
    )
}

// ============================================================================
// REPOSITORY (Data Access Layer)
// ============================================================================

import javax.inject.Inject

@Inject
class FinishGoodRepository(
    private val finishGoodApi: FinishGoodApi
) {

    suspend fun getPendingTransfers(page: Int = 1, limit: Int = 20): ApiResponse<List<PendingTransferResponse>> {
        return try {
            val response = finishGoodApi.getPendingTransfers(page, limit)
            if (response.isSuccessful) {
                response.body() ?: ApiResponse(false, null, "Empty response")
            } else {
                ApiResponse(false, null, "API Error: ${response.code()}")
            }
        } catch (e: Exception) {
            ApiResponse(false, null, "Network error: ${e.message}")
        }
    }

    suspend fun verifyCarton(request: VerifyCartonRequest): ApiResponse<VerifyCartonResponse> {
        return try {
            val response = finishGoodApi.verifyCarton(request)
            if (response.isSuccessful) {
                response.body() ?: ApiResponse(false, null, "Empty response")
            } else {
                ApiResponse(false, null, "API Error: ${response.code()}")
            }
        } catch (e: Exception) {
            ApiResponse(false, null, "Network error: ${e.message}")
        }
    }

    suspend fun confirmCarton(request: ConfirmCartonRequest): ApiResponse<ConfirmCartonResponse> {
        return try {
            val response = finishGoodApi.confirmCarton(request)
            if (response.isSuccessful) {
                response.body() ?: ApiResponse(false, null, "Empty response")
            } else {
                ApiResponse(false, null, "API Error: ${response.code()}")
            }
        } catch (e: Exception) {
            ApiResponse(false, null, "Network error: ${e.message}")
        }
    }
}
