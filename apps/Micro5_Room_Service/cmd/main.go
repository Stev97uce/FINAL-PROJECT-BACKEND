package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/stev97uce/room-service/internal/events"
	"github.com/stev97uce/room-service/internal/handlers"
	"github.com/stev97uce/room-service/internal/middleware"
	"github.com/stev97uce/room-service/internal/repository"
	"github.com/stev97uce/room-service/internal/services"
	"github.com/stev97uce/room-service/pkg/config"
	"github.com/stev97uce/room-service/pkg/database"
)

func main() {
	// Load configuration
	if err := config.LoadConfig(); err != nil {
		log.Fatal("Failed to load configuration:", err)
	}

	// Initialize databases
	if err := database.InitPostgreSQL(); err != nil {
		log.Fatal("Failed to initialize PostgreSQL:", err)
	}

	if err := database.InitRedis(); err != nil {
		log.Fatal("Failed to initialize Redis:", err)
	}

	// Initialize RabbitMQ
	publisher, err := events.NewRabbitMQPublisher()
	if err != nil {
		log.Fatal("Failed to initialize RabbitMQ:", err)
	}
	defer publisher.Close()

	// Initialize repositories
	roomRepo := repository.NewRoomRepository(database.DB)
	scheduleRepo := repository.NewScheduleRepository(database.DB)

	// Initialize services
	roomService := services.NewRoomService(roomRepo, scheduleRepo)
	scheduleService := services.NewScheduleService(scheduleRepo, roomRepo)

	// Initialize handlers
	roomHandler := handlers.NewRoomHandler(roomService)
	scheduleHandler := handlers.NewScheduleHandler(scheduleService)

	// Setup Gin router
	if !config.AppConfig.Debug {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.New()
	router.Use(gin.Recovery())
	router.Use(middleware.Logger())

	// CORS configuration
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:3000", "http://localhost:5173"},
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// Health check endpoints
	router.GET("/health", func(c *gin.Context) {
		ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
		defer cancel()

		if err := database.HealthCheck(ctx); err != nil {
			c.JSON(http.StatusServiceUnavailable, gin.H{
				"status":  "unhealthy",
				"service": config.AppConfig.AppName,
				"version": config.AppConfig.AppVersion,
				"error":   err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"service": config.AppConfig.AppName,
			"version": config.AppConfig.AppVersion,
		})
	})

	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Room Service API",
			"version": config.AppConfig.AppVersion,
		})
	})

	// API v1 routes
	v1 := router.Group("/api/v1")

	// Room routes (protected)
	rooms := v1.Group("/rooms")
	rooms.Use(middleware.AuthMiddleware())
	{
		// Public read operations
		rooms.GET("/", roomHandler.ListRooms)
		rooms.GET("/available", roomHandler.FindAvailableRooms)
		rooms.GET("/:id", roomHandler.GetRoom)

		// Admin/coordinator operations
		rooms.POST("/", middleware.RequireRole("admin", "coordinador"), roomHandler.CreateRoom)
		rooms.PUT("/:id", middleware.RequireRole("admin", "coordinador"), roomHandler.UpdateRoom)
		rooms.DELETE("/:id", middleware.RequireRole("admin", "coordinador"), roomHandler.DeleteRoom)
		rooms.PATCH("/:id/status", middleware.RequireRole("admin", "coordinador", "recepcionista"), roomHandler.UpdateRoomStatus)

		// Room schedules
		rooms.GET("/:id/schedule", scheduleHandler.GetRoomSchedules)
	}

	// Schedule routes (protected)
	schedules := v1.Group("/schedules")
	schedules.Use(middleware.AuthMiddleware())
	{
		schedules.GET("/", scheduleHandler.ListSchedules)
		schedules.GET("/:id", scheduleHandler.GetSchedule)
		schedules.POST("/", middleware.RequireRole("recepcionista", "coordinador", "admin"), scheduleHandler.CreateSchedule)
		schedules.PUT("/:id", middleware.RequireRole("recepcionista", "coordinador", "admin"), scheduleHandler.UpdateSchedule)
		schedules.DELETE("/:id", middleware.RequireRole("coordinador", "admin"), scheduleHandler.DeleteSchedule)
	}

	// Start server
	srv := &http.Server{
		Addr:    ":" + config.AppConfig.Port,
		Handler: router,
	}

	// Graceful shutdown
	go func() {
		log.Printf("Starting %s v%s on port %s", config.AppConfig.AppName, config.AppConfig.AppVersion, config.AppConfig.Port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal("Failed to start server:", err)
		}
	}()

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("Server forced to shutdown:", err)
	}

	// Close database connections
	if err := database.CloseDB(); err != nil {
		log.Println("Error closing database connections:", err)
	}

	log.Println("Server exited")
}
