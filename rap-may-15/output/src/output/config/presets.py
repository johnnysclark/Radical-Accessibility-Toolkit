"""
Preset management for common image types.

Loads and applies predefined conversion settings optimized for
different types of architectural drawings and images.
"""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List


class PresetError(Exception):
    """Custom exception for preset-related errors."""
    pass


class PresetManager:
    """
    Manager for image conversion presets.

    Loads preset configurations and provides access to optimized
    settings for different image types.
    """

    def __init__(self, presets_path: Optional[str] = None):
        """
        Initialize preset manager.

        Args:
            presets_path: Optional path to custom presets.yaml file.
                         If not provided, uses default bundled configuration.
        """
        if presets_path:
            self.presets_path = Path(presets_path)
        else:
            # Default to bundled configuration
            package_dir = Path(__file__).parent.parent
            self.presets_path = package_dir / "data" / "presets.yaml"

        self.presets = self._load_presets()

    def _load_presets(self) -> Dict[str, Any]:
        """
        Load presets from YAML file.

        Returns:
            Presets configuration dictionary

        Raises:
            PresetError: If presets cannot be loaded
        """
        if not self.presets_path.exists():
            raise PresetError(
                f"Presets file not found: {self.presets_path}"
            )

        try:
            with open(self.presets_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if not config or 'presets' not in config:
                raise PresetError("Invalid presets file: missing 'presets' section")

            return config

        except yaml.YAMLError as e:
            raise PresetError(
                f"Failed to parse presets YAML: {str(e)}"
            ) from e
        except Exception as e:
            raise PresetError(
                f"Failed to load presets: {str(e)}"
            ) from e

    def get_preset(self, name: str) -> Dict[str, Any]:
        """
        Get preset settings by name.

        Args:
            name: Preset name (e.g., 'floor_plan', 'sketch')

        Returns:
            Dictionary with preset settings

        Raises:
            PresetError: If preset not found
        """
        presets = self.presets.get('presets', {})

        if name not in presets:
            available = self.list_presets()
            raise PresetError(
                f"Preset '{name}' not found. "
                f"Available presets: {', '.join(available)}"
            )

        return presets[name]

    def get_preset_settings(self, name: str) -> Dict[str, Any]:
        """
        Get just the settings portion of a preset.

        Args:
            name: Preset name

        Returns:
            Settings dictionary

        Raises:
            PresetError: If preset not found
        """
        preset = self.get_preset(name)
        return preset.get('settings', {})

    def list_presets(self) -> List[str]:
        """
        Get list of available preset names.

        Returns:
            List of preset names
        """
        presets = self.presets.get('presets', {})
        return sorted(presets.keys())

    def get_preset_info(self, name: str) -> Dict[str, str]:
        """
        Get descriptive information about a preset.

        Args:
            name: Preset name

        Returns:
            Dictionary with name, description, and notes
        """
        preset = self.get_preset(name)
        return {
            'name': preset.get('name', name),
            'description': preset.get('description', ''),
            'notes': preset.get('notes', '')
        }

    def get_all_presets_info(self) -> Dict[str, Dict[str, str]]:
        """
        Get information about all available presets.

        Returns:
            Dictionary mapping preset names to their info
        """
        info = {}
        for name in self.list_presets():
            info[name] = self.get_preset_info(name)
        return info

    def get_default_preset(self) -> str:
        """
        Get the default preset name.

        Returns:
            Default preset name
        """
        return self.presets.get('default', 'floor_plan')

    def apply_preset(self, name: str, current_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply preset settings to current settings.

        Preset settings override current settings, but current settings
        that are not in the preset are preserved.

        Args:
            name: Preset name
            current_settings: Current settings dictionary

        Returns:
            Merged settings dictionary
        """
        preset_settings = self.get_preset_settings(name)

        # Start with current settings
        merged = current_settings.copy()

        # Override with preset settings
        merged.update(preset_settings)

        return merged

    def format_preset_list(self) -> str:
        """
        Format list of presets for display.

        Returns:
            Formatted string with all presets and descriptions
        """
        lines = ["Available Presets:", ""]

        for name in self.list_presets():
            info = self.get_preset_info(name)
            lines.append(f"  {name}")
            lines.append(f"    {info['description']}")
            lines.append("")

        return "\n".join(lines)

    def get_recommendations(self, image_type: str) -> List[str]:
        """
        Get preset recommendations based on image characteristics.

        Args:
            image_type: Image characteristic ('high_contrast', 'low_contrast', etc.)

        Returns:
            List of recommended preset names
        """
        recommendations = self.presets.get('recommendations', {})
        return recommendations.get(image_type, [])

    def reload(self):
        """
        Reload presets from file.

        Useful if presets file has been modified.
        """
        self.presets = self._load_presets()
