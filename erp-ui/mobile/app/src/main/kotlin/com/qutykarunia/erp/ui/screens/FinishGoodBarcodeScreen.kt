package com.qutykarunia.erp.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.google.mlkit.vision.barcode.common.Barcode
import com.qutykarunia.erp.ui.components.BarcodeScanner
import com.qutykarunia.erp.viewmodel.FinishGoodViewModel
import com.qutykarunia.erp.data.models.ScannedBarcode

/**
 * FinishGood Barcode Screen
 * 
 * Core production workflow:
 * 1. Scan carton QR code / barcode
 * 2. Count items per article
 * 3. Confirm per-article quantities
 * 4. Complete shipment
 * 
 * Supported formats:
 * - QR Code (primary) - contains carton ID
 * - Code128 (backup) - carton barcode
 * - EAN-13 (labels) - item identifier
 * - Code39 (alternative) - carton ID
 */
@Composable
fun FinishGoodBarcodeScreen(
    navController: NavController,
    viewModel: FinishGoodViewModel = hiltViewModel()
) {
    val state by viewModel.uiState.collectAsState()
    var showScanner by remember { mutableStateOf(true) }
    
    Surface(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background),
        color = MaterialTheme.colorScheme.background
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
        ) {
            // Header
            FinishGoodHeader()
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Current Carton Status
            if (state.currentCarton != null) {
                CurrentCartonCard(
                    carton = state.currentCarton!!,
                    totalScanned = state.scannedItems.size
                )
                Spacer(modifier = Modifier.height(16.dp))
            }
            
            // Scanner or Content
            if (showScanner && state.currentCarton == null) {
                // Barcode Scanner
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(300.dp)
                        .border(
                            width = 2.dp,
                            color = MaterialTheme.colorScheme.primary,
                            shape = MaterialTheme.shapes.medium
                        )
                        .background(
                            color = Color.Black.copy(alpha = 0.1f),
                            shape = MaterialTheme.shapes.medium
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    BarcodeScanner(
                        onBarcodeScanned = { barcode ->
                            viewModel.onBarcodeScanned(barcode)
                            showScanner = false
                        },
                        onError = { error ->
                            viewModel.onScanError(error)
                        }
                    )
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Scan Instruction
                Text(
                    text = "Scan carton barcode / QR code",
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )
            } else if (state.currentCarton != null) {
                // Article Count Grid
                LazyColumn(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(state.scannedItems) { item ->
                        ArticleCountRow(
                            article = item.article,
                            count = item.count,
                            onIncrement = { viewModel.incrementCount(item.article) },
                            onDecrement = { viewModel.decrementCount(item.article) },
                            onQuantityChange = { viewModel.setQuantity(item.article, it) }
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Action Buttons
            FinishGoodActionButtons(
                onAddArticle = {
                    showScanner = true
                },
                onConfirmCarton = {
                    viewModel.confirmCarton()
                },
                onCancel = {
                    viewModel.cancelCarton()
                    showScanner = true
                },
                isLoading = state.isLoading,
                canConfirm = state.scannedItems.isNotEmpty(),
                currentCartonNull = state.currentCarton == null
            )
        }
    }
}

/**
 * Header with shipment and carton info
 */
@Composable
private fun FinishGoodHeader() {
    Text(
        text = "FinishGood Barcode Scanning",
        modifier = Modifier.fillMaxWidth(),
        style = MaterialTheme.typography.headlineSmall,
        fontWeight = FontWeight.Bold,
        color = MaterialTheme.colorScheme.primary
    )
    
    Text(
        text = "Count items per article | Scan barcodes",
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 4.dp),
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant
    )
}

/**
 * Current carton information card
 */
@Composable
private fun CurrentCartonCard(
    carton: String,
    totalScanned: Int
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp),
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
                        text = "Carton ID",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                    Text(
                        text = carton,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
                
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = "Total Scanned",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                    Text(
                        text = totalScanned.toString(),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
            }
        }
    }
}

/**
 * Article count row with +/- buttons
 */
@Composable
private fun ArticleCountRow(
    article: String,
    count: Int,
    onIncrement: () -> Unit,
    onDecrement: () -> Unit,
    onQuantityChange: (Int) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
            .background(
                color = MaterialTheme.colorScheme.surfaceVariant,
                shape = MaterialTheme.shapes.small
            )
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = article,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.onSurface
            )
        }
        
        // Count Controls
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            IconButton(
                onClick = onDecrement,
                modifier = Modifier.size(32.dp)
            ) {
                Text("-", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
            
            Text(
                text = count.toString(),
                modifier = Modifier
                    .width(48.dp)
                    .padding(8.dp),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                color = MaterialTheme.colorScheme.primary
            )
            
            IconButton(
                onClick = onIncrement,
                modifier = Modifier.size(32.dp)
            ) {
                Text("+", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

/**
 * Action buttons for carton workflow
 */
@Composable
private fun FinishGoodActionButtons(
    onAddArticle: () -> Unit,
    onConfirmCarton: () -> Unit,
    onCancel: () -> Unit,
    isLoading: Boolean,
    canConfirm: Boolean,
    currentCartonNull: Boolean
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        if (currentCartonNull) {
            // Only show when no carton is loaded
            Button(
                onClick = onAddArticle,
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp),
                enabled = !isLoading
            ) {
                Text("Scan Carton")
            }
        } else {
            // Show when carton is loaded
            OutlinedButton(
                onClick = onCancel,
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp),
                enabled = !isLoading
            ) {
                Text("Cancel")
            }
            
            Button(
                onClick = onConfirmCarton,
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp),
                enabled = !isLoading && canConfirm
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                } else {
                    Text("Confirm Carton")
                }
            }
        }
    }
}
