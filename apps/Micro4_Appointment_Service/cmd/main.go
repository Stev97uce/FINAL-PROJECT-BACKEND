package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/stev97uce/appointment-service/internal/events"
	"github.com/stev97uce/appointment-service/internal/handlers"
	"github.com/stev97uce/appointment-service/internal/middleware"
	"github.com/stev97uce/appointment-service/internal/models"
	"github.com/stev97uce/appointment-service/internal/repository"
	"github.com/stev97uce/appointment-service/internal/services"
	"github.com/stev97uce/appointment-service/pkg/config"
	"github.com/stev97uce/appointment-service/pkg/database"
)

func main() {
	// Load configuration
	cfg := config.LoadConfig()

	// Initialize databases
	if err := database.InitPostgreSQL(cfg); err != nil {
		log.Fatalf("Failed to initialize PostgreSQL: %v", err)
	}
	defer database.CloseConnections()

	if err := database.InitRedis(cfg); err != nil {
		log.Fatalf("Failed to initialize Redis: %v", err)
	}

	// Auto-migrate database models
	if err := database.DB.AutoMigrate(&models.Appointment{}, &models.Availability{}); err != nil {
		log.Fatalf("Failed to migrate database: %v", err)
	}
	log.Println("Database migrations completed")

	// Initialize RabbitMQ
	rabbitMQ := events.NewRabbitMQPublisher(cfg)
	if err := rabbitMQ.Connect(); err != nil {
		log.Printf("Warning: Failed to connect to RabbitMQ: %v", err)
	} else {
		defer rabbitMQ.Close()
	}

	// Initialize repositories
	appointmentRepo := repository.NewAppointmentRepository(database.DB)
	availabilityRepo := repository.NewAvailabilityRepository(database.DB)

	// Initialize services
	appointmentService := services.NewAppointmentService(appointmentRepo)
	availabilityService := services.NewAvailabilityService(availabilityRepo, appointmentRepo)

	// Initialize handlers
	appointmentHandler := handlers.NewAppointmentHandler(appointmentService)
	availabilityHandler := handlers.NewAvailabilityHandler(availabilityService)

	// Setup Gin router
	if !cfg.Debug {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.Default()

	// CORS middleware
	corsOrigins := strings.Split(cfg.CORSOrigins, ",")
	router.Use(cors.New(cors.Config{
		AllowOrigins:     corsOrigins,
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// Custom logger middleware
	router.Use(middleware.LoggerMiddleware())

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"service": cfg.AppName,
			"version": cfg.AppVersion,
		})
	})

	// Root endpoint
	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Appointment Service API",
			"version": cfg.AppVersion,
		})
	})

	// API v1 routes
	v1 := router.Group("/api/v1")
	{
		// Appointment routes (protected)
		appointments := v1.Group("/appointments")
		appointments.Use(middleware.AuthMiddleware())
		{
			appointments.POST("/", middleware.RequireRole("recepcionista", "coordinador", "admin"), appointmentHandler.CreateAppointment)
			appointments.GET("/", appointmentHandler.ListAppointments)
			appointments.GET("/:id", appointmentHandler.GetAppointment)
			appointments.PATCH("/:id", middleware.RequireRole("recepcionista", "coordinador", "admin"), appointmentHandler.UpdateAppointment)
			appointments.DELETE("/:id", middleware.RequireRole("recepcionista", "coordinador", "admin"), appointmentHandler.CancelAppointment)
			appointments.POST("/:id/confirm", middleware.RequireRole("recepcionista", "coordinador", "admin"), appointmentHandler.ConfirmAppointment)
			appointments.POST("/:id/complete", middleware.RequireRole("profesional", "estudiante", "coordinador", "admin"), appointmentHandler.CompleteAppointment)
			appointments.POST("/:id/no-show", middleware.RequireRole("recepcionista", "coordinador", "admin"), appointmentHandler.MarkNoShow)
		}

		// Availability routes (protected)
		availability := v1.Group("/availability")
		availability.Use(middleware.AuthMiddleware())
		{
			availability.GET("/slots", availabilityHandler.FindAvailableSlots)
			availability.GET("/", availabilityHandler.ListByProfessional)
			availability.GET("/:id", availabilityHandler.GetAvailability)
			availability.POST("/", middleware.RequireRole("coordinador", "admin"), availabilityHandler.CreateAvailability)
			availability.PUT("/:id", middleware.RequireRole("coordinador", "admin"), availabilityHandler.UpdateAvailability)
			availability.DELETE("/:id", middleware.RequireRole("coordinador", "admin"), availabilityHandler.DeleteAvailability)
		}

		// Calendar routes (protected)
		calendar := v1.Group("/calendar")
		calendar.Use(middleware.AuthMiddleware())
		{
			calendar.GET("/", func(c *gin.Context) {
				c.JSON(http.StatusOK, gin.H{
					"message": "Calendar view endpoint",
					"note":    "Use /api/v1/appointments with date filters",
				})
			})
		}
	}

	// Create HTTP server
	srv := &http.Server{
		Addr:           ":" + cfg.Port,
		Handler:        router,
		ReadTimeout:    15 * time.Second,
		WriteTimeout:   15 * time.Second,
		MaxHeaderBytes: 1 << 20, // 1 MB
	}

	// Start server in goroutine
	go func() {
		log.Printf("Starting %s v%s on port %s", cfg.AppName, cfg.AppVersion, cfg.Port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	// Graceful shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server exited")
}
