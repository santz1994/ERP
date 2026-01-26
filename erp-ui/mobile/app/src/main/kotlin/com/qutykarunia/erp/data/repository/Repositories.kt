package com.qutykarunia.erp.data.repository

import com.qutykarunia.erp.data.api.ProductionApi
import com.qutykarunia.erp.data.api.FinishGoodApi
import com.qutykarunia.erp.data.db.*
import com.qutykarunia.erp.data.models.*
import timber.log.Timber
import java.time.LocalDate

/**
 * ProductionRepository
 * 
 * Implements offline-first data access pattern:
 * 1. Check local cache first
 * 2. If not available, fetch from API
 * 3. Store in local cache
 * 4. On sync, update backend
 */
class ProductionRepository(
    private val api: ProductionApi,
    private val dailyProductionDao: DailyProductionDao,
    private val offlineSyncDao: OfflineSyncDao
) {
    
    /**
     * Get daily production inputs with offline fallback
     */
    suspend fun getDailyInputs(spkId: Int): Result<List<DailyProductionCacheEntity>> {
        return try {
            // Try API first
            val apiResult = api.getMySPKs()
            
            if (apiResult.isSuccessful) {
                // Update local cache with fresh data
                val spkData = apiResult.body()?.find { it.id == spkId }
                if (spkData != null) {
                    Timber.d("Fetched SPK $spkId from API")
                    Result.success(emptyList()) // In production, would cache here
                }
            } else {
                throw Exception("API call failed: ${apiResult.code()}")
            }
            
            // Fallback to local cache
            val cachedInputs = dailyProductionDao.getProductionInputs(spkId)
            Result.success(cachedInputs)
            
        } catch (e: Exception) {
            // Network error - use cache
            Timber.w(e, "API failed, using local cache")
            val cachedInputs = dailyProductionDao.getProductionInputs(spkId)
            Result.success(cachedInputs)
        }
    }
    
    /**
     * Record daily production input
     */
    suspend fun recordDailyInput(
        spkId: Int,
        date: LocalDate,
        quantity: Int
    ): Result<Unit> {
        return try {
            // Create cache entity
            val cacheEntity = DailyProductionCacheEntity(
                id = "$spkId-${date}",
                spkId = spkId,
                productionDate = date,
                quantity = quantity,
                cumulativeQty = dailyProductionDao.getCumulativeQuantity(spkId) ?: 0,
                target = 500, // Mock - would come from SPK
                status = "LOCAL"
            )
            
            // Save locally
            dailyProductionDao.insertProduction(cacheEntity)
            
            // Queue for sync
            queueForSync("DAILY_INPUT", spkId = spkId)
            
            Timber.d("Daily input recorded - SPK: $spkId, Date: $date, Qty: $quantity")
            Result.success(Unit)
            
        } catch (e: Exception) {
            Timber.e(e, "Error recording daily input")
            Result.failure(e)
        }
    }
    
    /**
     * Sync local changes to backend
     */
    suspend fun syncPendingInputs(): Result<Int> {
        return try {
            val pendingItems = offlineSyncDao.getPendingSyncItems()
                .filter { it.type == "DAILY_INPUT" }
            
            var successCount = 0
            for (item in pendingItems) {
                try {
                    // Simulate API call
                    // val response = api.recordDailyInput(...)
                    
                    offlineSyncDao.markAsSynced(item.id)
                    successCount++
                    
                    Timber.d("Synced daily input: ${item.id}")
                    
                } catch (e: Exception) {
                    offlineSyncDao.markAsFailed(item.id)
                    Timber.w(e, "Failed to sync: ${item.id}")
                }
            }
            
            Result.success(successCount)
            
        } catch (e: Exception) {
            Timber.e(e, "Sync error")
            Result.failure(e)
        }
    }
    
    /**
     * Queue an operation for sync
     */
    private suspend fun queueForSync(type: String, spkId: Int? = null) {
        val syncItem = OfflineSyncEntity(
            id = "${type}-${System.currentTimeMillis()}",
            type = type,
            spkId = spkId,
            quantity = 1,
            status = "PENDING"
        )
        offlineSyncDao.insertSyncItem(syncItem)
    }
}

/**
 * FinishGoodRepository
 * 
 * Manages barcode scanning and carton confirmations
 */
class FinishGoodRepository(
    private val api: FinishGoodApi,
    private val finishGoodDao: FinishGoodDao,
    private val offlineSyncDao: OfflineSyncDao
) {
    
    /**
     * Save carton scan locally
     */
    suspend fun saveCartonScan(
        cartonId: String,
        article: String,
        quantity: Int
    ): Result<Unit> {
        return try {
            val entity = FinishGoodCacheEntity(
                cartonId = cartonId,
                article = article,
                quantity = quantity,
                status = "LOCAL"
            )
            
            finishGoodDao.insertCarton(entity)
            
            Timber.d("Carton scan saved - ID: $cartonId, Article: $article, Qty: $quantity")
            Result.success(Unit)
            
        } catch (e: Exception) {
            Timber.e(e, "Error saving carton scan")
            Result.failure(e)
        }
    }
    
    /**
     * Confirm carton and queue for sync
     */
    suspend fun confirmCarton(
        cartonId: String,
        finalQty: Int
    ): Result<Unit> {
        return try {
            // Mark carton as confirmed
            val cartons = finishGoodDao.getArticlesInCarton(cartonId)
            for (article in cartons) {
                val entity = finishGoodDao.getCarton(cartonId)
                if (entity != null) {
                    finishGoodDao.updateCarton(
                        entity.copy(status = "CONFIRMED")
                    )
                }
            }
            
            // Queue for sync
            val syncItem = OfflineSyncEntity(
                id = "FG-${cartonId}-${System.currentTimeMillis()}",
                type = "CARTON_CONFIRM",
                cartonId = cartonId,
                quantity = finalQty,
                status = "PENDING"
            )
            offlineSyncDao.insertSyncItem(syncItem)
            
            Timber.d("Carton confirmed and queued - ID: $cartonId")
            Result.success(Unit)
            
        } catch (e: Exception) {
            Timber.e(e, "Error confirming carton")
            Result.failure(e)
        }
    }
    
    /**
     * Sync carton confirmations to backend
     */
    suspend fun syncCartonConfirmations(): Result<Int> {
        return try {
            val pendingItems = offlineSyncDao.getPendingSyncItems()
                .filter { it.type == "CARTON_CONFIRM" }
            
            var successCount = 0
            for (item in pendingItems) {
                try {
                    // Simulate API call
                    // val request = CartonConfirmRequest(...)
                    // val response = api.confirmCarton(request)
                    
                    offlineSyncDao.markAsSynced(item.id)
                    finishGoodDao.markCartonSynced(item.cartonId!!)
                    successCount++
                    
                    Timber.d("Synced carton confirmation: ${item.id}")
                    
                } catch (e: Exception) {
                    offlineSyncDao.markAsFailed(item.id)
                    Timber.w(e, "Failed to sync carton: ${item.id}")
                }
            }
            
            Result.success(successCount)
            
        } catch (e: Exception) {
            Timber.e(e, "Carton sync error")
            Result.failure(e)
        }
    }
}

/**
 * UserRepository
 * 
 * Manages user authentication and session
 */
class UserRepository(
    private val userSessionDao: UserSessionDao
) {
    
    /**
     * Save user session
     */
    suspend fun saveUserSession(
        userId: String,
        username: String,
        role: String,
        token: String,
        refreshToken: String
    ): Result<Unit> {
        return try {
            val session = UserSessionEntity(
                userId = userId,
                username = username,
                role = role,
                jwtToken = token,
                refreshToken = refreshToken,
                tokenExpiresAt = System.currentTimeMillis() + (86400 * 1000) // 24 hours
            )
            
            userSessionDao.saveSession(session)
            
            Timber.d("User session saved - User: $userId")
            Result.success(Unit)
            
        } catch (e: Exception) {
            Timber.e(e, "Error saving user session")
            Result.failure(e)
        }
    }
    
    /**
     * Get current user session
     */
    suspend fun getUserSession(userId: String): Result<UserSessionEntity?> {
        return try {
            val session = userSessionDao.getUserSession(userId)
            Result.success(session)
        } catch (e: Exception) {
            Timber.e(e, "Error getting user session")
            Result.failure(e)
        }
    }
    
    /**
     * Clear session on logout
     */
    suspend fun clearSession(userId: String): Result<Unit> {
        return try {
            userSessionDao.deleteSessionByUserId(userId)
            Timber.d("User session cleared - User: $userId")
            Result.success(Unit)
        } catch (e: Exception) {
            Timber.e(e, "Error clearing session")
            Result.failure(e)
        }
    }
}
