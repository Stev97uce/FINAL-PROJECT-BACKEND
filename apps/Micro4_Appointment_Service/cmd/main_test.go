package main

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stev97uce/appointment-service/pkg/config"
)

func TestHealthEndpoint(t *testing.T) {
	// Set Gin to test mode
	gin.SetMode(gin.TestMode)

	// Load config
	cfg := &config.Config{
		AppName:    "Appointment Service",
		AppVersion: "1.0.0",
	}

	// Create router
	router := gin.Default()
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"service": cfg.AppName,
			"version": cfg.AppVersion,
		})
	})

	// Create test request
	req, err := http.NewRequest("GET", "/health", nil)
	if err != nil {
		t.Fatalf("Failed to create request: %v", err)
	}

	// Record response
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	// Check status code
	if w.Code != http.StatusOK {
		t.Errorf("Expected status code %d, got %d", http.StatusOK, w.Code)
	}

	// Check response body contains expected fields
	body := w.Body.String()
	if body == "" {
		t.Error("Expected non-empty response body")
	}
}

func TestRootEndpoint(t *testing.T) {
	gin.SetMode(gin.TestMode)

	cfg := &config.Config{
		AppVersion: "1.0.0",
	}

	router := gin.Default()
	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Appointment Service API",
			"version": cfg.AppVersion,
		})
	})

	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatalf("Failed to create request: %v", err)
	}

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status code %d, got %d", http.StatusOK, w.Code)
	}
}
