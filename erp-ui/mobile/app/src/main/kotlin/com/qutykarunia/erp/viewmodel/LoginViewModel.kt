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
import com.qutykarunia.erp.data.models.LoginRequest
import timber.log.Timber
import javax.inject.Inject

/**
 * LoginScreen ViewModel
 * 
 * Manages:
 * 1. Username/password validation
 * 2. API authentication calls
 * 3. JWT token storage
 * 4. Optional PIN (2FA) verification
 * 5. Session management
 * 6. Error handling
 */
@HiltViewModel
class LoginViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val productionApi: ProductionApi
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(LoginUIState())
    val uiState: StateFlow<LoginUIState> = _uiState.asStateFlow()
    
    private var tempUsername = ""
    private var tempPassword = ""
    
    /**
     * Perform login with username and password
     * 
     * Flow:
     * 1. Validate input
     * 2. Call authentication API
     * 3. Store JWT token
     * 4. Check if PIN is required (2FA)
     * 5. Update UI state
     */
    fun login(username: String, password: String, rememberMe: Boolean) {
        // Validation
        if (username.trim().isEmpty()) {
            _uiState.value = _uiState.value.copy(error = "Username cannot be empty")
            return
        }
        
        if (password.isEmpty()) {
            _uiState.value = _uiState.value.copy(error = "Password cannot be empty")
            return
        }
        
        if (password.length < 6) {
            _uiState.value = _uiState.value.copy(error = "Password must be at least 6 characters")
            return
        }
        
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(
                    isLoading = true,
                    error = null
                )
                
                tempUsername = username
                tempPassword = password
                
                Timber.d("Attempting login for user: $username")
                
                // Create login request
                val request = LoginRequest(
                    username = username.trim(),
                    password = password
                )
                
                // In production, would call:
                // val response = productionApi.login(request)
                
                // Mock successful login for now
                // In production:
                // if (response.isSuccessful && response.body()?.success == true) {
                //     val data = response.body()!!
                //     TokenManager.saveToken(context, data.access_token, data.expires_in)
                //     TokenManager.saveRefreshToken(context, data.refresh_token)
                //     
                //     if (rememberMe) {
                //         saveCredentials(username)
                //     }
                //     
                //     // Check if 2FA is required
                //     val requires2FA = data.requires_2fa ?: false
                //     
                //     _uiState.value = _uiState.value.copy(
                //         isLoading = false,
                //         requires2FA = requires2FA
                //     )
                // } else {
                //     handleLoginError(response)
                // }
                
                // Mock: Simulate PIN requirement
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    requires2FA = true, // Mock: require PIN
                    error = null
                )
                
                Timber.d("Login request sent, 2FA required")
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = "Login failed: ${e.message}"
                )
                Timber.e(e, "Login error")
            }
        }
    }
    
    /**
     * Confirm PIN for 2FA verification
     * 
     * Flow:
     * 1. Validate PIN format (6 digits)
     * 2. Call 2FA verification API
     * 3. Generate final JWT token
     * 4. Mark login as successful
     */
    fun confirmPin(pin: String) {
        // Validation
        if (pin.length != 6) {
            _uiState.value = _uiState.value.copy(error = "PIN must be 6 digits")
            return
        }
        
        if (!pin.all { it.isDigit() }) {
            _uiState.value = _uiState.value.copy(error = "PIN must contain only numbers")
            return
        }
        
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(
                    isLoading = true,
                    error = null
                )
                
                Timber.d("Verifying PIN for user: $tempUsername")
                
                // In production, would call 2FA verification API:
                // val response = authApi.verify2FA(pin)
                
                // Mock successful 2FA
                // if (response.isSuccessful && response.body()?.success == true) {
                //     val data = response.body()!!
                //     TokenManager.saveToken(context, data.access_token, data.expires_in)
                //     
                //     _uiState.value = _uiState.value.copy(
                //         isLoading = false,
                //         loginSuccess = true
                //     )
                // } else {
                //     handlePinError(response)
                // }
                
                // Mock: Accept any PIN
                storeTokens("mock_jwt_token_${System.currentTimeMillis()}")
                
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    loginSuccess = true,
                    error = null
                )
                
                Timber.d("2FA verification successful, user logged in")
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = "PIN verification failed: ${e.message}"
                )
                Timber.e(e, "PIN verification error")
            }
        }
    }
    
    /**
     * Store JWT tokens in secure storage
     */
    private fun storeTokens(accessToken: String) {
        TokenManager.saveToken(context, accessToken, expiresIn = 86400) // 24 hours
        TokenManager.saveRefreshToken(context, "mock_refresh_token_${System.currentTimeMillis()}")
        
        Timber.d("Tokens stored in secure storage")
    }
    
    /**
     * Clear error message
     */
    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
    
    /**
     * Logout and clear session
     */
    fun logout() {
        viewModelScope.launch {
            try {
                TokenManager.clearTokens(context)
                _uiState.value = LoginUIState()
                tempUsername = ""
                tempPassword = ""
                
                Timber.d("User logged out, tokens cleared")
                
            } catch (e: Exception) {
                Timber.e(e, "Logout error")
            }
        }
    }
}

/**
 * UI State for LoginScreen
 */
data class LoginUIState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val loginSuccess: Boolean = false,
    val requires2FA: Boolean = false,
    val userId: String? = null,
    val userRole: String? = null
)
