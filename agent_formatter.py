from dataclasses import dataclass
from typing import Any, List
import re

@dataclass
class AgentFormatter:
    """Formatter for Agent outputs to improve readability"""
    
    @staticmethod
    def format_action(text: str) -> str:
        """Format individual action text with proper emoji and styling"""
        # Common action patterns and their emojis
        action_patterns = {
            r'search.*google': '🔍 ',
            r'clicked?.*index': '🖱️ ',
            r'extract.*content': '📄 ',
            r'task.*completed': '✅ ',
            r'error': '❌ ',
            r'warning': '⚠️ '
        }
        
        formatted = text
        for pattern, emoji in action_patterns.items():
            if re.search(pattern, text.lower()):
                if not any(e in text for e in ['🔍', '🖱️', '📄', '✅', '❌', '⚠️']):
                    formatted = f"{emoji}{text}"
                break
                
        return formatted

    @staticmethod
    def format_message(text: str) -> str:
        """Format the complete message with proper styling"""
        # If it's JSON-like or technical content, return as is
        if text.strip().startswith('{') or text.strip().startswith('['):
            return text
            
        # Add line breaks for readability
        formatted = text.replace('. ', '.\n')
        
        # Format lists
        if '\n' in formatted:
            lines = formatted.split('\n')
            formatted_lines = []
            for line in lines:
                if line.strip():
                    # Add bullets to lines that don't start with emojis or special characters
                    if not any(line.strip().startswith(c) for c in ['•', '-', '*', '🔍', '🖱️', '📄', '✅', '❌', '⚠️']):
                        formatted_lines.append(f"• {line}")
                    else:
                        formatted_lines.append(line)
            formatted = '\n'.join(formatted_lines)
            
        return formatted

    @staticmethod
    def format_results(results: List[Any]) -> str:
        """Format a list of results with proper styling"""
        formatted_results = []
        
        for result in results:
            if hasattr(result, 'extracted_content') and result.extracted_content:
                content = result.extracted_content
                # Format the content
                formatted_content = AgentFormatter.format_action(content)
                # Add to results if not a duplicate
                if formatted_content not in formatted_results:
                    formatted_results.append(formatted_content)
            
            if hasattr(result, 'error') and result.error:
                error = f"❌ Error: {result.error}"
                if error not in formatted_results:
                    formatted_results.append(error)
        
        return '\n'.join(formatted_results)

    @staticmethod
    def format_final_output(output: Any) -> str:
        """Format the final output with all components"""
        if not output:
            return "No results available"
            
        # Handle raw string output
        if isinstance(output, str):
            return AgentFormatter.format_message(output)
            
        # Handle agent history output
        if hasattr(output, 'all_results'):
            formatted = "🎯 Results:\n\n"
            formatted += AgentFormatter.format_results(output.all_results)
            return formatted
            
        return str(output)