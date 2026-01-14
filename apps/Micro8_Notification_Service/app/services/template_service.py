"""
Template rendering service using Jinja2
KISS principle: Simple template rendering
"""
import logging
from jinja2 import Template, TemplateError
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TemplateService:
    """Simple Jinja2 template rendering"""
    
    @staticmethod
    def render_template(template_body: str, variables: Dict[str, Any]) -> str:
        """
        Render Jinja2 template with variables
        
        Args:
            template_body: Template string with {{variable}} placeholders
            variables: Dictionary of variables to replace
        
        Returns:
            str: Rendered template
        
        Raises:
            TemplateError: If template rendering fails
        """
        try:
            template = Template(template_body)
            rendered = template.render(**variables)
            return rendered
        except TemplateError as e:
            logger.error(f"Template rendering failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error rendering template: {e}")
            raise
    
    @staticmethod
    def validate_variables(
        required_variables: list,
        provided_variables: Dict[str, Any]
    ) -> bool:
        """
        Validate that all required variables are provided
        
        Args:
            required_variables: List of required variable names
            provided_variables: Dictionary of provided variables
        
        Returns:
            bool: True if all required variables are present
        """
        missing = set(required_variables) - set(provided_variables.keys())
        if missing:
            logger.warning(f"Missing template variables: {missing}")
            return False
        return True


# Global instance
template_service = TemplateService()
