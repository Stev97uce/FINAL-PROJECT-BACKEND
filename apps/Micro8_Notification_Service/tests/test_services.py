"""
Test services
"""
import pytest
from app.services.template_service import TemplateService


def test_template_rendering():
    """Test Jinja2 template rendering"""
    template_body = "Hello {{name}}, your appointment is on {{date}}"
    variables = {
        "name": "John Doe",
        "date": "2024-01-15"
    }
    
    rendered = TemplateService.render_template(template_body, variables)
    
    assert "Hello John Doe" in rendered
    assert "2024-01-15" in rendered


def test_template_validate_variables():
    """Test variable validation"""
    required = ["name", "email", "date"]
    provided = {"name": "John", "email": "john@example.com", "date": "2024-01-15"}
    
    result = TemplateService.validate_variables(required, provided)
    assert result == True


def test_template_validate_variables_missing():
    """Test variable validation with missing variables"""
    required = ["name", "email", "date"]
    provided = {"name": "John"}  # Missing email and date
    
    result = TemplateService.validate_variables(required, provided)
    assert result == False
