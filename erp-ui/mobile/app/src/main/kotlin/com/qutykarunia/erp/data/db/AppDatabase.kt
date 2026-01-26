package com.qutykarunia.erp.data.db

import androidx.room.*
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase
import com.qutykarunia.erp.data.models.*

/**
 * AppDatabase - Room Database Setup
 * 
 * Manages:
 * 1. Offline sync queue
 * 2. Daily production cache
 * 3. FinishGood cache
 * 4. User session data
 * 5. Database migrations
 */
@Database(
    entities = [
        OfflineSyncEntity::class,
        DailyProductionCacheEntity::class,
        FinishGoodCacheEntity::class,
        UserSessionEntity::class
    ],
    version = 1,
    exportSchema = true
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    
    // DAOs
    abstract fun offlineSyncDao(): OfflineSyncDao
    abstract fun dailyProductionDao(): DailyProductionDao
    abstract fun finishGoodDao(): FinishGoodDao
    abstract fun userSessionDao(): UserSessionDao
    
    companion object {
        const val DATABASE_NAME = "erp_app_db"
    }
}

/**
 * Type Converters for LocalDate and other complex types
 */
class Converters {
    @TypeConverter
    fun fromLocalDate(date: java.time.LocalDate?): String? {
        return date?.toString()
    }

    @TypeConverter
    fun toLocalDate(dateString: String?): java.time.LocalDate? {
        return dateString?.let { java.time.LocalDate.parse(it) }
    }

    @TypeConverter
    fun fromMap(map: Map<java.time.LocalDate, Int>?): String? {
        return map?.let { m ->
            m.entries.joinToString(";") { "${it.key}:${it.value}" }
        }
    }

    @TypeConverter
    fun toMap(value: String?): Map<java.time.LocalDate, Int>? {
        return value?.split(";")?.associate { entry ->
            val (date, qty) = entry.split(":")
            java.time.LocalDate.parse(date) to qty.toInt()
        }
    }
}

/**
 * DAO - Offline Sync Queue
 * 
 * Manages queued operations for offline-first sync
 */
@Dao
interface OfflineSyncDao {
    
    @Query("SELECT * FROM offline_sync_queue WHERE status = 'PENDING' ORDER BY createdAt ASC")
    suspend fun getPendingSyncItems(): List<OfflineSyncEntity>
    
    @Query("SELECT * FROM offline_sync_queue WHERE id = :id")
    suspend fun getSyncItem(id: String): OfflineSyncEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSyncItem(item: OfflineSyncEntity)
    
    @Update
    suspend fun updateSyncItem(item: OfflineSyncEntity)
    
    @Query("UPDATE offline_sync_queue SET status = 'SYNCED' WHERE id = :id")
    suspend fun markAsSynced(id: String)
    
    @Query("UPDATE offline_sync_queue SET status = 'FAILED', retryCount = retryCount + 1 WHERE id = :id")
    suspend fun markAsFailed(id: String)
    
    @Delete
    suspend fun deleteSyncItem(item: OfflineSyncEntity)
    
    @Query("DELETE FROM offline_sync_queue WHERE status = 'SYNCED' AND updatedAt < :oldThreshold")
    suspend fun deleteSyncedOlderThan(oldThreshold: Long)
    
    @Query("SELECT COUNT(*) FROM offline_sync_queue WHERE status = 'PENDING'")
    suspend fun getPendingCount(): Int
}

/**
 * DAO - Daily Production Cache
 * 
 * Caches daily production inputs for offline access
 */
@Dao
interface DailyProductionDao {
    
    @Query("SELECT * FROM daily_production_cache WHERE spkId = :spkId ORDER BY productionDate DESC")
    suspend fun getProductionInputs(spkId: Int): List<DailyProductionCacheEntity>
    
    @Query("SELECT * FROM daily_production_cache WHERE spkId = :spkId AND productionDate = :date")
    suspend fun getProductionForDate(spkId: Int, date: java.time.LocalDate): DailyProductionCacheEntity?
    
    @Query("SELECT SUM(quantity) FROM daily_production_cache WHERE spkId = :spkId AND status != 'ERROR'")
    suspend fun getCumulativeQuantity(spkId: Int): Int?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProduction(entity: DailyProductionCacheEntity)
    
    @Update
    suspend fun updateProduction(entity: DailyProductionCacheEntity)
    
    @Delete
    suspend fun deleteProduction(entity: DailyProductionCacheEntity)
    
    @Query("DELETE FROM daily_production_cache WHERE spkId = :spkId AND status = 'SYNCED'")
    suspend fun deleteSyncedProduction(spkId: Int)
    
    @Query("SELECT COUNT(*) FROM daily_production_cache WHERE status = 'LOCAL'")
    suspend fun getUnSyncedCount(): Int
}

/**
 * DAO - FinishGood Cache
 * 
 * Caches barcode scans and carton confirmations
 */
@Dao
interface FinishGoodDao {
    
    @Query("SELECT * FROM finish_good_cache WHERE status = 'LOCAL' ORDER BY createdAt DESC")
    suspend fun getUnSyncedCartons(): List<FinishGoodCacheEntity>
    
    @Query("SELECT * FROM finish_good_cache WHERE cartonId = :cartonId")
    suspend fun getCarton(cartonId: String): FinishGoodCacheEntity?
    
    @Query("SELECT DISTINCT article FROM finish_good_cache WHERE cartonId = :cartonId")
    suspend fun getArticlesInCarton(cartonId: String): List<String>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCarton(entity: FinishGoodCacheEntity)
    
    @Update
    suspend fun updateCarton(entity: FinishGoodCacheEntity)
    
    @Delete
    suspend fun deleteCarton(entity: FinishGoodCacheEntity)
    
    @Query("UPDATE finish_good_cache SET status = 'SYNCED' WHERE cartonId = :cartonId")
    suspend fun markCartonSynced(cartonId: String)
    
    @Query("DELETE FROM finish_good_cache WHERE status = 'SYNCED'")
    suspend fun deleteSyncedCartons()
}

/**
 * DAO - User Session
 * 
 * Manages user session and authentication data
 */
@Dao
interface UserSessionDao {
    
    @Query("SELECT * FROM user_session WHERE userId = :userId")
    suspend fun getUserSession(userId: String): UserSessionEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun saveSession(entity: UserSessionEntity)
    
    @Delete
    suspend fun deleteSession(entity: UserSessionEntity)
    
    @Query("DELETE FROM user_session WHERE userId = :userId")
    suspend fun deleteSessionByUserId(userId: String)
    
    @Query("DELETE FROM user_session")
    suspend fun deleteAllSessions()
}

/**
 * Database Migrations (for schema updates)
 * 
 * Currently: version 1 (no migrations needed yet)
 * 
 * Example migration for future use:
 * val MIGRATION_1_2 = object : Migration(1, 2) {
 *     override fun migrate(database: SupportSQLiteDatabase) {
 *         database.execSQL("ALTER TABLE offline_sync_queue ADD COLUMN failureReason TEXT")
 *     }
 * }
 */
