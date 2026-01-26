package com.qutykarunia.erp.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ChevronLeft
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.qutykarunia.erp.viewmodel.DailyProductionViewModel
import java.time.LocalDate
import java.time.YearMonth
import java.time.format.DateTimeFormatter

/**
 * Daily Production Input Screen
 * 
 * Production workflow tracking:
 * 1. Calendar grid view (day-by-day)
 * 2. Daily quantity input
 * 3. Cumulative total calculation
 * 4. Progress percentage tracking
 * 5. Confirm completion workflow
 * 
 * Features:
 * - Navigate by month
 * - Edit any day's quantity
 * - Real-time progress calculation
 * - Target vs actual comparison
 * - "Confirm Selesai" button for completion
 */
@Composable
fun DailyProductionInputScreen(
    navController: NavController,
    viewModel: DailyProductionViewModel = hiltViewModel()
) {
    val state by viewModel.uiState.collectAsState()
    var currentMonth by remember { mutableStateOf(YearMonth.now()) }
    
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
            DailyProductionHeader(
                spkNumber = state.spkNumber,
                productName = state.productName,
                targetQty = state.targetQty
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Progress Summary
            ProgressSummaryCard(
                targetQty = state.targetQty,
                actualQty = state.totalQty,
                progressPct = state.progressPct,
                remainingQty = state.targetQty - state.totalQty,
                estimatedDaysRemaining = state.estimatedDaysRemaining
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Month Navigation
            MonthNavigationBar(
                currentMonth = currentMonth,
                onPrevMonth = { currentMonth = currentMonth.minusMonths(1) },
                onNextMonth = { currentMonth = currentMonth.plusMonths(1) }
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Calendar Grid
            CalendarGridView(
                month = currentMonth,
                dailyInputs = state.dailyInputs,
                onDateSelected = { date, quantity ->
                    viewModel.setDailyInput(date, quantity)
                }
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Action Buttons
            DailyProductionActionButtons(
                onConfirmCompletion = {
                    viewModel.confirmCompletion()
                },
                onSaveProgress = {
                    viewModel.saveProgress()
                },
                canConfirmCompletion = state.totalQty >= state.targetQty,
                isLoading = state.isLoading
            )
        }
    }
}

/**
 * Screen header with SPK information
 */
@Composable
private fun DailyProductionHeader(
    spkNumber: String,
    productName: String,
    targetQty: Int
) {
    Column {
        Text(
            text = "Daily Production Input",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )
        
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Column {
                Text(
                    text = "SPK: $spkNumber",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = productName,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Text(
                text = "Target: $targetQty pcs",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}

/**
 * Progress summary card showing target, actual, and percentage
 */
@Composable
private fun ProgressSummaryCard(
    targetQty: Int,
    actualQty: Int,
    progressPct: Float,
    remainingQty: Int,
    estimatedDaysRemaining: Int?
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
            // Progress percentage
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Progress: ${String.format("%.1f", progressPct * 100)}%",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
                
                // Visual progress bar
                LinearProgressIndicator(
                    progress = { progressPct.coerceIn(0f, 1f) },
                    modifier = Modifier
                        .weight(1f)
                        .padding(start = 16.dp)
                        .height(8.dp),
                    color = MaterialTheme.colorScheme.secondary
                )
            }
            
            // Quantity details
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                ProgressDetail(
                    label = "Actual",
                    value = "$actualQty pcs",
                    color = MaterialTheme.colorScheme.secondary
                )
                
                ProgressDetail(
                    label = "Target",
                    value = "$targetQty pcs",
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
                
                ProgressDetail(
                    label = "Remaining",
                    value = "$remainingQty pcs",
                    color = if (remainingQty > 0)
                        MaterialTheme.colorScheme.error
                    else
                        MaterialTheme.colorScheme.tertiary
                )
                
                if (estimatedDaysRemaining != null && estimatedDaysRemaining > 0) {
                    ProgressDetail(
                        label = "Est. Days",
                        value = "$estimatedDaysRemaining",
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
            }
        }
    }
}

/**
 * Progress detail chip
 */
@Composable
private fun ProgressDetail(
    label: String,
    value: String,
    color: androidx.compose.ui.graphics.Color
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
        )
        Text(
            text = value,
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.Bold,
            color = color
        )
    }
}

/**
 * Month navigation controls
 */
@Composable
private fun MonthNavigationBar(
    currentMonth: YearMonth,
    onPrevMonth: () -> Unit,
    onNextMonth: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        IconButton(onClick = onPrevMonth) {
            Icon(
                imageVector = Icons.Default.ChevronLeft,
                contentDescription = "Previous month",
                tint = MaterialTheme.colorScheme.primary
            )
        }
        
        Text(
            text = currentMonth.format(DateTimeFormatter.ofPattern("MMMM yyyy")),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary,
            modifier = Modifier.weight(1f),
            textAlign = TextAlign.Center
        )
        
        IconButton(onClick = onNextMonth) {
            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = "Next month",
                tint = MaterialTheme.colorScheme.primary
            )
        }
    }
}

/**
 * Calendar grid with day-by-day input cells
 */
@Composable
private fun CalendarGridView(
    month: YearMonth,
    dailyInputs: Map<LocalDate, Int>,
    onDateSelected: (LocalDate, Int) -> Unit
) {
    val firstDay = month.atDay(1)
    val daysInMonth = month.lengthOfMonth()
    val firstDayOfWeek = firstDay.dayOfWeek.value % 7 // Sunday = 0
    
    // Week headers
    val weekDays = listOf("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
    
    LazyColumn(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                color = MaterialTheme.colorScheme.surface,
                shape = MaterialTheme.shapes.medium
            )
            .border(
                width = 1.dp,
                color = MaterialTheme.colorScheme.outline,
                shape = MaterialTheme.shapes.medium
            )
            .padding(8.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        // Week day headers
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                weekDays.forEach { day ->
                    Text(
                        text = day,
                        modifier = Modifier
                            .weight(1f)
                            .padding(4.dp),
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Bold,
                        textAlign = TextAlign.Center,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }
        }
        
        // Calendar days
        val weeks = mutableListOf<List<LocalDate?>>()\n        var currentWeek = mutableListOf<LocalDate?>()\n        \n        // Add empty days before month starts\n        repeat(firstDayOfWeek) {\n            currentWeek.add(null)\n        }\n        \n        // Add days of month\n        for (day in 1..daysInMonth) {\n            val date = month.atDay(day)\n            currentWeek.add(date)\n            \n            if (currentWeek.size == 7) {\n                weeks.add(currentWeek.toList())\n                currentWeek = mutableListOf()\n            }\n        }\n        \n        // Add remaining days if any\n        if (currentWeek.isNotEmpty()) {\n            while (currentWeek.size < 7) {\n                currentWeek.add(null)\n            }\n            weeks.add(currentWeek.toList())\n        }\n        \n        items(weeks) { week ->\n            Row(\n                modifier = Modifier.fillMaxWidth(),\n                horizontalArrangement = Arrangement.spacedBy(4.dp)\n            ) {\n                week.forEach { date ->\n                    if (date != null) {\n                        val quantity = dailyInputs[date] ?: 0\n                        CalendarDayCell(\n                            date = date,\n                            quantity = quantity,\n                            onQuantityChange = { newQty ->\n                                onDateSelected(date, newQty)\n                            }\n                        )\n                    } else {\n                        Spacer(modifier = Modifier.weight(1f).height(60.dp))\n                    }\n                }\n            }\n        }\n    }\n}\n\n/**\n * Individual calendar day cell with quantity input\n */\n@Composable\nprivate fun CalendarDayCell(\n    date: LocalDate,\n    quantity: Int,\n    onQuantityChange: (Int) -> Unit\n) {\n    var isEditing by remember { mutableStateOf(false) }\n    var editValue by remember { mutableStateOf(quantity.toString()) }\n    \n    Box(\n        modifier = Modifier\n            .weight(1f)\n            .background(\n                color = if (quantity > 0)\n                    MaterialTheme.colorScheme.tertiary.copy(alpha = 0.2f)\n                else\n                    MaterialTheme.colorScheme.surface,\n                shape = MaterialTheme.shapes.small\n            )\n            .border(\n                width = 1.dp,\n                color = if (quantity > 0)\n                    MaterialTheme.colorScheme.tertiary\n                else\n                    MaterialTheme.colorScheme.outlineVariant,\n                shape = MaterialTheme.shapes.small\n            )\n            .padding(4.dp)\n    ) {\n        Column(\n            modifier = Modifier\n                .fillMaxWidth()\n                .padding(4.dp),\n            horizontalAlignment = Alignment.CenterHorizontally\n        ) {\n            // Day number\n            Text(\n                text = date.dayOfMonth.toString(),\n                style = MaterialTheme.typography.labelSmall,\n                fontWeight = FontWeight.Bold,\n                color = MaterialTheme.colorScheme.onSurface\n            )\n            \n            // Quantity display/edit\n            if (isEditing) {\n                OutlinedTextField(\n                    value = editValue,\n                    onValueChange = { editValue = it },\n                    modifier = Modifier\n                        .width(50.dp)\n                        .height(36.dp),\n                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),\n                    textStyle = MaterialTheme.typography.labelSmall.copy(textAlign = TextAlign.Center),\n                    singleLine = true\n                )\n            } else {\n                Text(\n                    text = quantity.toString(),\n                    style = MaterialTheme.typography.titleSmall,\n                    fontWeight = FontWeight.Bold,\n                    color = if (quantity > 0)\n                        MaterialTheme.colorScheme.tertiary\n                    else\n                        MaterialTheme.colorScheme.onSurfaceVariant\n                )\n            }\n        }\n    }\n}\n\n/**\n * Action buttons for daily production workflow\n */\n@Composable\nprivate fun DailyProductionActionButtons(\n    onConfirmCompletion: () -> Unit,\n    onSaveProgress: () -> Unit,\n    canConfirmCompletion: Boolean,\n    isLoading: Boolean\n) {\n    Column(\n        modifier = Modifier\n            .fillMaxWidth()\n            .padding(8.dp),\n        verticalArrangement = Arrangement.spacedBy(8.dp)\n    ) {\n        // Save Progress Button\n        Button(\n            onClick = onSaveProgress,\n            modifier = Modifier\n                .fillMaxWidth()\n                .height(48.dp),\n            enabled = !isLoading\n        ) {\n            if (isLoading) {\n                CircularProgressIndicator(\n                    modifier = Modifier.size(20.dp),\n                    color = MaterialTheme.colorScheme.onPrimary\n                )\n            } else {\n                Text(\"Save Progress\")\n            }\n        }\n        \n        // Confirm Completion Button (only if target reached)\n        if (canConfirmCompletion) {\n            Button(\n                onClick = onConfirmCompletion,\n                modifier = Modifier\n                    .fillMaxWidth()\n                    .height(48.dp),\n                enabled = !isLoading,\n                colors = ButtonDefaults.buttonColors(\n                    containerColor = MaterialTheme.colorScheme.tertiary\n                )\n            ) {\n                Text(\"Confirm Selesai\")\n            }\n        }\n    }\n}\n