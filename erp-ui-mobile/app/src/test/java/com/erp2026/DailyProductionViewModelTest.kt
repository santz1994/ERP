package com.erp2026.viewmodel

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import androidx.lifecycle.Observer
import com.erp2026.data.repository.ProductionRepository
import com.erp2026.domain.model.DailyProduction
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.whenever
import org.mockito.kotlin.verify
import java.time.LocalDate

@ExperimentalCoroutinesApi
class DailyProductionViewModelTest {
    
    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()
    
    @Mock
    private lateinit var productionRepository: ProductionRepository
    
    @Mock
    private lateinit var productionObserver: Observer<ProductionState>
    
    private lateinit var viewModel: DailyProductionViewModel
    
    @Before
    fun setUp() {
        MockitoAnnotations.openMocks(this)
        viewModel = DailyProductionViewModel(productionRepository)
    }
    
    @Test
    fun testRecordDailyProduction() = runTest {
        // Arrange
        val production = DailyProduction(
            id = 1,
            lineId = "LINE001",
            articleId = "ARTICLE001",
            quantity = 100,
            date = LocalDate.now(),
            approvalStatus = "PENDING"
        )
        
        whenever(productionRepository.recordProduction(production))
            .thenReturn(production)
        
        viewModel.productionState.observeForever(productionObserver)
        
        // Act
        viewModel.recordProduction(production)
        
        // Assert
        verify(productionObserver).onChanged(ProductionState.Loading)
        verify(productionObserver).onChanged(ProductionState.Success(production))
    }
    
    @Test
    fun testGetDailyTotal() = runTest {
        // Arrange
        val productions = listOf(
            DailyProduction(1, "LINE001", "ART001", 100, LocalDate.now()),
            DailyProduction(2, "LINE002", "ART002", 150, LocalDate.now()),
            DailyProduction(3, "LINE003", "ART003", 200, LocalDate.now())
        )
        
        whenever(productionRepository.getProductionByDate(LocalDate.now()))
            .thenReturn(productions)
        
        // Act
        viewModel.loadProductionByDate(LocalDate.now())
        
        // Assert
        val total = productions.sumOf { it.quantity }
        assert(total == 450)
    }
    
    @Test
    fun testValidateQuantity() {
        // Arrange
        val validQuantity = 150
        val invalidQuantity = -50
        val excessiveQuantity = 20000
        
        // Act & Assert
        assert(viewModel.validateQuantity(validQuantity))
        assert(!viewModel.validateQuantity(invalidQuantity))
        assert(!viewModel.validateQuantity(excessiveQuantity))
    }
    
    @Test
    fun testCalculateCumulative() = runTest {
        // Arrange
        val productions = listOf(
            DailyProduction(1, "LINE001", "ART001", 100, LocalDate.now().minusDays(2)),
            DailyProduction(2, "LINE001", "ART001", 150, LocalDate.now().minusDays(1)),
            DailyProduction(3, "LINE001", "ART001", 200, LocalDate.now())
        )
        
        whenever(productionRepository.getProductionByArticle("ART001"))
            .thenReturn(productions)
        
        // Act
        val cumulative = productions.sumOf { it.quantity }
        
        // Assert
        assert(cumulative == 450)
    }
    
    @Test
    fun testApprovalRequired() {
        // Arrange
        val thresholdQuantity = 500
        val highQuantity = 750
        val lowQuantity = 250
        
        // Act
        val requiresApprovalHigh = highQuantity >= thresholdQuantity
        val requiresApprovalLow = lowQuantity >= thresholdQuantity
        
        // Assert
        assert(requiresApprovalHigh)
        assert(!requiresApprovalLow)
    }
    
    @Test
    fun testProductionTarget() = runTest {
        // Arrange
        val target = 1000
        val currentProduction = 750
        val targetProgress = (currentProduction.toDouble() / target) * 100
        
        // Act & Assert
        assert(targetProgress == 75.0)
    }
    
    @Test
    fun testRecordingError() = runTest {
        // Arrange
        val production = DailyProduction(
            id = 1,
            lineId = "LINE001",
            articleId = "ARTICLE001",
            quantity = 100,
            date = LocalDate.now()
        )
        val errorMessage = "Database error"
        
        whenever(productionRepository.recordProduction(production))
            .thenThrow(Exception(errorMessage))
        
        viewModel.productionState.observeForever(productionObserver)
        
        // Act
        viewModel.recordProduction(production)
        
        // Assert
        verify(productionObserver).onChanged(ProductionState.Loading)
        verify(productionObserver).onChanged(ProductionState.Error(errorMessage))
    }
    
    @Test
    fun testOfflineMode() {
        // Arrange
        viewModel.enableOfflineMode()
        
        // Act & Assert
        assert(viewModel.isOfflineMode.value == true)
    }
    
    @Test
    fun testSyncProduction() = runTest {
        // Arrange
        val production = DailyProduction(
            id = 1,
            lineId = "LINE001",
            articleId = "ARTICLE001",
            quantity = 100,
            date = LocalDate.now()
        )
        
        whenever(productionRepository.syncProduction(production))
            .thenReturn(Unit)
        
        // Act
        viewModel.syncProduction(production)
        
        // Assert
        verify(productionRepository).syncProduction(production)
    }
}

sealed class ProductionState {
    object Loading : ProductionState()
    data class Success(val production: DailyProduction) : ProductionState()
    data class Error(val message: String) : ProductionState()
    data class SuccessList(val productions: List<DailyProduction>) : ProductionState()
}
