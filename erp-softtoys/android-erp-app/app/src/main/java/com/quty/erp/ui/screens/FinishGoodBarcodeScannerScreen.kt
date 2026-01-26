package com.quty.erp.ui.screens

import androidx.camera.core.Camera
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.LifecycleOwner
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.common.InputImage
import com.quty.erp.api.ConfirmCartonRequest
import com.quty.erp.api.VerifyCartonRequest
import com.quty.erp.ui.viewmodels.FinishGoodViewModel
import java.util.concurrent.Executor
import java.util.concurrent.Executors

/**
 * FinishGood Barcode Scanning Screen
 * 
 * WORKFLOW:
 * 1. Load pending transfers from backend
 * 2. Display current carton info
 * 3. Open camera with ML Kit barcode scanning
 * 4. Scan carton barcode
 * 5. Parse and validate barcode
 * 6. Manual count verification
 * 7. Confirm & mark as counted
 * 8. Load next pending carton
 * 
 * BARCODE FORMAT:
 * - Format: "[ARTICLE]|[CARTON_ID]|[QTY]|[DATE]"
 * - Example: "IKEA123456|CTN20260001|100|20260126"
 * - Uses QR code or Code128 for reliability
 */

@Composable
fun FinishGoodBarcodeScannerScreen(
    viewModel: FinishGoodViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit
) {
    val currentCarton by viewModel.currentCarton.collectAsState()
    val isScanning by viewModel.isScanning.collectAsState()
    val scannedBarcode by viewModel.scannedBarcode.collectAsState()
    val verificationResult by viewModel.verificationResult.collectAsState()
    val manualCount by viewModel.manualCount.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()
    
    LaunchedEffect(Unit) {
        viewModel.loadPendingTransfers()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
    ) {
        // 🔴 HEADER
        FinishGoodHeader(
            cartonId = currentCarton?.carton_id ?: "No carton",
            article = currentCarton?.article_name ?: "Loading...",
            onClose = onNavigateBack
        )

        if (isLoading) {
            // Loading state
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = Color.White)
            }
        } else if (currentCarton != null) {
            when {
                !isScanning && scannedBarcode == null -> {
                    // 📷 SCANNING MODE
                    BarcodeScannerView(
                        onBarcodeDetected = { barcode ->
                            viewModel.onBarcodeScanned(barcode)
                        },
                        currentCarton = currentCarton!!
                    )
                }
                scannedBarcode != null && verificationResult != null -> {
                    // ✅ VERIFICATION RESULT
                    VerificationResultView(
                        cartonId = currentCarton!!.carton_id,
                        scannedBarcode = scannedBarcode!!,
                        verificationResult = verificationResult!!,
                        systemQty = currentCarton!!.qty,
                        manualCount = manualCount,
                        onCountChanged = { viewModel.updateManualCount(it) },
                        onConfirm = { 
                            viewModel.confirmCarton(manualCount ?: currentCarton!!.qty)
                        },
                        onRetry = { 
                            viewModel.resetScanning()
                        }
                    )
                }
            }
        } else {
            // No pending cartons
            NoPendingCartons(onClose = onNavigateBack)
        }

        // Error message
        if (errorMessage != null) {
            Snackbar(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(16.dp),
                containerColor = MaterialTheme.colorScheme.error
            ) {
                Text(errorMessage!!, color = Color.White)
            }
        }
    }
}


// ============================================================================
// COMPONENT 1: Header with Carton Info
// ============================================================================

@Composable
private fun FinishGoodHeader(
    cartonId: String,
    article: String,
    onClose: () -> Unit
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .height(100.dp),
        color = Color(0xFF1F1F1F)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "Carton: $cartonId",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Text(
                    text = article,
                    fontSize = 14.sp,
                    color = Color.Gray
                )
            }
            
            IconButton(onClick = onClose) {
                Icon(Icons.Default.Close, contentDescription = "Close", tint = Color.White)
            }
        }
    }
}


// ============================================================================
// COMPONENT 2: Barcode Scanner View (ML Kit)
// ============================================================================

@Composable
private fun BarcodeScannerView(
    onBarcodeDetected: (String) -> Unit,
    currentCarton: com.quty.erp.api.PendingTransferResponse
) {
    val lifecycleOwner = androidx.lifecycle.compose.LocalLifecycleOwner.current
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(androidx.compose.ui.platform.LocalContext.current) }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
    ) {
        // Camera preview
        AndroidView(
            modifier = Modifier.fillMaxSize(),
            factory = { context ->
                val previewView = PreviewView(context)
                val executor = Executors.newSingleThreadExecutor()
                
                cameraProviderFuture.addListener({
                    val cameraProvider = cameraProviderFuture.get()
                    val preview = Preview.Builder().build().also {
                        it.setSurfaceProvider(previewView.surfaceProvider)
                    }

                    // ✅ BARCODE ANALYZER WITH ML KIT
                    val imageAnalyzer = ImageAnalysis.Builder()
                        .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                        .build()
                        .also {
                            it.setAnalyzer(executor) { imageProxy ->
                                processImage(imageProxy, onBarcodeDetected)
                                imageProxy.close()
                            }
                        }

                    val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

                    try {
                        cameraProvider.unbindAll()
                        cameraProvider.bindToLifecycle(
                            lifecycleOwner,
                            cameraSelector,
                            preview,
                            imageAnalyzer
                        )
                    } catch (exc: Exception) {
                        // Handle binding error
                    }
                }, executor)

                previewView
            }
        )

        // 🎯 SCANNER GUIDE (Red rectangle)
        Box(
            modifier = Modifier
                .align(Alignment.Center)
                .size(300.dp, 200.dp)
                .background(Color.Transparent, shape = androidx.compose.foundation.shape.RoundedCornerShape(8.dp))
        ) {
            // Top line
            Divider(color = Color.Red, thickness = 2.dp, modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.TopCenter))
            // Bottom line
            Divider(color = Color.Red, thickness = 2.dp, modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter))
        }

        // Instructions
        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(32.dp)
                .fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Align barcode within the red box",
                color = Color.White,
                fontSize = 16.sp,
                fontWeight = FontWeight.Medium
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "System quantity: ${currentCarton.qty} units",
                color = Color.Gray,
                fontSize = 14.sp
            )
        }
    }
}


// ============================================================================
// COMPONENT 3: Verification Result View
// ============================================================================

@Composable
private fun VerificationResultView(
    cartonId: String,
    scannedBarcode: String,
    verificationResult: com.quty.erp.api.VerifyCartonResponse,
    systemQty: Int,
    manualCount: Int?,
    onCountChanged: (Int) -> Unit,
    onConfirm: () -> Unit,
    onRetry: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .padding(16.dp),
        verticalArrangement = Arrangement.Center
    ) {
        // ✅ Verification Status
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            color = if (verificationResult.match) Color(0xFF2E7D32) else Color(0xFFC62828),
            shape = androidx.compose.foundation.shape.RoundedCornerShape(8.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = if (verificationResult.match) "✅ Barcode Verified" else "❌ Mismatch",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = verificationResult.message,
                    color = Color.White,
                    fontSize = 14.sp
                )
            }
        }

        // Article info
        InfoCard(label = "Article", value = verificationResult.article)
        InfoCard(label = "Carton ID", value = cartonId)
        InfoCard(label = "System Quantity", value = verificationResult.system_qty.toString())

        Spacer(modifier = Modifier.height(24.dp))

        // Manual count input
        CountInputSection(
            label = "Actual Count",
            value = manualCount ?: systemQty,
            systemQty = systemQty,
            onChange = onCountChanged
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Action buttons
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Button(
                onClick = onRetry,
                modifier = Modifier
                    .weight(1f)
                    .height(50.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF424242))
            ) {
                Text("Retry Scan", color = Color.White, fontWeight = FontWeight.Bold)
            }

            Button(
                onClick = onConfirm,
                modifier = Modifier
                    .weight(1f)
                    .height(50.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32))
            ) {
                Text("Confirm", color = Color.White, fontWeight = FontWeight.Bold)
            }
        }
    }
}


// ============================================================================
// HELPER COMPONENTS
// ============================================================================

@Composable
private fun InfoCard(label: String, value: String) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp),
        color = Color(0xFF1F1F1F),
        shape = androidx.compose.foundation.shape.RoundedCornerShape(4.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(label, color = Color.Gray, fontSize = 14.sp)
            Text(value, color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun CountInputSection(
    label: String,
    value: Int,
    systemQty: Int,
    onChange: (Int) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        Text(label, color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.Medium)
        Spacer(modifier = Modifier.height(8.dp))
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Button(
                onClick = { onChange(maxOf(0, value - 1)) },
                modifier = Modifier.size(50.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF424242))
            ) {
                Text("-", fontWeight = FontWeight.Bold)
            }
            
            Surface(
                modifier = Modifier
                    .weight(1f)
                    .height(50.dp)
                    .padding(horizontal = 16.dp),
                color = Color(0xFF1F1F1F),
                shape = androidx.compose.foundation.shape.RoundedCornerShape(4.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text(
                        value.toString(),
                        color = Color.White,
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            
            Button(
                onClick = { onChange(value + 1) },
                modifier = Modifier.size(50.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF424242))
            ) {
                Text("+", fontWeight = FontWeight.Bold)
            }
        }
        
        if (value != systemQty) {
            Text(
                "System qty: $systemQty",
                color = Color(0xFFFFA500),
                fontSize = 12.sp,
                modifier = Modifier.padding(top = 8.dp)
            )
        }
    }
}

@Composable
private fun NoPendingCartons(onClose: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            "No pending cartons",
            color = Color.White,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )
        Text(
            "All cartons have been counted",
            color = Color.Gray,
            fontSize = 14.sp,
            modifier = Modifier.padding(top = 8.dp)
        )
        Button(
            onClick = onClose,
            modifier = Modifier.padding(top = 24.dp)
        ) {
            Text("Done")
        }
    }
}


// ============================================================================
// BARCODE PROCESSING WITH ML KIT
// ============================================================================

private fun processImage(
    imageProxy: androidx.camera.core.ImageProxy,
    onBarcodeDetected: (String) -> Unit
) {
    try {
        val mediaImage = imageProxy.image ?: return
        val inputImage = InputImage.fromMediaImage(mediaImage, imageProxy.imageInfo.rotationDegrees)

        // ✅ ML Kit Barcode Scanner
        val options = BarcodeScannerOptions.Builder()
            .setBarcodeFormats(
                com.google.mlkit.vision.barcode.Barcode.FORMAT_QR_CODE,
                com.google.mlkit.vision.barcode.Barcode.FORMAT_CODE_128,
                com.google.mlkit.vision.barcode.Barcode.FORMAT_CODE_39,
                com.google.mlkit.vision.barcode.Barcode.FORMAT_EAN_13
            )
            .build()

        val scanner = BarcodeScanning.getClient(options)

        scanner.process(inputImage)
            .addOnSuccessListener { barcodes ->
                for (barcode in barcodes) {
                    val value = barcode.rawValue
                    if (!value.isNullOrEmpty()) {
                        onBarcodeDetected(value)
                        break
                    }
                }
            }
            .addOnFailureListener {
                // Scanning failed, retry
            }
    } catch (e: Exception) {
        // Error processing image
    }
}
