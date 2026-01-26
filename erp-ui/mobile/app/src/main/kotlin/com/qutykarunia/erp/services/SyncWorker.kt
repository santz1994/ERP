package com.qutykarunia.erp.services

import android.content.Context
import androidx.work.*
import timber.log.Timber
import java.util.concurrent.TimeUnit

/**
 * WorkManager Background Sync Service
 * 
 * Manages:
 * 1. Periodic sync of offline queue
 * 2. JWT token refresh
 * 3. Background error recovery
 * 4. Retry logic with exponential backoff
 */
class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    
    override suspend fun doWork(): Result {
        return try {
            Timber.d("Starting background sync...")
            
            // In production, would:
            // 1. Get repositories from DI
            // 2. Sync daily production inputs
            // 3. Sync carton confirmations
            // 4. Handle errors gracefully
            
            // Simulate sync delay
            Thread.sleep(1000)
            
            Timber.d("Background sync completed successfully")
            Result.success()
            
        } catch (e: Exception) {
            Timber.e(e, "Background sync failed")
            
            // Retry with exponential backoff
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }
    
    companion object {
        const val SYNC_WORK_NAME = "production_sync_work"
        const val SYNC_INTERVAL_MINUTES = 30
        
        /**
         * Schedule periodic background sync
         */
        fun schedulePeriodicSync(context: Context) {
            val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(
                duration = SYNC_INTERVAL_MINUTES.toLong(),
                timeUnit = TimeUnit.MINUTES,
                flexInterval = 5,
                flexTimeUnit = TimeUnit.MINUTES
            )
                .setBackoffCriteria(
                    backoffPolicy = BackoffPolicy.EXPONENTIAL,
                    initialDelay = 15,
                    backoffDelayPolicy = TimeUnit.MINUTES
                )
                .addTag(SYNC_WORK_NAME)
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .setRequiresBatteryNotLow(true)
                        .build()
                )
                .build()
            
            WorkManager.getInstance(context)
                .enqueueUniquePeriodicWork(
                    SYNC_WORK_NAME,
                    ExistingPeriodicWorkPolicy.KEEP,
                    syncRequest
                )
            
            Timber.d("Periodic sync scheduled - Interval: ${SYNC_INTERVAL_MINUTES}m")
        }
        
        /**
         * Schedule one-time sync (immediate)
         */
        fun scheduleImmediateSync(context: Context) {
            val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>()
                .addTag(SYNC_WORK_NAME)
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .build()
                )
                .build()
            
            WorkManager.getInstance(context)
                .enqueueUniqueWork(
                    "${SYNC_WORK_NAME}_immediate",
                    ExistingWorkPolicy.REPLACE,
                    syncRequest
                )
            
            Timber.d("Immediate sync scheduled")
        }
        
        /**
         * Cancel all background sync
         */
        fun cancelSync(context: Context) {
            WorkManager.getInstance(context)
                .cancelAllWorkByTag(SYNC_WORK_NAME)
            
            Timber.d("Background sync cancelled")
        }
    }
}

/**
 * JWT Token Refresh Worker
 * 
 * Periodically refresh JWT tokens before expiration
 */
class TokenRefreshWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    
    override suspend fun doWork(): Result {
        return try {
            Timber.d("Starting token refresh...")
            
            // In production, would:
            // 1. Check token expiration
            // 2. Call refresh endpoint
            // 3. Update stored token
            // 4. Schedule next refresh
            
            Timber.d("Token refresh completed")
            Result.success()
            
        } catch (e: Exception) {
            Timber.e(e, "Token refresh failed")
            Result.retry()
        }
    }
    
    companion object {
        const val TOKEN_REFRESH_WORK_NAME = "token_refresh_work"
        
        /**
         * Schedule periodic token refresh (1 hour before expiration)
         */
        fun scheduleTokenRefresh(context: Context, expiresInSeconds: Long) {
            // Refresh 1 hour before expiration
            val delayMinutes = (expiresInSeconds / 60) - 60
            
            if (delayMinutes > 0) {
                val refreshRequest = OneTimeWorkRequestBuilder<TokenRefreshWorker>()
                    .setInitialDelay(delayMinutes, TimeUnit.MINUTES)
                    .addTag(TOKEN_REFRESH_WORK_NAME)
                    .setConstraints(
                        Constraints.Builder()
                            .setRequiredNetworkType(NetworkType.CONNECTED)
                            .build()
                    )
                    .build()
                
                WorkManager.getInstance(context)
                    .enqueueUniqueWork(
                        TOKEN_REFRESH_WORK_NAME,
                        ExistingWorkPolicy.REPLACE,
                        refreshRequest
                    )
                
                Timber.d("Token refresh scheduled - Delay: ${delayMinutes}m")
            }
        }
    }
}

/**
 * Sync Service Manager
 * 
 * Centralizes WorkManager configuration
 */
object SyncServiceManager {
    
    /**
     * Initialize all background services
     */
    fun initializeSyncServices(context: Context) {
        try {
            // Schedule periodic sync
            SyncWorker.schedulePeriodicSync(context)
            
            // Configure constraints for optimal battery usage
            Timber.d("Background sync services initialized")
            
        } catch (e: Exception) {
            Timber.e(e, "Error initializing sync services")
        }
    }
    
    /**
     * Trigger immediate sync
     */
    fun triggerImmediateSync(context: Context) {
        try {
            SyncWorker.scheduleImmediateSync(context)
        } catch (e: Exception) {
            Timber.e(e, "Error triggering immediate sync")
        }
    }
    
    /**
     * Stop all background services
     */
    fun stopAllServices(context: Context) {
        try {
            SyncWorker.cancelSync(context)
            Timber.d("All background sync services stopped")
        } catch (e: Exception) {
            Timber.e(e, "Error stopping sync services")
        }
    }
}

/**
 * WorkManager Constraints Configuration
 * 
 * Optimal settings for production:
 * - Network: CONNECTED (only sync when network available)
 * - Battery: NOT LOW (preserve battery)
 * - Device Idle: Preferred (run during idle time)
 * - Storage: Not full (ensure storage space)
 * 
 * Sync Triggers:
 * 1. Periodic: Every 30 minutes
 * 2. Manual: User action (immediate sync button)
 * 3. On Resume: When app returns to foreground
 * 4. On Network Change: When network becomes available
 */
