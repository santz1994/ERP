# 📱 SESSION 31 - ANDROID APP DEVELOPMENT GUIDE

**Target**: FinishGood Mobile App | **Min Android**: 7.1.2 (API 25) | **Target**: API 34  
**Language**: Kotlin | **Architecture**: MVVM + Clean Architecture  

---

## 🎯 ANDROID APP ARCHITECTURE

### Project Structure
```
FinishGoodApp/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── kotlin/com/qutykarunia/erp/
│   │   │   │   ├── MainActivity.kt
│   │   │   │   ├── ui/
│   │   │   │   │   ├── screens/
│   │   │   │   │   │   ├── auth/
│   │   │   │   │   │   │   ├── LoginScreen.kt
│   │   │   │   │   │   │   └── AuthViewModel.kt
│   │   │   │   │   │   ├── inventory/
│   │   │   │   │   │   │   ├── PendingTransfersScreen.kt
│   │   │   │   │   │   │   ├── InventoryViewModel.kt
│   │   │   │   │   │   │   └── InventoryRepository.kt
│   │   │   │   │   │   ├── barcode/
│   │   │   │   │   │   │   ├── BarcodeScannerScreen.kt
│   │   │   │   │   │   │   ├── BarcodeViewModel.kt
│   │   │   │   │   │   │   └── BarcodeAnalyzer.kt
│   │   │   │   │   │   ├── receiving/
│   │   │   │   │   │   │   ├── ReceivingScreen.kt
│   │   │   │   │   │   │   ├── ReceivingViewModel.kt
│   │   │   │   │   │   │   └── ReceivingRepository.kt
│   │   │   │   │   │   └── reports/
│   │   │   │   │   │       ├── ReportsScreen.kt
│   │   │   │   │   │       └── ReportsViewModel.kt
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── CartonCard.kt
│   │   │   │   │   │   ├── BarcodeScanButton.kt
│   │   │   │   │   │   ├── CountVerificationDialog.kt
│   │   │   │   │   │   └── DiscrepancyAlert.kt
│   │   │   │   │   └── navigation/
│   │   │   │   │       └── NavGraph.kt
│   │   │   │   ├── data/
│   │   │   │   │   ├── api/
│   │   │   │   │   │   ├── ApiService.kt
│   │   │   │   │   │   ├── RetrofitClient.kt
│   │   │   │   │   │   ├── models/
│   │   │   │   │   │   │   ├── TransferResponse.kt
│   │   │   │   │   │   │   ├── CartonData.kt
│   │   │   │   │   │   │   └── BarcodeData.kt
│   │   │   │   │   │   └── interceptors/
│   │   │   │   │   │       ├── AuthInterceptor.kt
│   │   │   │   │   │       └── ErrorInterceptor.kt
│   │   │   │   │   ├── database/
│   │   │   │   │   │   ├── AppDatabase.kt
│   │   │   │   │   │   ├── entities/
│   │   │   │   │   │   │   ├── TransferEntity.kt
│   │   │   │   │   │   │   ├── BarcodeRecordEntity.kt
│   │   │   │   │   │   │   └── CartonEntity.kt
│   │   │   │   │   │   └── daos/
│   │   │   │   │   │       ├── TransferDao.kt
│   │   │   │   │   │       ├── BarcodeDao.kt
│   │   │   │   │   │       └── CartonDao.kt
│   │   │   │   │   ├── local/
│   │   │   │   │   │   ├── UserPreferences.kt
│   │   │   │   │   │   └── SessionManager.kt
│   │   │   │   │   └── repository/
│   │   │   │   │       ├── TransferRepository.kt
│   │   │   │   │       ├── BarcodeRepository.kt
│   │   │   │   │       └── AuthRepository.kt
│   │   │   │   ├── domain/
│   │   │   │   │   ├── models/
│   │   │   │   │   │   ├── Transfer.kt
│   │   │   │   │   │   ├── BarcodeRecord.kt
│   │   │   │   │   │   └── Carton.kt
│   │   │   │   │   └── usecases/
│   │   │   │   │       ├── GetPendingTransfersUseCase.kt
│   │   │   │   │       ├── ReceiveCartonUseCase.kt
│   │   │   │   │       ├── ValidateBarcodeUseCase.kt
│   │   │   │   │       └── SyncDataUseCase.kt
│   │   │   │   ├── utils/
│   │   │   │   │   ├── BarcodeUtils.kt
│   │   │   │   │   ├── DateUtils.kt
│   │   │   │   │   ├── NetworkUtils.kt
│   │   │   │   │   ├── PermissionUtils.kt
│   │   │   │   │   ├── ImageUtils.kt
│   │   │   │   │   └── Constants.kt
│   │   │   │   ├── di/
│   │   │   │   │   ├── AppModule.kt
│   │   │   │   │   ├── RepositoryModule.kt
│   │   │   │   │   └── UseCaseModule.kt
│   │   │   │   └── App.kt
│   │   │   ├── AndroidManifest.xml
│   │   │   └── res/
│   │   │       ├── drawable/
│   │   │       │   ├── ic_camera.xml
│   │   │       │   ├── ic_check.xml
│   │   │       │   └── ic_error.xml
│   │   │       ├── layout/
│   │   │       └── values/
│   │   │           ├── strings.xml
│   │   │           ├── colors.xml
│   │   │           └── styles.xml
│   │   ├── test/ (Unit tests)
│   │   └── androidTest/ (Instrumented tests)
│   ├── build.gradle.kts
│   └── proguard-rules.pro
├── gradle/wrapper/
├── gradle.properties
├── settings.gradle.kts
└── build.gradle.kts
```

---

## 🔧 BUILD CONFIGURATION

### build.gradle.kts (Top-level)
```kotlin
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.10" apply false
    id("com.google.hilt.android") version "2.47" apply false
    id("com.google.devtools.ksp") version "1.9.10-1.0.13" apply false
}
```

### app/build.gradle.kts
```kotlin
plugins {
    id("com.android.application")
    kotlin("android")
    kotlin("kapt")
    id("com.google.hilt.android")
    id("com.google.devtools.ksp")
}

android {
    namespace = "com.qutykarunia.erp"
    compileSdk = 34
    
    defaultConfig {
        applicationId = "com.qutykarunia.erp"
        minSdk = 25  // Android 7.1.2
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
        
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        
        buildConfigField("String", "BASE_URL", "\"http://192.168.1.122:8000/api/v1/\"")
        buildConfigField("long", "TOKEN_EXPIRY_MS", "86400000")  // 24 hours
    }
    
    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            buildConfigField("String", "BASE_URL", "\"https://api.qutykarunia.com/api/v1/\"")
        }
        debug {
            isDebuggable = true
        }
    }
    
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    
    kotlinOptions {
        jvmTarget = "17"
    }
    
    buildFeatures {
        compose = true
        buildConfig = true
    }
    
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.3"
    }
}

dependencies {
    // Core Android
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
    implementation("androidx.activity:activity-compose:1.8.1")
    
    // Jetpack Compose
    implementation("androidx.compose.ui:ui:1.6.0")
    implementation("androidx.compose.ui:ui-graphics:1.6.0")
    implementation("androidx.compose.ui:ui-tooling-preview:1.6.0")
    implementation("androidx.compose.material3:material3:1.1.2")
    implementation("androidx.navigation:navigation-compose:2.7.5")
    
    // Hilt (Dependency Injection)
    implementation("com.google.dagger:hilt-android:2.47")
    kapt("com.google.dagger:hilt-compiler:2.47")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")
    
    // Retrofit + OkHttp
    implementation("com.squareup.retrofit2:retrofit:2.10.0")
    implementation("com.squareup.retrofit2:converter-gson:2.10.0")
    implementation("com.squareup.okhttp3:okhttp:4.11.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.11.0")
    
    // Room Database
    implementation("androidx.room:room-runtime:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    
    // DataStore (Preferences)
    implementation("androidx.datastore:datastore-preferences:1.0.0")
    
    // ML Kit Vision (Barcode scanning)
    implementation("com.google.mlkit:barcode-scanning:17.2.0")
    implementation("androidx.camera:camera-core:1.3.0")
    implementation("androidx.camera:camera-camera2:1.3.0")
    implementation("androidx.camera:camera-lifecycle:1.3.0")
    implementation("androidx.camera:camera-view:1.3.0")
    
    // ZXing (Alternative barcode)
    implementation("com.google.zxing:core:3.5.2")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    
    // JSON
    implementation("com.google.code.gson:gson:2.10.1")
    
    // Logging
    implementation("com.jakewharton.timber:timber:5.0.1")
    
    // WorkManager (Background sync)
    implementation("androidx.work:work-runtime-ktx:2.8.1")
    
    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.mockito:mockito-core:5.5.1")
    testImplementation("org.mockito.kotlin:mockito-kotlin:5.1.0")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.6.0")
    debugImplementation("androidx.compose.ui:ui-tooling:1.6.0")
    debugImplementation("androidx.compose.ui:ui-test-manifest:1.6.0")
}
```

---

## 📲 CORE SCREENS & IMPLEMENTATION

### Screen 1: Login Screen
```kotlin
@Composable
fun LoginScreen(
    viewModel: AuthViewModel = hiltViewModel(),
    onLoginSuccess: () -> Unit = {}
) {
    var pinInput by remember { mutableStateOf("") }
    var showError by remember { mutableStateOf(false) }
    val loginState by viewModel.loginState.collectAsState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Logo
        Image(
            painter = painterResource(id = R.drawable.ic_logo),
            contentDescription = "Logo",
            modifier = Modifier.size(120.dp)
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Title
        Text(
            text = "FinishGood Warehouse",
            style = MaterialTheme.typography.headlineLarge,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // PIN Input
        OutlinedTextField(
            value = pinInput,
            onValueChange = { if (it.length <= 6) pinInput = it },
            label = { Text("Enter PIN") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword),
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth()
        )
        
        if (showError) {
            Text(
                text = "Invalid PIN",
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 8.dp)
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Login Button
        Button(
            onClick = {
                viewModel.login(pinInput)
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(50.dp),
            enabled = pinInput.length == 6 && loginState !is LoginState.Loading
        ) {
            if (loginState is LoginState.Loading) {
                CircularProgressIndicator(modifier = Modifier.size(24.dp))
            } else {
                Text("Login")
            }
        }
        
        // RFID Option
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = { /* Trigger RFID reading */ },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.secondaryButtonColors()
        ) {
            Text("Scan RFID")
        }
    }
    
    // Handle login states
    LaunchedEffect(loginState) {
        when (loginState) {
            is LoginState.Success -> onLoginSuccess()
            is LoginState.Error -> showError = true
            else -> {}
        }
    }
}
```

### Screen 2: Pending Transfers
```kotlin
@Composable
fun PendingTransfersScreen(
    viewModel: InventoryViewModel = hiltViewModel(),
    onCartonSelected: (Int) -> Unit = {}
) {
    val transfers by viewModel.pendingTransfers.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
        Text(
            text = "Pending Transfers",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.align(Alignment.CenterHorizontally)
            )
        } else {
            // List of cartons
            LazyColumn {
                items(transfers.size) { index ->
                    val carton = transfers[index]
                    CartonCard(
                        carton = carton,
                        onClick = { onCartonSelected(carton.id) }
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                }
            }
        }
    }
    
    // Trigger fetch on screen load
    LaunchedEffect(Unit) {
        viewModel.fetchPendingTransfers()
    }
}

@Composable
fun CartonCard(
    carton: CartonData,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Carton #${carton.cartonNumber}",
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Article: ${carton.articleCode}",
                        style = MaterialTheme.typography.bodySmall
                    )
                    Text(
                        text = "Expected: ${carton.expectedPieces} pieces",
                        style = MaterialTheme.typography.bodySmall
                    )
                }
                
                StatusBadge(status = carton.status)
            }
        }
    }
}

@Composable
fun StatusBadge(status: String) {
    Badge(
        modifier = Modifier.background(
            when (status) {
                "PENDING" -> MaterialTheme.colorScheme.error
                "SCANNING" -> MaterialTheme.colorScheme.tertiary
                "COMPLETE" -> MaterialTheme.colorScheme.tertiary
                else -> MaterialTheme.colorScheme.outline
            }
        )
    ) {
        Text(status, color = Color.White)
    }
}
```

### Screen 3: Barcode Scanner
```kotlin
@Composable
fun BarcodeScannerScreen(
    transferId: Int,
    viewModel: BarcodeViewModel = hiltViewModel(),
    onScanComplete: () -> Unit = {}
) {
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraPermissionState = rememberPermissionState(
        Manifest.permission.CAMERA
    )
    
    var scannedBarcode by remember { mutableStateOf("") }
    val scanResult by viewModel.scanResult.collectAsState()
    
    LaunchedEffect(Unit) {
        if (!cameraPermissionState.status.isGranted) {
            cameraPermissionState.launchPermissionRequest()
        }
    }
    
    if (cameraPermissionState.status.isGranted) {
        Box(modifier = Modifier.fillMaxSize()) {
            // Camera Preview
            AndroidView(
                factory = { context ->
                    PreviewView(context).apply {
                        // Setup camera
                        val cameraProvider = ProcessCameraProvider.getInstance(context).get()
                        val preview = Preview.Builder().build().also {
                            it.setSurfaceProvider(surfaceProvider)
                        }
                        
                        val imageAnalysis = ImageAnalysis.Builder()
                            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                            .build()
                        
                        imageAnalysis.setAnalyzer(Executors.newSingleThreadExecutor()) { imageProxy ->
                            viewModel.analyzeImage(imageProxy)
                        }
                        
                        try {
                            cameraProvider.unbindAll()
                            cameraProvider.bindToLifecycle(
                                lifecycleOwner,
                                CameraSelector.DEFAULT_BACK_CAMERA,
                                preview,
                                imageAnalysis
                            )
                        } catch (e: Exception) {
                            Log.e("BarcodeScanner", "Use case binding failed", e)
                        }
                    }
                },
                modifier = Modifier.fillMaxSize()
            )
            
            // Overlay and controls
            Column(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                if (scannedBarcode.isNotEmpty()) {
                    Text(
                        text = "Scanned: $scannedBarcode",
                        style = MaterialTheme.typography.bodyLarge,
                        color = Color.White,
                        modifier = Modifier
                            .background(Color.Black.copy(alpha = 0.7f))
                            .padding(8.dp)
                    )
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Button(
                    onClick = { onScanComplete() },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Next")
                }
            }
        }
    } else {
        Text("Camera permission required")
    }
    
    // Handle scan results
    LaunchedEffect(scanResult) {
        when (scanResult) {
            is BarcodeResult.Success -> {
                scannedBarcode = scanResult.barcode
                viewModel.validateBarcode(scanResult.barcode, transferId)
            }
            is BarcodeResult.Error -> {
                // Show error
            }
            else -> {}
        }
    }
}
```

### Screen 4: Count Verification
```kotlin
@Composable
fun CountVerificationScreen(
    carton: CartonData,
    viewModel: ReceivingViewModel = hiltViewModel(),
    onConfirm: () -> Unit = {}
) {
    var actualCount by remember { mutableStateOf(0) }
    var reasonForDiscrepancy by remember { mutableStateOf("") }
    val isLoading by viewModel.isLoading.collectAsState()
    
    val discrepancy = if (actualCount > 0) {
        actualCount - carton.expectedPieces
    } else {
        0
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Verify Count",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Expected count display
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "Expected Pieces: ${carton.expectedPieces}",
                    style = MaterialTheme.typography.bodyLarge
                )
                Text(
                    text = "Carton #${carton.cartonNumber}",
                    style = MaterialTheme.typography.bodySmall
                )
                Text(
                    text = "Article: ${carton.articleCode}",
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Actual count input
        OutlinedTextField(
            value = if (actualCount > 0) actualCount.toString() else "",
            onValueChange = { actualCount = it.toIntOrNull() ?: 0 },
            label = { Text("Enter Actual Count") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Discrepancy display
        if (discrepancy != 0) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = if (discrepancy < 0) {
                        MaterialTheme.colorScheme.errorContainer
                    } else {
                        MaterialTheme.colorScheme.tertiaryContainer
                    }
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = if (discrepancy < 0) "Shortage" else "Overage",
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Difference: $discrepancy pieces",
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Reason input
            OutlinedTextField(
                value = reasonForDiscrepancy,
                onValueChange = { reasonForDiscrepancy = it },
                label = { Text("Reason for Discrepancy") },
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = 100.dp),
                maxLines = 4
            )
        }
        
        Spacer(modifier = Modifier.weight(1f))
        
        // Confirm button
        Button(
            onClick = {
                viewModel.confirmReceipt(
                    cartonId = carton.id,
                    actualCount = actualCount,
                    reason = reasonForDiscrepancy
                )
                onConfirm()
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(50.dp),
            enabled = actualCount > 0 && !isLoading
        ) {
            if (isLoading) {
                CircularProgressIndicator(modifier = Modifier.size(24.dp))
            } else {
                Text("Confirm Receipt")
            }
        }
    }
}
```

---

## 🏗️ VIEWMODELS & STATE MANAGEMENT

### AuthViewModel
```kotlin
@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _loginState = MutableStateFlow<LoginState>(LoginState.Idle)
    val loginState: StateFlow<LoginState> = _loginState.asStateFlow()
    
    fun login(pin: String) {
        viewModelScope.launch {
            _loginState.value = LoginState.Loading
            try {
                val response = authRepository.login(pin)
                if (response.isSuccessful) {
                    _loginState.value = LoginState.Success(response.body())
                } else {
                    _loginState.value = LoginState.Error("Login failed")
                }
            } catch (e: Exception) {
                _loginState.value = LoginState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed class LoginState {
    object Idle : LoginState()
    object Loading : LoginState()
    data class Success(val data: AuthResponse) : LoginState()
    data class Error(val message: String) : LoginState()
}
```

### InventoryViewModel
```kotlin
@HiltViewModel
class InventoryViewModel @Inject constructor(
    private val transferRepository: TransferRepository
) : ViewModel() {
    
    private val _pendingTransfers = MutableStateFlow<List<CartonData>>(emptyList())
    val pendingTransfers: StateFlow<List<CartonData>> = _pendingTransfers.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    fun fetchPendingTransfers() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val transfers = transferRepository.getPendingTransfers()
                _pendingTransfers.value = transfers
            } catch (e: Exception) {
                Log.e("InventoryViewModel", "Error fetching transfers", e)
            } finally {
                _isLoading.value = false
            }
        }
    }
}
```

### BarcodeViewModel
```kotlin
@HiltViewModel
class BarcodeViewModel @Inject constructor(
    private val barcodeRepository: BarcodeRepository
) : ViewModel() {
    
    private val _scanResult = MutableStateFlow<BarcodeResult>(BarcodeResult.Idle)
    val scanResult: StateFlow<BarcodeResult> = _scanResult.asStateFlow()
    
    fun analyzeImage(imageProxy: ImageProxy) {
        viewModelScope.launch {
            try {
                val bitmap = imageProxy.toBitmap()
                val result = barcodeRepository.scanBarcode(bitmap)
                _scanResult.value = result
                imageProxy.close()
            } catch (e: Exception) {
                _scanResult.value = BarcodeResult.Error(e.message ?: "Scan failed")
                imageProxy.close()
            }
        }
    }
    
    fun validateBarcode(barcode: String, transferId: Int) {
        viewModelScope.launch {
            val isValid = barcodeRepository.validateFormat(barcode)
            if (isValid) {
                // Proceed
            } else {
                _scanResult.value = BarcodeResult.Error("Invalid barcode format")
            }
        }
    }
}

sealed class BarcodeResult {
    object Idle : BarcodeResult()
    data class Success(val barcode: String) : BarcodeResult()
    data class Error(val message: String) : BarcodeResult()
}
```

---

## 🔌 API INTEGRATION

### ApiService
```kotlin
interface ApiService {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<AuthResponse>
    
    @GET("finishgoods/pending-transfers")
    suspend fun getPendingTransfers(): Response<List<TransferResponse>>
    
    @GET("finishgoods/status/{transferId}")
    suspend fun getTransferStatus(@Path("transferId") transferId: Int): Response<TransferResponse>
    
    @POST("finishgoods/record-received")
    suspend fun recordReceived(@Body request: ReceiveCartonRequest): Response<ReceiptResponse>
    
    @POST("finishgoods/confirm-delivery")
    suspend fun confirmDelivery(@Body request: ConfirmDeliveryRequest): Response<ReceiptResponse>
    
    @POST("barcode/validate")
    suspend fun validateBarcode(@Body request: BarcodeValidationRequest): Response<ValidationResponse>
}
```

### RetrofitClient
```kotlin
object RetrofitClient {
    fun createService(context: Context, token: String? = null): ApiService {
        val httpClient = OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor(token))
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
        
        return Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .client(httpClient)
            .build()
            .create(ApiService::class.java)
    }
}
```

---

## 💾 DATABASE MODELS

### Room Entities
```kotlin
@Entity(tableName = "transfers")
data class TransferEntity(
    @PrimaryKey
    val id: Int,
    val fromDept: String,
    val toDept: String,
    val cartonCount: Int,
    val expectedQty: Int,
    val actualQty: Int?,
    val status: String,
    val createdAt: Long,
    val receivedAt: Long?
)

@Entity(tableName = "barcode_records")
data class BarcodeRecordEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val transferId: Int,
    val barcode: String,
    val articleCode: String,
    val weekNumber: String,
    val scannedAt: Long
)

@Entity(tableName = "cartons")
data class CartonEntity(
    @PrimaryKey
    val id: Int,
    val cartonNumber: Int,
    val barcode: String,
    val articleCode: String,
    val weekNumber: String,
    val expectedPieces: Int,
    val actualPieces: Int?,
    val status: String  // PENDING, SCANNED, RECEIVED, STORED
)
```

---

## ✅ IMPLEMENTATION CHECKLIST

- [ ] Create Android Studio project
- [ ] Setup project structure & build.gradle
- [ ] Implement authentication flow
- [ ] Implement pending transfers screen
- [ ] Implement barcode scanner (ML Kit)
- [ ] Implement count verification screen
- [ ] Implement offline database (Room)
- [ ] Implement data synchronization
- [ ] Implement error handling & retry logic
- [ ] Add unit tests (ViewModels, repositories)
- [ ] Add instrumented tests (UI)
- [ ] Implement offline capability (WorkManager)
- [ ] Test on Android 7.1.2+ devices
- [ ] Add ProGuard rules for production
- [ ] Create APK build & sign
- [ ] Create user documentation

---

**Status**: Ready for implementation  
**Next Steps**: Start with project setup and authentication  
**Testing**: Minimum Android 7.1.2 (API 25), target API 34

