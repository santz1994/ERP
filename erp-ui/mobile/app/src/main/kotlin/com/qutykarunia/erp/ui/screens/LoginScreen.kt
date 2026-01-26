package com.qutykarunia.erp.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.qutykarunia.erp.viewmodel.LoginViewModel

/**
 * Login Screen
 * 
 * Authentication workflow:
 * 1. Username/password entry
 * 2. Optional PIN entry (2-factor auth)
 * 3. RFID card reader support (future)
 * 4. JWT token generation & storage
 * 5. Navigate to dashboard on success
 * 
 * Security features:
 * - Password field masking
 * - Secure token storage
 * - JWT token refresh
 * - Error handling
 */
@Composable
fun LoginScreen(
    navController: NavController,
    viewModel: LoginViewModel = hiltViewModel()
) {
    val state by viewModel.uiState.collectAsState()
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var pin by remember { mutableStateOf("") }
    var showPassword by remember { mutableStateOf(false) }
    var rememberMe by remember { mutableStateOf(false) }
    var showPinInput by remember { mutableStateOf(false) }
    
    // Navigate to dashboard on successful login
    LaunchedEffect(state.loginSuccess) {
        if (state.loginSuccess) {
            navController.navigate("dashboard") {
                popUpTo("login") { inclusive = true }
            }
        }
    }
    
    Surface(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background),
        color = MaterialTheme.colorScheme.background
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Logo & App Name
            LoginHeader()
            
            Spacer(modifier = Modifier.height(48.dp))
            
            if (!showPinInput) {
                // Username & Password Form
                LoginForm(
                    username = username,
                    onUsernameChange = { username = it },
                    password = password,
                    onPasswordChange = { password = it },
                    showPassword = showPassword,
                    onShowPasswordToggle = { showPassword = !showPassword },
                    rememberMe = rememberMe,
                    onRememberMeChange = { rememberMe = it },
                    isLoading = state.isLoading,
                    onLogin = {
                        viewModel.login(username, password, rememberMe)
                        showPinInput = true
                    }
                )
            } else {
                // PIN Input Form (2FA)
                PinInputForm(
                    pin = pin,
                    onPinChange = { newPin ->
                        if (newPin.length <= 6) {
                            pin = newPin
                        }
                    },
                    isLoading = state.isLoading,
                    onConfirmPin = {
                        viewModel.confirmPin(pin)
                    },
                    onBackToPassword = {
                        showPinInput = false
                        pin = ""
                    }
                )
            }
            
            // Error Message
            if (state.error != null) {
                Spacer(modifier = Modifier.height(16.dp))
                
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(8.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(12.dp)
                    ) {
                        Text(
                            text = state.error!!,
                            color = MaterialTheme.colorScheme.onErrorContainer,
                            style = MaterialTheme.typography.bodySmall,
                            textAlign = TextAlign.Start
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(32.dp))
            
            // Footer Info
            Text(
                text = "Quty Karunia ERP System v1.0",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Text(
                text = "Min API 25 (Android 7.1.2+)",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

/**
 * Login header with app branding
 */
@Composable
private fun LoginHeader() {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // App Icon/Logo (placeholder)
        Surface(
            modifier = Modifier
                .size(80.dp),
            shape = MaterialTheme.shapes.large,
            color = MaterialTheme.colorScheme.primary
        ) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "ERP",
                    style = MaterialTheme.typography.headlineLarge,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimary
                )
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "Quty Karunia",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface
        )
        
        Text(
            text = "Production Management System",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

/**
 * Login form with username and password
 */
@Composable
private fun LoginForm(
    username: String,
    onUsernameChange: (String) -> Unit,
    password: String,
    onPasswordChange: (String) -> Unit,
    showPassword: Boolean,
    onShowPasswordToggle: () -> Unit,
    rememberMe: Boolean,
    onRememberMeChange: (Boolean) -> Unit,
    isLoading: Boolean,
    onLogin: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Username Field
        OutlinedTextField(
            value = username,
            onValueChange = onUsernameChange,
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            label = { Text("Username") },
            placeholder = { Text("Enter username") },
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Text),
            enabled = !isLoading
        )
        
        // Password Field
        OutlinedTextField(
            value = password,
            onValueChange = onPasswordChange,
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            label = { Text("Password") },
            placeholder = { Text("Enter password") },
            singleLine = true,
            visualTransformation = if (showPassword)
                VisualTransformation.None
            else
                PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
            trailingIcon = {
                IconButton(onClick = onShowPasswordToggle, enabled = !isLoading) {
                    Icon(
                        imageVector = if (showPassword)
                            Icons.Default.VisibilityOff
                        else
                            Icons.Default.Visibility,
                        contentDescription = if (showPassword)
                            "Hide password"
                        else
                            "Show password",
                        tint = MaterialTheme.colorScheme.primary
                    )
                }
            },
            enabled = !isLoading
        )
        
        // Remember Me Checkbox
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Checkbox(
                checked = rememberMe,
                onCheckedChange = onRememberMeChange,
                enabled = !isLoading
            )
            
            Text(
                text = "Remember me",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.padding(start = 8.dp)
            )
        }
        
        // Login Button
        Button(
            onClick = onLogin,
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp),
            enabled = username.isNotEmpty() && password.isNotEmpty() && !isLoading
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    color = MaterialTheme.colorScheme.onPrimary
                )
            } else {
                Text("Login")
            }
        }
    }
}

/**
 * PIN input form for 2FA (optional)
 */
@Composable
private fun PinInputForm(
    pin: String,
    onPinChange: (String) -> Unit,
    isLoading: Boolean,
    onConfirmPin: () -> Unit,
    onBackToPassword: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Info text
        Text(
            text = "Enter PIN Code",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface
        )
        
        Text(
            text = "2-factor authentication required",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // PIN Input Field
        OutlinedTextField(
            value = pin,
            onValueChange = onPinChange,
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            label = { Text("PIN (6 digits)") },
            placeholder = { Text("000000") },
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            visualTransformation = PasswordVisualTransformation(),
            enabled = !isLoading
        )
        
        // PIN dots display
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 16.dp),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            repeat(6) { index ->
                Surface(
                    modifier = Modifier
                        .size(12.dp)
                        .padding(4.dp),
                    shape = MaterialTheme.shapes.small,
                    color = if (index < pin.length)
                        MaterialTheme.colorScheme.primary
                    else
                        MaterialTheme.colorScheme.outlineVariant
                ) {}
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Confirm Button
        Button(
            onClick = onConfirmPin,
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp),
            enabled = pin.length == 6 && !isLoading
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    color = MaterialTheme.colorScheme.onPrimary
                )
            } else {
                Text("Confirm PIN")
            }
        }
        
        // Back Button
        OutlinedButton(
            onClick = onBackToPassword,
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp),
            enabled = !isLoading
        ) {
            Text("Back")
        }
    }
}
