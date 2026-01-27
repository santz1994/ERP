package com.erp2026.viewmodel

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import androidx.lifecycle.Observer
import com.erp2026.data.repository.AuthRepository
import com.erp2026.domain.model.LoginRequest
import com.erp2026.domain.model.LoginResponse
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.whenever
import org.mockito.kotlin.verify

@ExperimentalCoroutinesApi
class LoginViewModelTest {
    
    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()
    
    @Mock
    private lateinit var authRepository: AuthRepository
    
    @Mock
    private lateinit var loginObserver: Observer<LoginState>
    
    private lateinit var viewModel: LoginViewModel
    
    @Before
    fun setUp() {
        MockitoAnnotations.openMocks(this)
        viewModel = LoginViewModel(authRepository)
    }
    
    @Test
    fun testLoginSuccess() = runTest {
        // Arrange
        val username = "user123"
        val password = "password123"
        val expectedResponse = LoginResponse(
            accessToken = "token_abc123",
            refreshToken = "refresh_token_xyz",
            userId = 1,
            userName = username,
            userRole = "OPERATOR"
        )
        
        whenever(authRepository.login(username, password)).thenReturn(expectedResponse)
        
        viewModel.loginState.observeForever(loginObserver)
        
        // Act
        viewModel.login(username, password)
        
        // Assert
        verify(loginObserver).onChanged(LoginState.Loading)
        verify(loginObserver).onChanged(LoginState.Success(expectedResponse))
    }
    
    @Test
    fun testLoginFailureInvalidCredentials() = runTest {
        // Arrange
        val username = "invalid"
        val password = "wrong"
        val errorMessage = "Invalid credentials"
        
        whenever(authRepository.login(username, password))
            .thenThrow(Exception(errorMessage))
        
        viewModel.loginState.observeForever(loginObserver)
        
        // Act
        viewModel.login(username, password)
        
        // Assert
        verify(loginObserver).onChanged(LoginState.Loading)
        verify(loginObserver).onChanged(LoginState.Error(errorMessage))
    }
    
    @Test
    fun testLoginValidation() {
        // Test empty username
        assert(viewModel.validateUsername("").not())
        
        // Test empty password
        assert(viewModel.validatePassword("").not())
        
        // Test valid credentials
        assert(viewModel.validateUsername("user123"))
        assert(viewModel.validatePassword("password123"))
    }
    
    @Test
    fun testLogout() = runTest {
        // Arrange
        whenever(authRepository.logout()).thenReturn(Unit)
        
        viewModel.loginState.observeForever(loginObserver)
        
        // Act
        viewModel.logout()
        
        // Assert
        verify(loginObserver).onChanged(LoginState.LoggedOut)
    }
    
    @Test
    fun testRememberMe() {
        // Arrange
        val username = "user123"
        
        // Act
        viewModel.setRememberMe(true)
        viewModel.saveCredentials(username)
        
        // Assert
        assert(viewModel.rememberMeEnabled.value == true)
    }
    
    @Test
    fun testPasswordReset() = runTest {
        // Arrange
        val email = "user@company.com"
        whenever(authRepository.requestPasswordReset(email)).thenReturn(Unit)
        
        // Act
        viewModel.requestPasswordReset(email)
        
        // Assert
        verify(authRepository).requestPasswordReset(email)
    }
    
    @Test
    fun testTwoFactorAuthentication() = runTest {
        // Arrange
        val code = "123456"
        whenever(authRepository.verifyTwoFactor(code)).thenReturn(true)
        
        // Act
        val result = viewModel.verifyTwoFactor(code)
        
        // Assert
        assert(result == true)
    }
    
    @Test
    fun testSessionTimeout() = runTest {
        // Arrange
        val timeoutMinutes = 30
        
        // Act
        viewModel.setSessionTimeout(timeoutMinutes)
        
        // Assert
        assert(viewModel.sessionTimeout.value == timeoutMinutes)
    }
}

sealed class LoginState {
    object Loading : LoginState()
    data class Success(val response: LoginResponse) : LoginState()
    data class Error(val message: String) : LoginState()
    object LoggedOut : LoginState()
}
